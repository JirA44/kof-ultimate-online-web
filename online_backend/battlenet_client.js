/**
 * KOF Ultimate Online - Battle.net Style Client
 * Runs alongside the game, handles matchmaking & lobbies
 * Communicates with Ikemen GO via JSON files
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Configuration
const MATCHMAKING_SERVER = process.env.MATCHMAKING_URL || 'ws://localhost:3101';
const GAME_DIR = path.resolve(__dirname, '..');
const STATE_FILE = path.join(GAME_DIR, 'save', 'online_state.json');
const LOBBIES_FILE = path.join(GAME_DIR, 'save', 'lobbies.json');
const PROFILE_FILE = path.join(GAME_DIR, 'save', 'player_profile.json');

class BattleNetClient {
    constructor() {
        this.ws = null;
        this.playerId = null;
        this.playerName = 'Player';
        this.elo = 1000;
        this.connected = false;
        this.inQueue = false;
        this.currentMatch = null;
        this.lobbies = [];

        this.loadProfile();
    }

    // ==================== PROFILE ====================
    loadProfile() {
        try {
            if (fs.existsSync(PROFILE_FILE)) {
                const data = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8'));
                this.playerId = data.playerId;
                this.playerName = data.playerName || 'Player';
                this.elo = data.elo || 1000;
                console.log(`[Profile] Loaded: ${this.playerName} (ELO: ${this.elo})`);
            } else {
                this.playerId = this.generateId();
                this.saveProfile();
            }
        } catch (e) {
            console.error('[Profile] Error loading:', e.message);
            this.playerId = this.generateId();
        }
    }

    saveProfile() {
        const profile = {
            playerId: this.playerId,
            playerName: this.playerName,
            elo: this.elo,
            lastUpdated: new Date().toISOString()
        };
        fs.writeFileSync(PROFILE_FILE, JSON.stringify(profile, null, 2));
    }

    generateId() {
        return 'kof_' + Math.random().toString(36).substring(2, 15);
    }

    // ==================== CONNECTION ====================
    connect() {
        console.log(`[WS] Connecting to ${MATCHMAKING_SERVER}...`);

        this.ws = new WebSocket(MATCHMAKING_SERVER);

        this.ws.on('open', () => {
            console.log('[WS] Connected!');
            this.connected = true;
            this.register();
            this.updateState();
        });

        this.ws.on('message', (data) => {
            try {
                const msg = JSON.parse(data);
                this.handleMessage(msg);
            } catch (e) {
                console.error('[WS] Parse error:', e.message);
            }
        });

        this.ws.on('close', () => {
            console.log('[WS] Disconnected');
            this.connected = false;
            this.updateState();
            // Reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        });

        this.ws.on('error', (err) => {
            console.error('[WS] Error:', err.message);
        });
    }

    send(msg) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(msg));
        }
    }

    register() {
        this.send({
            type: 'register',
            playerId: this.playerId,
            playerName: this.playerName,
            elo: this.elo
        });
    }

    // ==================== MESSAGE HANDLERS ====================
    handleMessage(msg) {
        console.log('[MSG]', msg.type);

        switch (msg.type) {
            case 'registered':
                console.log(`[Registered] as ${msg.playerId}`);
                this.requestLobbies();
                break;

            case 'lobbies':
                this.lobbies = msg.lobbies || [];
                this.saveLobbies();
                break;

            case 'match_found':
                this.handleMatchFound(msg);
                break;

            case 'queue_joined':
                this.inQueue = true;
                console.log('[Queue] Joined matchmaking queue');
                this.updateState();
                break;

            case 'queue_left':
                this.inQueue = false;
                console.log('[Queue] Left matchmaking queue');
                this.updateState();
                break;

            case 'lobby_created':
                console.log(`[Lobby] Created: ${msg.lobbyId}`);
                this.updateState();
                break;

            case 'player_joined':
                console.log(`[Lobby] ${msg.playerName} joined`);
                break;

            case 'game_start':
                this.handleGameStart(msg);
                break;

            case 'error':
                console.error('[Server Error]', msg.message);
                break;
        }
    }

    handleMatchFound(msg) {
        console.log(`[Match Found] vs ${msg.opponent.playerName} (ELO: ${msg.opponent.elo})`);

        this.currentMatch = {
            matchId: msg.matchId,
            opponent: msg.opponent,
            isHost: msg.isHost,
            hostIp: msg.hostIp,
            port: msg.port || 7500
        };

        this.inQueue = false;
        this.updateState();

        // Auto-launch game connection
        if (this.currentMatch.isHost) {
            console.log('[Match] You are HOST. Waiting for opponent...');
        } else {
            console.log(`[Match] Connecting to ${this.currentMatch.hostIp}:${this.currentMatch.port}`);
        }
    }

    handleGameStart(msg) {
        console.log('[Game] Starting match!');
        this.currentMatch = {
            ...this.currentMatch,
            ...msg
        };
        this.updateState();
    }

    // ==================== ACTIONS ====================
    quickMatch() {
        console.log('[Action] Quick Match requested');
        this.send({
            type: 'join_queue',
            playerId: this.playerId,
            elo: this.elo,
            mode: 'versus'
        });
    }

    cancelQueue() {
        console.log('[Action] Cancel queue');
        this.send({
            type: 'leave_queue',
            playerId: this.playerId
        });
    }

    createLobby(name, maxPlayers = 2) {
        console.log(`[Action] Creating lobby: ${name}`);
        this.send({
            type: 'create_lobby',
            playerId: this.playerId,
            lobbyName: name,
            maxPlayers: maxPlayers
        });
    }

    joinLobby(lobbyId) {
        console.log(`[Action] Joining lobby: ${lobbyId}`);
        this.send({
            type: 'join_lobby',
            playerId: this.playerId,
            lobbyId: lobbyId
        });
    }

    requestLobbies() {
        this.send({ type: 'get_lobbies' });
    }

    // ==================== STATE MANAGEMENT ====================
    updateState() {
        const state = {
            connected: this.connected,
            playerId: this.playerId,
            playerName: this.playerName,
            elo: this.elo,
            inQueue: this.inQueue,
            currentMatch: this.currentMatch,
            lobbiesCount: this.lobbies.length,
            timestamp: Date.now()
        };

        try {
            fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
        } catch (e) {
            console.error('[State] Write error:', e.message);
        }
    }

    saveLobbies() {
        try {
            fs.writeFileSync(LOBBIES_FILE, JSON.stringify({
                lobbies: this.lobbies,
                timestamp: Date.now()
            }, null, 2));
        } catch (e) {
            console.error('[Lobbies] Write error:', e.message);
        }
    }

    // ==================== COMMAND WATCHER ====================
    // Watch for commands from the game (via file)
    startCommandWatcher() {
        const cmdFile = path.join(GAME_DIR, 'save', 'online_command.json');

        setInterval(() => {
            try {
                if (fs.existsSync(cmdFile)) {
                    const cmd = JSON.parse(fs.readFileSync(cmdFile, 'utf8'));
                    fs.unlinkSync(cmdFile); // Delete after reading

                    this.handleGameCommand(cmd);
                }
            } catch (e) {
                // Ignore read errors
            }
        }, 100); // Check every 100ms
    }

    handleGameCommand(cmd) {
        console.log('[Game Command]', cmd.action);

        switch (cmd.action) {
            case 'quick_match':
                this.quickMatch();
                break;
            case 'cancel_queue':
                this.cancelQueue();
                break;
            case 'create_lobby':
                this.createLobby(cmd.name || `${this.playerName}'s Game`);
                break;
            case 'join_lobby':
                this.joinLobby(cmd.lobbyId);
                break;
            case 'refresh_lobbies':
                this.requestLobbies();
                break;
            case 'set_name':
                this.playerName = cmd.name;
                this.saveProfile();
                this.register();
                break;
        }
    }
}

// ==================== MAIN ====================
console.log('╔══════════════════════════════════════════════════════════╗');
console.log('║     KOF ULTIMATE ONLINE - BATTLE.NET CLIENT              ║');
console.log('╚══════════════════════════════════════════════════════════╝');

const client = new BattleNetClient();
client.connect();
client.startCommandWatcher();

// Keep alive
process.on('SIGINT', () => {
    console.log('\n[Exit] Shutting down...');
    if (client.ws) client.ws.close();
    process.exit(0);
});
