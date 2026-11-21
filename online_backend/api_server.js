/**
 * KOF Ultimate Online - API Server
 * Serveur API REST pour gestion profils, stats, matchmaking
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Database = require('./database');

const app = express();
const PORT = process.env.PORT || 3100;
const JWT_SECRET = process.env.JWT_SECRET || (process.env.NODE_ENV === 'production' ? null : 'kof-ultimate-secret-key-change-in-production');
if (!JWT_SECRET) throw new Error('JWT_SECRET must be set in production');

// Middleware
app.use(cors());
app.use(express.json());

// Database
const db = new Database();

// ==================== AUTHENTICATION ====================

// Middleware d'authentification
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Token requis' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Token invalide' });
        }
        req.user = user;
        next();
    });
}

// Inscription
app.post('/api/auth/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;

        if (!username || !email || !password) {
            return res.status(400).json({ error: 'Tous les champs sont requis' });
        }

        // Hash password
        const passwordHash = await bcrypt.hash(password, 10);

        db.createPlayer(username, email, passwordHash, (err, player) => {
            if (err) {
                if (err.message.includes('UNIQUE')) {
                    return res.status(409).json({ error: 'Nom d\'utilisateur ou email déjà utilisé' });
                }
                return res.status(500).json({ error: 'Erreur création joueur' });
            }

            const token = jwt.sign(
                { id: player.id, username: player.username },
                JWT_SECRET,
                { expiresIn: '7d' }
            );

            res.status(201).json({
                message: 'Joueur créé avec succès',
                token,
                player: { id: player.id, username: player.username }
            });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// Connexion
app.post('/api/auth/login', async (req, res) => {
    try {
        const { username, password } = req.body;

        db.getPlayerByUsername(username, async (err, player) => {
            if (err || !player) {
                return res.status(401).json({ error: 'Identifiants invalides' });
            }

            const validPassword = await bcrypt.compare(password, player.password_hash);
            if (!validPassword) {
                return res.status(401).json({ error: 'Identifiants invalides' });
            }

            // Update status
            db.updatePlayerStatus(player.id, true, 'online', () => {});

            const token = jwt.sign(
                { id: player.id, username: player.username },
                JWT_SECRET,
                { expiresIn: '7d' }
            );

            res.json({
                message: 'Connexion réussie',
                token,
                player: {
                    id: player.id,
                    username: player.username,
                    display_name: player.display_name,
                    level: player.level,
                    avatar: player.avatar
                }
            });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// Déconnexion
app.post('/api/auth/logout', authenticateToken, (req, res) => {
    db.updatePlayerStatus(req.user.id, false, 'offline', (err) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur déconnexion' });
        }
        res.json({ message: 'Déconnexion réussie' });
    });
});

// ==================== PLAYER PROFILE ====================

// Get profile
app.get('/api/player/profile', authenticateToken, (req, res) => {
    db.getPlayerById(req.user.id, (err, player) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération profil' });
        }

        db.getPlayerStats(req.user.id, (err, stats) => {
            if (err) {
                return res.status(500).json({ error: 'Erreur récupération stats' });
            }

            res.json({
                player: {
                    id: player.id,
                    username: player.username,
                    display_name: player.display_name,
                    email: player.email,
                    level: player.level,
                    xp: player.xp,
                    avatar: player.avatar,
                    banner: player.banner,
                    created_at: player.created_at,
                    last_login: player.last_login
                },
                stats: stats || {}
            });
        });
    });
});

// Get player stats
app.get('/api/player/:id/stats', (req, res) => {
    db.getPlayerStats(req.params.id, (err, stats) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération stats' });
        }
        res.json(stats || {});
    });
});

// Update profile
app.patch('/api/player/profile', authenticateToken, (req, res) => {
    const { display_name, avatar, banner } = req.body;
    // TODO: Implement profile update
    res.json({ message: 'Profile update coming soon' });
});

// ==================== MATCHMAKING ====================

// Get online players
app.get('/api/matchmaking/players', authenticateToken, (req, res) => {
    db.getOnlinePlayers((err, players) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération joueurs' });
        }
        // Filter out current user
        const filteredPlayers = players.filter(p => p.id !== req.user.id);
        res.json(filteredPlayers);
    });
});

// ==================== ROOMS ====================

// Get available rooms
app.get('/api/rooms', authenticateToken, (req, res) => {
    db.getAvailableRooms((err, rooms) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération salles' });
        }
        res.json(rooms);
    });
});

// Create room
app.post('/api/rooms', authenticateToken, (req, res) => {
    const { room_name, password, max_players, mode } = req.body;

    const roomData = {
        room_name,
        host_id: req.user.id,
        password,
        max_players: max_players || 8,
        mode: mode || '1v1'
    };

    db.createRoom(roomData, (err, roomId) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur création salle' });
        }
        res.status(201).json({ message: 'Salle créée', roomId });
    });
});

// Delete room
app.delete('/api/rooms/:id', authenticateToken, (req, res) => {
    // TODO: Vérifier que le joueur est l'hôte
    db.deleteRoom(req.params.id, (err) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur suppression salle' });
        }
        res.json({ message: 'Salle supprimée' });
    });
});

// ==================== LEADERBOARD ====================

// Get leaderboard
app.get('/api/leaderboard', (req, res) => {
    const limit = parseInt(req.query.limit) || 100;
    db.getLeaderboard(limit, (err, leaderboard) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération classement' });
        }
        res.json(leaderboard);
    });
});

// ==================== MATCH HISTORY ====================

// Get match history
app.get('/api/player/matches', authenticateToken, (req, res) => {
    const limit = parseInt(req.query.limit) || 20;
    db.getPlayerMatchHistory(req.user.id, limit, (err, matches) => {
        if (err) {
            return res.status(500).json({ error: 'Erreur récupération historique' });
        }
        res.json(matches);
    });
});

// ==================== HEALTH CHECK ====================

app.get('/api/health', (req, res) => {
    res.json({
        status: 'online',
        service: 'KOF Ultimate Online API',
        version: '2.0.0',
        timestamp: new Date().toISOString()
    });
});

// ==================== SERVER START ====================

app.listen(PORT, () => {
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║                                                                ║');
    console.log('║          🌐  KOF ULTIMATE ONLINE - API SERVER                  ║');
    console.log('║                     Version 2.0.0                              ║');
    console.log('║                                                                ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('');
    console.log(`✅ API Server démarré sur http://localhost:${PORT}`);
    console.log('');
    console.log('📋 Endpoints disponibles:');
    console.log('   POST   /api/auth/register       - Inscription');
    console.log('   POST   /api/auth/login          - Connexion');
    console.log('   POST   /api/auth/logout         - Déconnexion');
    console.log('   GET    /api/player/profile      - Profil joueur');
    console.log('   GET    /api/player/:id/stats    - Stats joueur');
    console.log('   GET    /api/matchmaking/players - Joueurs en ligne');
    console.log('   GET    /api/rooms               - Salles disponibles');
    console.log('   POST   /api/rooms               - Créer une salle');
    console.log('   GET    /api/leaderboard         - Classement');
    console.log('   GET    /api/player/matches      - Historique matchs');
    console.log('   GET    /api/health              - Health check');
    console.log('');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Arrêt du serveur...');
    db.close();
    process.exit(0);
});

module.exports = app;
