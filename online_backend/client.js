/**
 * KOF Ultimate Online - Client
 * Client pour se connecter à l'API et au matchmaking
 */

const WebSocket = require('ws');
const https = require('https');

class KOFOnlineClient {
    constructor(apiUrl = 'http://localhost:3100', wsUrl = 'ws://localhost:3101') {
        this.apiUrl = apiUrl;
        this.wsUrl = wsUrl;
        this.token = null;
        this.playerId = null;
        this.ws = null;
        this.eventHandlers = {};
    }

    // ==================== API METHODS ====================

    async register(username, email, password) {
        const response = await this._apiRequest('/api/auth/register', 'POST', {
            username,
            email,
            password
        });

        if (response.token) {
            this.token = response.token;
            this.playerId = response.player.id;
        }

        return response;
    }

    async login(username, password) {
        const response = await this._apiRequest('/api/auth/login', 'POST', {
            username,
            password
        });

        if (response.token) {
            this.token = response.token;
            this.playerId = response.player.id;
        }

        return response;
    }

    async logout() {
        const response = await this._apiRequest('/api/auth/logout', 'POST', {}, true);
        this.token = null;
        this.playerId = null;
        return response;
    }

    async getProfile() {
        return await this._apiRequest('/api/player/profile', 'GET', null, true);
    }

    async getStats(playerId = null) {
        const id = playerId || this.playerId;
        return await this._apiRequest(`/api/player/${id}/stats`, 'GET');
    }

    async getOnlinePlayers() {
        return await this._apiRequest('/api/matchmaking/players', 'GET', null, true);
    }

    async getRooms() {
        return await this._apiRequest('/api/rooms', 'GET', null, true);
    }

    async createRoom(roomData) {
        return await this._apiRequest('/api/rooms', 'POST', roomData, true);
    }

    async getLeaderboard(limit = 100) {
        return await this._apiRequest(`/api/leaderboard?limit=${limit}`, 'GET');
    }

    async getMatchHistory(limit = 20) {
        return await this._apiRequest(`/api/player/matches?limit=${limit}`, 'GET', null, true);
    }

    // ==================== WEBSOCKET METHODS ====================

    connectMatchmaking(username, elo = 1000) {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.wsUrl);

            this.ws.on('open', () => {
                console.log('✅ Connecté au serveur matchmaking');

                // Register
                if (!this.token || this.playerId === null) {
                    this.ws.close();
                    return reject(new Error('Authentifiez-vous avant la connexion au matchmaking'));
                }
                this.ws.send(JSON.stringify({
                    type: 'register',
                    playerId: this.playerId,
                    username: username,
                    token: this.token,
                    elo: elo
                }));

                resolve();
            });

            this.ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    this._handleMessage(message);
                } catch (error) {
                    console.error('❌ Erreur parsing message:', error);
                }
            });

            this.ws.on('error', (error) => {
                console.error('❌ WebSocket error:', error);
                reject(error);
            });

            this.ws.on('close', () => {
                console.log('🔌 Déconnecté du serveur matchmaking');
                this._emit('disconnected');
            });
        });
    }

    joinMatchmaking(mode = 'quick', elo = 1000) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            throw new Error('Non connecté au serveur matchmaking');
        }

        this.ws.send(JSON.stringify({
            type: 'join_matchmaking',
            playerId: this.playerId,
            mode: mode,
            elo: elo
        }));

        console.log(`🔍 Recherche de match en cours (${mode})...`);
    }

    leaveMatchmaking() {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'leave_matchmaking',
            playerId: this.playerId
        }));

        console.log('❌ Sortie de la file d\'attente');
    }

    reportMatchResult(matchId, winnerId, loserId, duration) {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'match_result',
            matchId: matchId,
            winnerId: winnerId,
            loserId: loserId,
            duration: duration
        }));
    }

    createCustomRoom(roomName, password = null, maxPlayers = 8, mode = '1v1') {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'create_room',
            playerId: this.playerId,
            roomName: roomName,
            password: password,
            maxPlayers: maxPlayers,
            mode: mode
        }));
    }

    joinRoom(roomId, password = null) {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'join_room',
            playerId: this.playerId,
            roomId: roomId,
            password: password
        }));
    }

    leaveRoom(roomId) {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'leave_room',
            playerId: this.playerId,
            roomId: roomId
        }));
    }

    sendChatMessage(roomId, message) {
        if (!this.ws) return;

        this.ws.send(JSON.stringify({
            type: 'chat_message',
            playerId: this.playerId,
            roomId: roomId,
            message: message
        }));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    // ==================== EVENT HANDLERS ====================

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    _emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    _handleMessage(message) {
        console.log('📩 Message reçu:', message.type);

        switch (message.type) {
            case 'registered':
                this._emit('registered', message);
                break;

            case 'searching':
                this._emit('searching', message);
                break;

            case 'match_found':
                console.log('🎮 Match trouvé!');
                console.log(`   Adversaire: ${message.opponent.username}`);
                console.log(`   ELO: ${message.opponent.elo}`);
                this._emit('match_found', message);
                break;

            case 'match_complete':
                console.log(`🏆 Match terminé: ${message.result}`);
                console.log(`   ELO: ${message.eloChange} (Nouveau: ${message.newElo})`);
                this._emit('match_complete', message);
                break;

            case 'room_created':
                this._emit('room_created', message);
                break;

            case 'joined_room':
                this._emit('joined_room', message);
                break;

            case 'player_joined_room':
                this._emit('player_joined_room', message);
                break;

            case 'player_left_room':
                this._emit('player_left_room', message);
                break;

            case 'chat_message':
                this._emit('chat_message', message);
                break;

            case 'player_online':
                this._emit('player_online', message);
                break;

            case 'player_offline':
                this._emit('player_offline', message);
                break;

            case 'new_room':
                this._emit('new_room', message);
                break;

            case 'room_closed':
                this._emit('room_closed', message);
                break;

            case 'error':
                console.error('❌ Erreur:', message.message);
                this._emit('error', message);
                break;

            case 'pong':
                // Heartbeat response
                break;

            default:
                console.log('❓ Message inconnu:', message.type);
        }
    }

    // ==================== PRIVATE METHODS ====================

    async _apiRequest(endpoint, method = 'GET', body = null, requireAuth = false) {
        const url = `${this.apiUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };

        if (requireAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const options = {
            method: method,
            headers: headers
        };

        if (body && method !== 'GET') {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur API');
            }

            return data;
        } catch (error) {
            console.error(`❌ Erreur API (${method} ${endpoint}):`, error.message);
            throw error;
        }
    }
}

// Export for browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KOFOnlineClient;
}
