/**
 * KOF Ultimate Online - Stress Test
 * 20 players, full match cycle with results
 */

const fetch = require('node-fetch');
const WebSocket = require('ws');

const API_URL = 'http://localhost:3100';
const WS_URL = 'ws://localhost:3101';

// 20 players with varied ELO
const PLAYERS = [];
for (let i = 1; i <= 20; i++) {
    PLAYERS.push({
        username: `Player_${String(i).padStart(2, '0')}`,
        elo: 800 + Math.floor(Math.random() * 400) // 800-1200
    });
}

let stats = {
    registered: 0,
    connected: 0,
    matchesFound: 0,
    matchesAccepted: 0,
    gamesStarted: 0,
    gamesFinished: 0,
    errors: []
};

let connections = [];
let playerStates = new Map();

async function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function registerPlayer(player) {
    try {
        await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: player.username,
                password: 'test123',
                email: `${player.username.toLowerCase()}@test.com`
            })
        });

        const loginRes = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: player.username, password: 'test123' })
        });

        if (loginRes.ok) {
            const data = await loginRes.json();
            stats.registered++;
            return data.token;
        }
        return null;
    } catch (err) {
        stats.errors.push(`Reg ${player.username}: ${err.message}`);
        return null;
    }
}

function connectPlayer(player, token) {
    return new Promise((resolve) => {
        const ws = new WebSocket(WS_URL);
        let resolved = false;
        let currentMatchId = null;

        playerStates.set(player.username, { status: 'connecting', wins: 0, losses: 0 });

        ws.on('open', () => {
            stats.connected++;
            playerStates.set(player.username, { ...playerStates.get(player.username), status: 'connected' });

            ws.send(JSON.stringify({
                type: 'register',
                playerId: player.username,
                token: token,
                elo: player.elo
            }));
        });

        ws.on('message', (data) => {
            try {
                const msg = JSON.parse(data);

                switch(msg.type) {
                    case 'registered':
                        playerStates.set(player.username, { ...playerStates.get(player.username), status: 'registered' });
                        // Join queue
                        ws.send(JSON.stringify({
                            type: 'join_matchmaking',
                            playerId: player.username,
                            mode: 'ranked',
                            elo: player.elo
                        }));
                        break;

                    case 'searching':
                        playerStates.set(player.username, { ...playerStates.get(player.username), status: 'searching' });
                        break;

                    case 'match_found':
                        stats.matchesFound++;
                        currentMatchId = msg.matchId;
                        const opponent = msg.opponent?.playerId || msg.opponent?.username || msg.player2?.playerId || 'Unknown';
                        console.log(`[MATCH] ${player.username} vs ${opponent}`);
                        playerStates.set(player.username, { ...playerStates.get(player.username), status: 'matched' });

                        // Accept match
                        setTimeout(() => {
                            ws.send(JSON.stringify({
                                type: 'accept_match',
                                matchId: currentMatchId,
                                playerId: player.username
                            }));
                            stats.matchesAccepted++;
                        }, 100 + Math.random() * 200);
                        break;

                    case 'match_start':
                    case 'game_start':
                        stats.gamesStarted++;
                        console.log(`[GAME] ${player.username} game started!`);
                        playerStates.set(player.username, { ...playerStates.get(player.username), status: 'playing' });

                        // Simulate game (2-5 seconds)
                        setTimeout(() => {
                            const won = Math.random() > 0.5;
                            ws.send(JSON.stringify({
                                type: 'match_result',
                                matchId: currentMatchId,
                                playerId: player.username,
                                result: won ? 'win' : 'loss'
                            }));

                            const state = playerStates.get(player.username);
                            if (won) state.wins++;
                            else state.losses++;
                            state.status = 'finished';
                            playerStates.set(player.username, state);

                            stats.gamesFinished++;
                            console.log(`[END] ${player.username} ${won ? 'WON' : 'LOST'}`);
                        }, 2000 + Math.random() * 3000);
                        break;

                    case 'match_end':
                    case 'game_end':
                        // Re-queue after game
                        setTimeout(() => {
                            playerStates.set(player.username, { ...playerStates.get(player.username), status: 'requeuing' });
                            ws.send(JSON.stringify({
                                type: 'join_matchmaking',
                                playerId: player.username,
                                mode: 'ranked',
                                elo: player.elo
                            }));
                        }, 500);
                        break;

                    case 'error':
                        console.log(`[ERR] ${player.username}: ${msg.message}`);
                        break;
                }
            } catch (e) {}
        });

        ws.on('error', (err) => {
            stats.errors.push(`WS ${player.username}: ${err.message}`);
        });

        connections.push(ws);

        setTimeout(() => {
            if (!resolved) {
                resolved = true;
                resolve(ws);
            }
        }, 1000);
    });
}

function printStatus() {
    let searching = 0, matched = 0, playing = 0, finished = 0;
    playerStates.forEach(state => {
        if (state.status === 'searching') searching++;
        else if (state.status === 'matched') matched++;
        else if (state.status === 'playing') playing++;
        else if (state.status === 'finished') finished++;
    });
    return `Search:${searching} Match:${matched} Play:${playing} Done:${finished}`;
}

async function runTest() {
    console.log('='.repeat(60));
    console.log('  KOF ULTIMATE ONLINE - STRESS TEST');
    console.log('='.repeat(60));
    console.log(`  ${PLAYERS.length} players | 90 second test\n`);

    // Check API
    try {
        const health = await fetch(`${API_URL}/api/health`);
        if (!health.ok) throw new Error();
        console.log('[OK] API Server online\n');
    } catch {
        console.log('[ERR] API Server offline!');
        process.exit(1);
    }

    // Register
    console.log('--- REGISTRATION ---');
    const tokens = {};
    for (const player of PLAYERS) {
        tokens[player.username] = await registerPlayer(player);
    }
    console.log(`Registered: ${stats.registered}/${PLAYERS.length}\n`);

    // Connect
    console.log('--- CONNECTING ---');
    for (const player of PLAYERS) {
        if (tokens[player.username]) {
            await connectPlayer(player, tokens[player.username]);
            await delay(50);
        }
    }
    console.log(`Connected: ${stats.connected}/${PLAYERS.length}\n`);

    // Run test
    console.log('--- MATCHMAKING & GAMES ---');
    const startTime = Date.now();
    const testDuration = 90000; // 90 seconds

    while (Date.now() - startTime < testDuration) {
        await delay(5000);
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        console.log(`[${elapsed}s] Found:${stats.matchesFound} Started:${stats.gamesStarted} Finished:${stats.gamesFinished} | ${printStatus()}`);
    }

    // Cleanup
    console.log('\n--- CLEANUP ---');
    connections.forEach(ws => { try { ws.close(); } catch {} });

    // Final stats
    console.log('\n' + '='.repeat(60));
    console.log('  STRESS TEST RESULTS');
    console.log('='.repeat(60));
    console.log(`  Players:          ${stats.registered}/${PLAYERS.length} registered`);
    console.log(`  Connections:      ${stats.connected}/${PLAYERS.length} websocket`);
    console.log(`  Matches Found:    ${stats.matchesFound}`);
    console.log(`  Matches Accepted: ${stats.matchesAccepted}`);
    console.log(`  Games Started:    ${stats.gamesStarted}`);
    console.log(`  Games Finished:   ${stats.gamesFinished}`);
    console.log(`  Errors:           ${stats.errors.length}`);

    // Player stats
    console.log('\n  TOP PLAYERS:');
    const sorted = [...playerStates.entries()]
        .sort((a, b) => b[1].wins - a[1].wins)
        .slice(0, 5);
    sorted.forEach(([name, state], i) => {
        console.log(`    ${i+1}. ${name}: ${state.wins}W/${state.losses}L`);
    });

    const success = stats.matchesFound > 0;
    console.log(`\n  ${success ? 'STRESS TEST PASSED' : 'STRESS TEST FAILED'}`);
    console.log('='.repeat(60));

    process.exit(0);
}

runTest();
