/**
 * KOF Ultimate Online - Automatic Multiplayer Test
 * Simulates 6 players finding matches
 */

const fetch = require('node-fetch');
const WebSocket = require('ws');

const API_URL = 'http://localhost:3100';
const WS_URL = 'ws://localhost:3101';

const PLAYERS = [
    { username: 'TestPlayer1', elo: 1000 },
    { username: 'TestPlayer2', elo: 1050 },
    { username: 'TestPlayer3', elo: 950 },
    { username: 'TestPlayer4', elo: 1100 },
    { username: 'TestPlayer5', elo: 900 },
    { username: 'TestPlayer6', elo: 1000 }
];

let stats = {
    registered: 0,
    connected: 0,
    matchesFound: 0,
    errors: []
};

async function registerPlayer(player) {
    try {
        const res = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: player.username,
                password: 'test123',
                email: `${player.username.toLowerCase()}@test.com`
            })
        });

        if (res.ok || res.status === 409) { // 409 = already exists
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
                console.log(`[OK] ${player.username} logged in`);
                return data.token;
            }
        }

        console.log(`[WARN] ${player.username} registration/login issue`);
        return null;
    } catch (err) {
        stats.errors.push(`${player.username}: ${err.message}`);
        console.log(`[ERR] ${player.username}: ${err.message}`);
        return null;
    }
}

function connectToMatchmaking(player, token) {
    return new Promise((resolve) => {
        try {
            const ws = new WebSocket(WS_URL);

            ws.on('open', () => {
                stats.connected++;
                console.log(`[WS] ${player.username} connected to matchmaking`);

                // Register in matchmaking
                ws.send(JSON.stringify({
                    type: 'register',
                    playerId: player.username,
                    token: token
                }));

                // Start searching for match
                setTimeout(() => {
                    ws.send(JSON.stringify({
                        type: 'find_match',
                        mode: 'ranked'
                    }));
                    console.log(`[SEARCH] ${player.username} searching for match...`);
                }, 500);
            });

            ws.on('message', (data) => {
                try {
                    const msg = JSON.parse(data);
                    if (msg.type === 'match_found') {
                        stats.matchesFound++;
                        console.log(`[MATCH] ${player.username} found match with ${msg.opponent}`);
                    } else if (msg.type === 'registered') {
                        console.log(`[OK] ${player.username} registered in queue`);
                    }
                } catch (e) {}
            });

            ws.on('error', (err) => {
                stats.errors.push(`WS ${player.username}: ${err.message}`);
            });

            ws.on('close', () => {
                console.log(`[CLOSE] ${player.username} disconnected`);
            });

            setTimeout(() => {
                ws.close();
                resolve();
            }, 30000); // 30 second test

        } catch (err) {
            stats.errors.push(`WS ${player.username}: ${err.message}`);
            resolve();
        }
    });
}

async function runTest() {
    console.log('='.repeat(60));
    console.log('KOF ULTIMATE ONLINE - MULTIPLAYER SIMULATION TEST');
    console.log('='.repeat(60));
    console.log(`Testing with ${PLAYERS.length} simulated players\n`);

    // Check API health
    try {
        const health = await fetch(`${API_URL}/api/health`);
        if (!health.ok) throw new Error('API not responding');
        console.log('[OK] API Server is online\n');
    } catch (err) {
        console.log('[ERR] API Server is offline!');
        process.exit(1);
    }

    // Register all players
    console.log('--- REGISTERING PLAYERS ---');
    const tokens = {};
    for (const player of PLAYERS) {
        tokens[player.username] = await registerPlayer(player);
        await new Promise(r => setTimeout(r, 200)); // Small delay
    }

    // Connect to matchmaking
    console.log('\n--- CONNECTING TO MATCHMAKING ---');
    const promises = PLAYERS.map(player =>
        tokens[player.username] ? connectToMatchmaking(player, tokens[player.username]) : Promise.resolve()
    );

    // Wait for all connections
    await Promise.all(promises);

    // Print results
    console.log('\n' + '='.repeat(60));
    console.log('RESULTS');
    console.log('='.repeat(60));
    console.log(`Players registered: ${stats.registered}/${PLAYERS.length}`);
    console.log(`WebSocket connections: ${stats.connected}/${PLAYERS.length}`);
    console.log(`Matches found: ${stats.matchesFound}`);
    console.log(`Errors: ${stats.errors.length}`);

    if (stats.errors.length > 0) {
        console.log('\nErrors:');
        stats.errors.forEach(e => console.log(`  - ${e}`));
    }

    const success = stats.registered > 0 && stats.connected > 0;
    console.log(`\n${success ? '[OK] Test PASSED' : '[FAIL] Test FAILED'}`);
    console.log('='.repeat(60));

    process.exit(success ? 0 : 1);
}

runTest();
