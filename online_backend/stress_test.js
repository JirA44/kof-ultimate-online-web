/**
 * KOF Ultimate Online - Stress Test
 * 20 authenticated virtual players, full matchmaking and match-result cycle.
 * Run only against an isolated local/test deployment.
 */
const fetch = require('node-fetch');
const WebSocket = require('ws');

const API_URL = process.env.API_URL || 'http://localhost:3100';
const WS_URL = process.env.MATCHMAKING_URL || 'ws://localhost:3101';
const HEALTH_URL = process.env.MATCHMAKING_HEALTH_URL || 'http://localhost:3101/health';
const PLAYER_COUNT = Number(process.env.TEST_PLAYERS || 20);
const TEST_DURATION_MS = Number(process.env.TEST_DURATION_MS || 90000);
const RUN_ID = Math.random().toString(36).slice(2, 8);

const players = Array.from({ length: PLAYER_COUNT }, (_, i) => ({
  username: `Load_${String(i + 1).padStart(2, '0')}_${RUN_ID}`,
  password: `Test-${RUN_ID}-${i}-not-a-real-user`,
  email: `load-${i}-${RUN_ID}@example.invalid`
}));

const stats = {
  registered: 0, connected: 0, matchesFound: 0, matchesAccepted: 0,
  gamesStarted: 0, gamesFinished: 0, errors: [], latenciesMs: [],
  serverMemoryMb: [], serverCpuPercent: []
};
const connections = [];
const playerStates = new Map();
let stopping = false;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function registerPlayer(player) {
  try {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: player.username, email: player.email, password: player.password })
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`register HTTP ${response.status}: ${body.slice(0, 200)}`);
    }
    const data = await response.json();
    if (!data.token || data.player?.id === undefined) throw new Error('API registration response omitted token/player id');
    return { token: data.token, playerId: String(data.player.id) };
  } catch (err) {
    stats.errors.push(`Register ${player.username}: ${err.message}`);
    return null;
  }
}

function connectPlayer(player, credentials) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL);
    const state = { status: 'connecting', wins: 0, losses: 0 };
    playerStates.set(player.username, state);
    connections.push(ws);
    let currentMatchId = null;
    let opponentId = null;
    let pingStartedAt = null;
    let settled = false;

    const registerTimeout = setTimeout(() => {
      if (!settled) { settled = true; reject(new Error(`register timeout: ${player.username}`)); }
    }, 10000);

    ws.on('open', () => {
      stats.connected++;
      state.status = 'connected';
      ws.send(JSON.stringify({
        type: 'register',
        playerId: credentials.playerId,
        token: credentials.token
      }));
      setInterval(() => {
        if (ws.readyState === WebSocket.OPEN && !stopping) {
          pingStartedAt = Date.now();
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 2000).unref?.();
    });

    ws.on('message', raw => {
      let msg;
      try { msg = JSON.parse(raw); }
      catch (err) { stats.errors.push(`Invalid JSON from server: ${err.message}`); return; }

      switch (msg.type) {
        case 'registered':
          state.status = 'searching';
          if (!settled) { settled = true; clearTimeout(registerTimeout); resolve(ws); }
          ws.send(JSON.stringify({ type: 'join_matchmaking', playerId: credentials.playerId, mode: 'ranked' }));
          break;
        case 'searching':
          state.status = 'searching';
          break;
        case 'match_found':
          stats.matchesFound++;
          currentMatchId = msg.matchId;
          opponentId = String(msg.opponent?.id || '');
          state.status = 'matched';
          if (!opponentId) stats.errors.push(`Missing opponent id for ${player.username}`);
          setTimeout(() => {
            if (ws.readyState === WebSocket.OPEN && currentMatchId) {
              ws.send(JSON.stringify({ type: 'accept_match', playerId: credentials.playerId, matchId: currentMatchId }));
              stats.matchesAccepted++;
            }
          }, 100 + Math.random() * 150);
          break;
        case 'match_start':
          stats.gamesStarted++;
          state.status = 'playing';
          if (msg.isPlayer1) {
            if (!opponentId || !currentMatchId) { stats.errors.push(`Incomplete match state for ${player.username}`); break; }
            setTimeout(() => {
              if (ws.readyState !== WebSocket.OPEN) return;
              const winnerId = Math.random() < 0.5 ? credentials.playerId : opponentId;
              const loserId = winnerId === credentials.playerId ? opponentId : credentials.playerId;
              ws.send(JSON.stringify({
                type: 'match_result', matchId: currentMatchId, winnerId, loserId, duration: 3
              }));
            }, 1000 + Math.random() * 1000);
          }
          break;
        case 'match_complete':
          stats.gamesFinished++;
          if (msg.result === 'victory') state.wins++;
          else if (msg.result === 'defeat') state.losses++;
          state.status = 'finished';
          currentMatchId = null;
          opponentId = null;
          setTimeout(() => {
            if (ws.readyState === WebSocket.OPEN && !stopping) {
              state.status = 'searching';
              ws.send(JSON.stringify({ type: 'join_matchmaking', playerId: credentials.playerId, mode: 'ranked' }));
            }
          }, 300);
          break;
        case 'pong':
          if (pingStartedAt !== null) {
            stats.latenciesMs.push(Date.now() - pingStartedAt);
            pingStartedAt = null;
          }
          break;
        case 'error':
          stats.errors.push(`Server ${player.username}: ${msg.message}`);
          break;
      }
    });

    ws.on('error', err => {
      stats.errors.push(`WebSocket ${player.username}: ${err.message}`);
      if (!settled) { settled = true; clearTimeout(registerTimeout); reject(err); }
    });
    ws.on('close', () => {
      if (!stopping && state.status !== 'finished') stats.errors.push(`Unexpected disconnect: ${player.username}`);
    });
  });
}

async function sampleServerHealth() {
  try {
    const response = await fetch(HEALTH_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (Number.isFinite(data.memory_rss_mb)) stats.serverMemoryMb.push(data.memory_rss_mb);
    if (Number.isFinite(data.cpu_percent_since_last_sample)) stats.serverCpuPercent.push(data.cpu_percent_since_last_sample);
  } catch (err) {
    stats.errors.push(`Health sample: ${err.message}`);
  }
}

function percentile(values, p) {
  const sorted = values.slice().sort((a, b) => a - b);
  return sorted.length ? sorted[Math.min(sorted.length - 1, Math.ceil(p * sorted.length) - 1)] : 'n/a';
}

async function runTest() {
  console.log(`KOF multiplayer test: ${PLAYER_COUNT} virtual players, ${Math.round(TEST_DURATION_MS / 1000)}s, run ${RUN_ID}`);
  try {
    const health = await fetch(`${API_URL}/api/health`);
    if (!health.ok) throw new Error(`API health HTTP ${health.status}`);
    await sampleServerHealth();
  } catch (err) {
    console.error(`Preflight failed: ${err.message}`);
    process.exit(1);
  }

  const credentials = {};
  for (const player of players) {
    credentials[player.username] = await registerPlayer(player);
  }
  stats.registered = Object.values(credentials).filter(Boolean).length;

  for (const player of players) {
    const auth = credentials[player.username];
    if (!auth) continue;
    try { await connectPlayer(player, auth); }
    catch (err) { stats.errors.push(`Connect ${player.username}: ${err.message}`); }
    await delay(25);
  }

  const startedAt = Date.now();
  while (Date.now() - startedAt < TEST_DURATION_MS) {
    await Promise.all([sampleServerHealth(), delay(5000)]);
    console.log(`[${Math.floor((Date.now() - startedAt) / 1000)}s] connected=${stats.connected} matches=${stats.matchesFound} starts=${stats.gamesStarted} completed=${stats.gamesFinished} errors=${stats.errors.length}`);
  }

  stopping = true;
  connections.forEach(ws => { try { ws.close(); } catch (_) {} });
  await delay(250);

  const success = stats.registered === PLAYER_COUNT &&
    stats.connected === PLAYER_COUNT &&
    stats.matchesFound >= 2 &&
    stats.gamesStarted >= 2 &&
    stats.gamesFinished >= 2 &&
    stats.errors.length === 0;

  console.log('\nRESULTS');
  console.log(`Registered/connected: ${stats.registered}/${stats.connected} of ${PLAYER_COUNT}`);
  console.log(`Match-found events: ${stats.matchesFound}; starts: ${stats.gamesStarted}; completion notifications: ${stats.gamesFinished}`);
  console.log(`Errors: ${stats.errors.length}`);
  console.log(`Ping p50/p95: ${percentile(stats.latenciesMs, 0.50)} / ${percentile(stats.latenciesMs, 0.95)} ms`);
  console.log(`Server RSS max: ${stats.serverMemoryMb.length ? Math.max(...stats.serverMemoryMb).toFixed(1) : 'n/a'} MB`);
  console.log(`Server CPU sample max: ${stats.serverCpuPercent.length ? Math.max(...stats.serverCpuPercent).toFixed(1) : 'n/a'}%`);
  if (stats.errors.length) console.log('First errors:', stats.errors.slice(0, 10));
  console.log(success ? 'STRESS TEST PASSED' : 'STRESS TEST FAILED');
  process.exit(success ? 0 : 1);
}

runTest().catch(err => {
  console.error(err);
  process.exit(1);
});
