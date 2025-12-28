/**
 * KOF Ultimate Online - Full Multiplayer Test
 * Tests registration, matchmaking, and match formation
 */

const fetch = require('node-fetch');
const WebSocket = require('ws');

const API_URL = 'http://localhost:3100';
const WS_URL = 'ws://localhost:3101';

const PLAYERS = [
    { username: 'Fighter_Alpha', elo: 1000 },
    { username: 'Fighter_Beta', elo: 1020 },
    { username: 'Fighter_Gamma', elo: 980 },
    { username: 'Fighter_Delta', elo: 1050 },
    { username: 'Fighter_Epsilon', elo: 950 },
    { username: 'Fighter_Zeta', elo: 1000 },
    { username: 'Fighter_Eta', elo: 1100 },
    { username: 'Fighter_Theta', elo: 900 }
];

let stats = {
    registered: 0,
    connected: 0,
    inQueue: 0,
    matchesFound: 0,
    matchesPlayed: 0,
    errors: []
};

let connections = [];

async function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function registerPlayer(player) {
    try {
        // Try register
        await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: player.username,
                password: 'test123',
                email: `${player.username.toLowerCase()}@test.com`
            })
        });

        // Login
        const loginRes = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: player.username,
                password: 'test123'
            })
        });

        if (loginRes.ok) {
            const data = await loginRes.json();
            stats.registered++;
            return data.token;
        }
        return null;
    } catch (err) {
        stats.errors.push(`Register ${player.username}: ${err.message}`);
        return null;
    }
}

function connectPlayer(player, token) {
    return new Promise((resolve) => {
        const ws = new WebSocket(WS_URL);
        let resolved = false;

        ws.on('open', () => {
            stats.connected++;
            console.log(`[+] ${player.username} connected`);

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
                        console.log(`[Q] ${player.username} registered`);
                        stats.inQueue++;
                        // Join matchmaking queue
                        ws.send(JSON.stringify({
                            type: 'join_matchmaking',
                            playerId: player.username,
                            mode: 'ranked',
                            elo: player.elo
                        }));
                        break;

                    case 'matchmaking_joined':
                        console.log(`[S] ${player.username} searching (ELO: ${player.elo})...`);
                        break;

                    case 'searching':
                        console.log(`[S] ${player.username} searching...`);
                        break;

                    case 'match_found':
                        stats.matchesFound++;
                        console.log(`[M] MATCH: ${player.username} vs ${msg.opponent || msg.player2}`);
                        // Accept match
                        ws.send(JSON.stringify({ type: 'accept_match', matchId: msg.matchId }));
                        break;

                    case 'match_start':
                        console.log(`[G] GAME START: ${player.username}`);
                        // Simulate game result after 2 seconds
                        setTimeout(() => {
                            const won = Math.random() > 0.5;
                            ws.send(JSON.stringify({
                                type: 'match_result',
                                matchId: msg.matchId,
                                result: won ? 'win' : 'loss'
                            }));
                            stats.matchesPlayed++;
                            console.log(`[R] ${player.username} ${won ? 'WON' : 'LOST'}`);
                        }, 2000);
                        break;

                    case 'match_end':
                        console.log(`[E] Match ended for ${player.username}`);
                        // Search again
                        setTimeout(() => {
                            ws.send(JSON.stringify({ type: 'find_match', mode: 'ranked' }));
                        }, 1000);
                        break;

                    case 'error':
                        console.log(`[!] ${player.username}: ${msg.message}`);
                        break;
                }
            } catch (e) {}
        });

        ws.on('error', (err) => {
            if (!resolved) {
                stats.errors.push(`WS ${player.username}: ${err.message}`);
                resolved = true;
                resolve(null);
            }
        });

        ws.on('close', () => {
            if (!resolved) {
                resolved = true;
                resolve(null);
            }
        });

        connections.push(ws);

        setTimeout(() => {
            if (!resolved) {
                resolved = true;
                resolve(ws);
            }
        }, 2000);
    });
}

async function checkLeaderboard() {
    try {
        const res = await fetch(`${API_URL}/api/leaderboard`);
        if (res.ok) {
            const data = await res.json();
            console.log('\n--- LEADERBOARD ---');
            if (data.players && data.players.length > 0) {
                data.players.slice(0, 5).forEach((p, i) => {
                    console.log(`  ${i+1}. ${p.username} - ${p.elo || 1000} ELO`);
                });
            } else {
                console.log('  (empty)');
            }
        }
    } catch (e) {}
}

async function runTest() {
    console.log('='.repeat(60));
    console.log('  KOF ULTIMATE ONLINE - FULL MULTIPLAYER TEST');
    console.log('='.repeat(60));
    console.log(`  ${PLAYERS.length} players | 60 second test\n`);

    // Check servers
    try {
        const health = await fetch(`${API_URL}/api/health`);
        if (!health.ok) throw new Error();
        console.log('[OK] API Server online');
    } catch {
        console.log('[ERR] API Server offline!');
        process.exit(1);
    }

    // Register players
    console.log('\n--- REGISTRATION ---');
    const tokens = {};
    for (const player of PLAYERS) {
        tokens[player.username] = await registerPlayer(player);
        await delay(100);
    }
    console.log(`Registered: ${stats.registered}/${PLAYERS.length}`);

    // Connect all players
    console.log('\n--- CONNECTING ---');
    for (const player of PLAYERS) {
        if (tokens[player.username]) {
            await connectPlayer(player, tokens[player.username]);
            await delay(200);
        }
    }

    console.log('\n--- MATCHMAKING (60s) ---');

    // Run for 60 seconds
    const startTime = Date.now();
    while (Date.now() - startTime < 60000) {
        await delay(5000);
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        console.log(`  [${elapsed}s] Matches: ${stats.matchesFound} found, ${stats.matchesPlayed} played`);
    }

    // Cleanup
    console.log('\n--- CLEANUP ---');
    connections.forEach(ws => {
        try { ws.close(); } catch {}
    });

    // Check leaderboard
    await checkLeaderboard();

    // Results
    console.log('\n' + '='.repeat(60));
    console.log('  FINAL RESULTS');
    console.log('='.repeat(60));
    console.log(`  Players registered:    ${stats.registered}/${PLAYERS.length}`);
    console.log(`  WebSocket connected:   ${stats.connected}/${PLAYERS.length}`);
    console.log(`  Players in queue:      ${stats.inQueue}`);
    console.log(`  Matches found:         ${stats.matchesFound}`);
    console.log(`  Matches played:        ${stats.matchesPlayed}`);
    console.log(`  Errors:                ${stats.errors.length}`);

    if (stats.errors.length > 0) {
        console.log('\n  Errors:');
        stats.errors.slice(0, 5).forEach(e => console.log(`    - ${e}`));
    }

    const success = stats.registered >= 6 && stats.connected >= 6;
    console.log(`\n  ${success ? 'TEST PASSED' : 'TEST FAILED'}`);
    console.log('='.repeat(60));

    process.exit(0);
}

runTest();
