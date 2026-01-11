/**
 * Test de matchmaking avec 2 joueurs
 */
const WebSocket = require('ws');

console.log('🎮 Test de matchmaking avec 2 joueurs...\n');

// Player 1
const ws1 = new WebSocket('ws://localhost:3101');
let player1Registered = false;

// Player 2
const ws2 = new WebSocket('ws://localhost:3101');
let player2Registered = false;

let matchFound = false;

ws1.on('open', () => {
    console.log('👤 Player1: Connecté');
    ws1.send(JSON.stringify({
        type: 'register',
        playerId: 'player1',
        username: 'Fighter_Ken',
        elo: 1500
    }));
});

ws1.on('message', (data) => {
    const msg = JSON.parse(data);
    console.log('👤 Player1 reçoit:', msg.type);

    if (msg.type === 'registered') {
        player1Registered = true;
        tryStartMatchmaking();
    }

    if (msg.type === 'match_found') {
        console.log('\n🎯 Player1: MATCH TROUVÉ!');
        console.log('   Adversaire:', msg.opponent.username);
        console.log('   ELO:', msg.opponent.elo);
        matchFound = true;
        checkComplete();
    }
});

ws2.on('open', () => {
    console.log('👤 Player2: Connecté');
    ws2.send(JSON.stringify({
        type: 'register',
        playerId: 'player2',
        username: 'Fighter_Ryu',
        elo: 1480
    }));
});

ws2.on('message', (data) => {
    const msg = JSON.parse(data);
    console.log('👤 Player2 reçoit:', msg.type);

    if (msg.type === 'registered') {
        player2Registered = true;
        tryStartMatchmaking();
    }

    if (msg.type === 'match_found') {
        console.log('\n🎯 Player2: MATCH TROUVÉ!');
        console.log('   Adversaire:', msg.opponent.username);
        console.log('   ELO:', msg.opponent.elo);
        matchFound = true;
        checkComplete();
    }
});

function tryStartMatchmaking() {
    if (player1Registered && player2Registered) {
        console.log('\n📝 Les deux joueurs recherchent un match...');

        // Player 1 joins queue
        ws1.send(JSON.stringify({
            type: 'join_matchmaking',
            playerId: 'player1',
            elo: 1500,
            mode: 'quick'
        }));

        // Player 2 joins queue after 500ms
        setTimeout(() => {
            ws2.send(JSON.stringify({
                type: 'join_matchmaking',
                playerId: 'player2',
                elo: 1480,
                mode: 'quick'
            }));
        }, 500);
    }
}

function checkComplete() {
    setTimeout(() => {
        if (matchFound) {
            console.log('\n════════════════════════════════════════════');
            console.log('   ✅ MATCHMAKING FONCTIONNE PARFAITEMENT!');
            console.log('════════════════════════════════════════════\n');
            console.log('   Fighter_Ken (1500) VS Fighter_Ryu (1480)');
            console.log('\n');
        }
        ws1.close();
        ws2.close();
        process.exit(0);
    }, 1000);
}

ws1.on('error', (err) => console.error('Player1 error:', err.message));
ws2.on('error', (err) => console.error('Player2 error:', err.message));

// Timeout
setTimeout(() => {
    console.error('❌ Timeout');
    process.exit(1);
}, 15000);
