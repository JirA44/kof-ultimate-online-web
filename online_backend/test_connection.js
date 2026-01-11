/**
 * Test de connexion au serveur matchmaking
 */
const WebSocket = require('ws');

console.log('🧪 Test de connexion au serveur matchmaking...\n');

const ws = new WebSocket('ws://localhost:3101');

ws.on('open', () => {
    console.log('✅ Connexion WebSocket établie!\n');

    // Test 1: Register
    console.log('📝 Test 1: Enregistrement du joueur...');
    ws.send(JSON.stringify({
        type: 'register',
        playerId: 'test_player_1',
        username: 'TestPlayer',
        elo: 1500
    }));
});

ws.on('message', (data) => {
    const msg = JSON.parse(data);
    console.log('📨 Réponse:', msg.type, JSON.stringify(msg, null, 2));

    if (msg.type === 'registered') {
        console.log('\n✅ Enregistrement réussi!');

        // Test 2: Join matchmaking
        console.log('\n📝 Test 2: Rejoindre la file matchmaking...');
        ws.send(JSON.stringify({
            type: 'join_matchmaking',
            playerId: 'test_player_1',
            elo: 1500,
            mode: 'quick'
        }));
    }

    if (msg.type === 'searching') {
        console.log('\n✅ En file d\'attente! Position:', msg.queuePosition);

        // Test 3: Leave queue
        console.log('\n📝 Test 3: Quitter la file...');
        ws.send(JSON.stringify({
            type: 'leave_matchmaking',
            playerId: 'test_player_1'
        }));
    }

    if (msg.type === 'left_queue') {
        console.log('\n✅ Sorti de la file!');

        // Test 4: Create room
        console.log('\n📝 Test 4: Créer une salle...');
        ws.send(JSON.stringify({
            type: 'create_room',
            playerId: 'test_player_1',
            roomName: 'Test Room',
            maxPlayers: 2,
            mode: '1v1'
        }));
    }

    if (msg.type === 'room_created') {
        console.log('\n✅ Salle créée! ID:', msg.roomId);
        console.log('\n════════════════════════════════════');
        console.log('   TOUS LES TESTS RÉUSSIS! ✅');
        console.log('════════════════════════════════════\n');
        ws.close();
        process.exit(0);
    }
});

ws.on('error', (err) => {
    console.error('❌ Erreur:', err.message);
    process.exit(1);
});

ws.on('close', () => {
    console.log('🔌 Connexion fermée');
});

// Timeout
setTimeout(() => {
    console.error('❌ Timeout - Le serveur ne répond pas');
    process.exit(1);
}, 10000);
