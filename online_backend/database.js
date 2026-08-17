/**
 * KOF Ultimate Online - Database Manager
 * Gestion de la base de données SQLite pour profils joueurs
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class Database {
    constructor(dbPath = path.join(__dirname, 'kof_online.db')) {
        this.db = new sqlite3.Database(dbPath, (err) => {
            if (err) {
                console.error('❌ Erreur connexion DB:', err);
            } else {
                console.log('✅ Connecté à la base de données');
                this.initTables();
            }
        });
    }

    initTables() {
        // Table des joueurs
        this.db.run(`
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                avatar TEXT DEFAULT 'default.png',
                banner TEXT DEFAULT 'default_banner.png',
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_online INTEGER DEFAULT 0,
                status TEXT DEFAULT 'offline'
            )
        `);

        // Table des statistiques
        this.db.run(`
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id INTEGER PRIMARY KEY,
                total_wins INTEGER DEFAULT 0,
                total_losses INTEGER DEFAULT 0,
                total_draws INTEGER DEFAULT 0,
                ranked_wins INTEGER DEFAULT 0,
                ranked_losses INTEGER DEFAULT 0,
                elo_rating INTEGER DEFAULT 1000,
                highest_elo INTEGER DEFAULT 1000,
                win_streak INTEGER DEFAULT 0,
                longest_win_streak INTEGER DEFAULT 0,
                total_matches INTEGER DEFAULT 0,
                total_playtime INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        `);

        // Table des matchs
        this.db.run(`
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_type TEXT NOT NULL,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,
                winner_id INTEGER,
                player1_characters TEXT,
                player2_characters TEXT,
                duration INTEGER,
                elo_change INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player1_id) REFERENCES players(id),
                FOREIGN KEY (player2_id) REFERENCES players(id),
                FOREIGN KEY (winner_id) REFERENCES players(id)
            )
        `);

        // Table des salles personnalisées
        this.db.run(`
            CREATE TABLE IF NOT EXISTS custom_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                host_id INTEGER NOT NULL,
                password TEXT,
                max_players INTEGER DEFAULT 8,
                current_players INTEGER DEFAULT 1,
                mode TEXT DEFAULT '1v1',
                status TEXT DEFAULT 'waiting',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES players(id)
            )
        `);

        // Table des amis
        this.db.run(`
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                friend_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (friend_id) REFERENCES players(id)
            )
        `);

        // Table des achievements
        this.db.run(`
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                requirement_type TEXT,
                requirement_value INTEGER
            )
        `);

        // Table player_achievements
        this.db.run(`
            CREATE TABLE IF NOT EXISTS player_achievements (
                player_id INTEGER,
                achievement_id INTEGER,
                unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, achievement_id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )
        `);

        console.log('✅ Tables initialisées');
    }

    // ==================== PLAYERS ====================

    createPlayer(username, email, passwordHash, callback) {
        const sql = `INSERT INTO players (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)`;
        const db = this.db; // Save reference for callback
        db.run(sql, [username, email, passwordHash, username], function(err) {
            if (err) {
                callback(err, null);
            } else {
                // Créer les stats par défaut
                const playerId = this.lastID;
                const statsSQL = `INSERT INTO player_stats (player_id) VALUES (?)`;
                db.run(statsSQL, [playerId], (statsErr) => {
                    if (statsErr) {
                        callback(statsErr, null);
                        return;
                    }
                    callback(null, { id: playerId, username });
                });
            }
        });
    }

    getPlayerByUsername(username, callback) {
        const sql = `SELECT * FROM players WHERE username = ?`;
        this.db.get(sql, [username], callback);
    }

    getPlayerById(id, callback) {
        const sql = `SELECT * FROM players WHERE id = ?`;
        this.db.get(sql, [id], callback);
    }

    updatePlayerStatus(playerId, isOnline, status, callback) {
        const sql = `UPDATE players SET is_online = ?, status = ?, last_login = CURRENT_TIMESTAMP WHERE id = ?`;
        this.db.run(sql, [isOnline ? 1 : 0, status, playerId], callback);
    }

    getOnlinePlayers(callback) {
        const sql = `
            SELECT id, username, display_name, level, status, avatar
            FROM players
            WHERE is_online = 1
            ORDER BY level DESC
        `;
        this.db.all(sql, callback);
    }

    // ==================== STATS ====================

    getPlayerStats(playerId, callback) {
        const sql = `
            SELECT ps.*, p.username, p.display_name, p.level, p.avatar
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            WHERE ps.player_id = ?
        `;
        this.db.get(sql, [playerId], callback);
    }

    updateStats(playerId, statsUpdate, callback) {
        const fields = Object.keys(statsUpdate).map(key => `${key} = ?`).join(', ');
        const values = [...Object.values(statsUpdate), playerId];
        const sql = `UPDATE player_stats SET ${fields} WHERE player_id = ?`;
        this.db.run(sql, values, callback);
    }

    // ==================== MATCHES ====================

    createMatch(matchData, callback) {
        const sql = `
            INSERT INTO matches (match_type, player1_id, player2_id, winner_id,
                               player1_characters, player2_characters, duration, elo_change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `;
        const values = [
            matchData.match_type,
            matchData.player1_id,
            matchData.player2_id,
            matchData.winner_id,
            matchData.player1_characters,
            matchData.player2_characters,
            matchData.duration,
            matchData.elo_change
        ];
        this.db.run(sql, values, callback);
    }

    getPlayerMatchHistory(playerId, limit = 20, callback) {
        const sql = `
            SELECT m.*,
                   p1.username as player1_name,
                   p2.username as player2_name,
                   w.username as winner_name
            FROM matches m
            LEFT JOIN players p1 ON m.player1_id = p1.id
            LEFT JOIN players p2 ON m.player2_id = p2.id
            LEFT JOIN players w ON m.winner_id = w.id
            WHERE m.player1_id = ? OR m.player2_id = ?
            ORDER BY m.created_at DESC
            LIMIT ?
        `;
        this.db.all(sql, [playerId, playerId, limit], callback);
    }

    // ==================== ROOMS ====================

    createRoom(roomData, callback) {
        const sql = `
            INSERT INTO custom_rooms (room_name, host_id, password, max_players, mode)
            VALUES (?, ?, ?, ?, ?)
        `;
        const values = [
            roomData.room_name,
            roomData.host_id,
            roomData.password || null,
            roomData.max_players || 8,
            roomData.mode || '1v1'
        ];
        this.db.run(sql, values, function(err) {
            if (callback) callback(err, this.lastID);
        });
    }

    getAvailableRooms(callback) {
        const sql = `
            SELECT r.*, p.username as host_name
            FROM custom_rooms r
            JOIN players p ON r.host_id = p.id
            WHERE r.status = 'waiting' AND r.current_players < r.max_players
            ORDER BY r.created_at DESC
        `;
        this.db.all(sql, callback);
    }

    deleteRoom(roomId, callback) {
        const sql = `DELETE FROM custom_rooms WHERE id = ?`;
        this.db.run(sql, [roomId], callback);
    }

    // ==================== LEADERBOARD ====================

    getLeaderboard(limit = 100, callback) {
        const sql = `
            SELECT p.id, p.username, p.display_name, p.level, p.avatar,
                   ps.elo_rating, ps.total_wins, ps.total_losses, ps.win_streak,
                   ps.ranked_wins, ps.ranked_losses
            FROM players p
            JOIN player_stats ps ON p.id = ps.player_id
            ORDER BY ps.elo_rating DESC
            LIMIT ?
        `;
        this.db.all(sql, [limit], callback);
    }

    // ==================== UTILITY ====================

    close() {
        this.db.close((err) => {
            if (err) {
                console.error('❌ Erreur fermeture DB:', err);
            } else {
                console.log('✅ Base de données fermée');
            }
        });
    }
}

module.exports = Database;
