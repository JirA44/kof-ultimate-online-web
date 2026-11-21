# 🌐 KOF ULTIMATE ONLINE - BACKEND v2.0

Système backend complet pour KOF Ultimate Online avec matchmaking, profils joueurs, et intégration Cloudflare.

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Démarrage](#démarrage)
6. [API Documentation](#api-documentation)
7. [WebSocket Protocol](#websocket-protocol)
8. [Cloudflare Deploy](#cloudflare-deploy)
9. [Base de données](#base-de-données)
10. [Client SDK](#client-sdk)

---

## 🎯 VUE D'ENSEMBLE

### Composants

Le backend KOF Ultimate Online se compose de 3 services principaux:

1. **API Server** (Port 3100) - REST API pour profils, stats, authentification
2. **Matchmaking Server** (Port 3101) - WebSocket pour matchmaking temps réel
3. **Cloudflare Worker** - Gateway API avec CDN global

### Fonctionnalités

✅ **Authentification**
- Inscription/Connexion avec JWT
- Hash bcrypt pour mots de passe
- Sessions sécurisées

✅ **Profils Joueurs**
- Profils personnalisables
- Avatars et bannières
- Système de niveaux et XP

✅ **Statistiques**
- Wins/Losses
- ELO Rating
- Historique des matchs
- Streaks

✅ **Matchmaking**
- Matchmaking rapide (Quick Match)
- Matchmaking classé (Ranked)
- Matching basé sur ELO ±200
- Temps réel via WebSocket

✅ **Salles Personnalisées**
- Création de salles
- Mot de passe optionnel
- Modes de jeu configurables
- Chat en temps réel

✅ **Leaderboard**
- Classement global ELO
- Top 100 joueurs
- Filtrage par mode

---

## 🏗️ ARCHITECTURE

```
┌─────────────────┐
│  Client (Jeu)   │
└────────┬────────┘
         │
         ├─────────────────┬───────────────────┐
         │                 │                   │
         ▼                 ▼                   ▼
┌────────────────┐  ┌─────────────┐  ┌──────────────────┐
│ Cloudflare     │  │ API Server  │  │ Matchmaking      │
│ Worker         │  │ (REST)      │  │ Server (WS)      │
│ (Gateway)      │  │ :3100       │  │ :3101            │
└────────────────┘  └──────┬──────┘  └────────┬─────────┘
                           │                  │
                           ▼                  ▼
                    ┌──────────────────────────┐
                    │   SQLite Database        │
                    │   (kof_online.db)        │
                    └──────────────────────────┘
```

### Technologies

- **Node.js** - Runtime JavaScript
- **Express** - Framework API REST
- **ws** - WebSocket server
- **SQLite3** - Base de données
- **bcrypt** - Hash passwords
- **JWT** - Authentication tokens
- **Cloudflare Workers** - Edge computing

---

## 💻 INSTALLATION

### Prérequis

- Node.js 16+ ([télécharger](https://nodejs.org/))
- npm (inclus avec Node.js)
- Compte Cloudflare (optionnel pour deploy)

### Étapes

1. **Installer les dépendances**

```bash
cd "D:\KOF Ultimate Online\online_backend"
npm install
```

2. **Configurer l'environnement**

```bash
# Copier le fichier exemple
copy .env.example .env

# Éditer .env et configurer vos valeurs
notepad .env
```

3. **Initialiser la base de données**

La base de données sera créée automatiquement au premier démarrage.

---

## ⚙️ CONFIGURATION

### Fichier .env

```env
# Ports
PORT=3100
MATCHMAKING_PORT=3101

# JWT Secret (IMPORTANT: Changez en production!)
JWT_SECRET=votre-secret-jwt-ultra-securise

# Database
DB_PATH=./kof_online.db

# CORS
ALLOWED_ORIGINS=http://localhost,http://localhost:3000
```

### Configuration Cloudflare

Éditez `wrangler.toml`:

```toml
account_id = "votre_account_id_cloudflare"
name = "kof-ultimate-online-api"
```

---

## 🚀 DÉMARRAGE

### Option 1: Script Batch (Windows)

```batch
START_BACKEND_COMPLETE.bat
```

Démarre automatiquement les deux serveurs dans des fenêtres séparées.

### Option 2: Commandes npm

**Démarrer API Server:**
```bash
npm run api
```

**Démarrer Matchmaking Server:**
```bash
npm run matchmaking
```

**Démarrer les deux en parallèle:**
```bash
npm run all
```

### Vérification

Ouvrez dans votre navigateur:
- API Health: http://localhost:3100/api/health
- Matchmaking Health: http://localhost:3101/health

---

## 📡 API DOCUMENTATION

### Base URL

```
http://localhost:3100/api
```

### Authentification

#### POST /api/auth/register

Inscription d'un nouveau joueur.

**Body:**
```json
{
  "username": "player123",
  "email": "player@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "message": "Joueur créé avec succès",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "player": {
    "id": 1,
    "username": "player123"
  }
}
```

#### POST /api/auth/login

Connexion d'un joueur.

**Body:**
```json
{
  "username": "player123",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "message": "Connexion réussie",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "player": {
    "id": 1,
    "username": "player123",
    "display_name": "player123",
    "level": 15,
    "avatar": "avatar_01.png"
  }
}
```

#### POST /api/auth/logout

Déconnexion (requiert token).

**Headers:**
```
Authorization: Bearer <token>
```

### Profils

#### GET /api/player/profile

Récupère le profil du joueur connecté.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "player": {
    "id": 1,
    "username": "player123",
    "display_name": "player123",
    "email": "player@example.com",
    "level": 15,
    "xp": 3450,
    "avatar": "avatar_01.png",
    "banner": "banner_02.png",
    "created_at": "2025-01-15 10:30:00",
    "last_login": "2025-01-20 14:25:00"
  },
  "stats": {
    "total_wins": 45,
    "total_losses": 23,
    "elo_rating": 1250,
    "win_streak": 3
  }
}
```

#### GET /api/player/:id/stats

Récupère les stats d'un joueur spécifique.

### Matchmaking

#### GET /api/matchmaking/players

Liste des joueurs en ligne.

**Headers:**
```
Authorization: Bearer <token>
```

### Salles

#### GET /api/rooms

Liste des salles disponibles.

#### POST /api/rooms

Créer une nouvelle salle.

**Body:**
```json
{
  "room_name": "Ma Salle",
  "password": "secret",
  "max_players": 8,
  "mode": "1v1"
}
```

### Classement

#### GET /api/leaderboard?limit=100

Récupère le classement global.

**Response:**
```json
[
  {
    "id": 1,
    "username": "pro_player",
    "display_name": "Pro Player",
    "level": 50,
    "avatar": "avatar_10.png",
    "elo_rating": 2100,
    "total_wins": 450,
    "total_losses": 123,
    "win_streak": 15
  },
  ...
]
```

---

## 🔐 MULTIPLAYER AUTHENTICATION AND LOAD TESTS

The matchmaking WebSocket verifies the API JWT when `REQUIRE_WS_AUTH=true` (the default). The WebSocket client must send the same bearer token returned by `/api/auth/register` or `/api/auth/login`; the server derives the player ID and username from that token. Client-supplied identity, ELO and match-result fields are not trusted. For isolated legacy local testing only, `REQUIRE_WS_AUTH=false` allows unauthenticated profiles; never use that mode on a public deployment.

Both services load `.env` with dotenv and must share the same `JWT_SECRET`. A development fallback is retained only when `NODE_ENV` is not `production`. Production startup fails if `JWT_SECRET` is missing. A committed `.env` file must never contain credentials; use `.env.example` as a template and rotate any values that may have been exposed.

Set `GAME_SERVER_URL` to the actual reachable game transport endpoint. `localhost` works only when the client and game server run on the same machine; remote clients require a deployed endpoint, normally `wss://...`.

Run the load test only against a local test deployment backed by a disposable database. Set `DB_PATH=./kof_stress_test.db` before starting the API and matchmaking processes (the database path is now configurable). Do not point the test at production or your live player database.

```bash
# In the online_backend directory, using a dedicated test .env:
npm run all
# In another terminal:
npm run test:multiplayer
```

The test uses 20 temporary accounts, verifies authenticated WebSocket registration and complete match-result cycles, and exits nonzero when the expected flow fails. Its ping percentiles describe client-to-matchmaking round trips. Server RSS and CPU values are sampled from `/health`; these measurements describe this test environment and do not establish production capacity. Increase player counts in controlled stages and record deployment, hardware, duration and errors before claiming capacity.

---
## 🔌 WEBSOCKET PROTOCOL

### Connexion

```javascript
const ws = new WebSocket('ws://localhost:3101');
```

### Messages

Tous les messages sont au format JSON.

#### Register (Client → Server)

```json
{
  "type": "register",
  "playerId": 1,
  "username": "player123",
  "elo": 1250
}
```

#### Join Matchmaking (Client → Server)

```json
{
  "type": "join_matchmaking",
  "playerId": 1,
  "mode": "quick",
  "elo": 1250
}
```

#### Match Found (Server → Client)

```json
{
  "type": "match_found",
  "matchId": "uuid-here",
  "opponent": {
    "id": 2,
    "username": "opponent123",
    "elo": 1230
  }
}
```

#### Report Match Result (Client → Server)

```json
{
  "type": "match_result",
  "matchId": "uuid-here",
  "winnerId": 1,
  "loserId": 2,
  "duration": 180
}
```

#### Match Complete (Server → Client)

```json
{
  "type": "match_complete",
  "result": "victory",
  "eloChange": "+25",
  "newElo": 1275
}
```

### Events

- `registered` - Inscription confirmée
- `searching` - En recherche d'adversaire
- `match_found` - Match trouvé
- `match_complete` - Match terminé
- `player_online` - Joueur connecté
- `player_offline` - Joueur déconnecté
- `room_created` - Salle créée
- `new_room` - Nouvelle salle disponible
- `chat_message` - Message chat

---

## ☁️ CLOUDFLARE DEPLOY

### Prérequis

1. Compte Cloudflare
2. Wrangler CLI installé

```bash
npm install -g wrangler
```

### Configuration

1. **Login Cloudflare**

```bash
wrangler login
```

2. **Obtenir Account ID**

Dashboard Cloudflare → Workers → Overview → Account ID

3. **Éditer wrangler.toml**

```toml
account_id = "votre_account_id"
```

### Deploy

```bash
wrangler publish
```

Votre API sera disponible sur: `https://kof-ultimate-online-api.your-subdomain.workers.dev`

### Cloudflare Tunnel (pour backend local)

1. **Installer cloudflared**

```bash
# Windows
winget install Cloudflare.cloudflared
```

2. **Créer tunnel**

```bash
cloudflared tunnel create kof-ultimate-tunnel
```

3. **Router le trafic**

```bash
cloudflared tunnel route dns kof-ultimate-tunnel api.your-domain.com
```

4. **Démarrer tunnel**

```bash
cloudflared tunnel run kof-ultimate-tunnel --url http://localhost:3100
```

---

## 💾 BASE DE DONNÉES

### Structure

#### Table: players

```sql
CREATE TABLE players (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  email TEXT UNIQUE,
  password_hash TEXT,
  display_name TEXT,
  avatar TEXT,
  level INTEGER DEFAULT 1,
  xp INTEGER DEFAULT 0,
  created_at DATETIME,
  last_login DATETIME,
  is_online INTEGER DEFAULT 0
)
```

#### Table: player_stats

```sql
CREATE TABLE player_stats (
  player_id INTEGER PRIMARY KEY,
  total_wins INTEGER DEFAULT 0,
  total_losses INTEGER DEFAULT 0,
  elo_rating INTEGER DEFAULT 1000,
  win_streak INTEGER DEFAULT 0,
  FOREIGN KEY (player_id) REFERENCES players(id)
)
```

#### Table: matches

```sql
CREATE TABLE matches (
  id INTEGER PRIMARY KEY,
  match_type TEXT,
  player1_id INTEGER,
  player2_id INTEGER,
  winner_id INTEGER,
  duration INTEGER,
  elo_change INTEGER,
  created_at DATETIME
)
```

### Backup

```bash
# Backup manuel
copy kof_online.db kof_online_backup.db

# Ou via SQLite
sqlite3 kof_online.db ".backup kof_online_backup.db"
```

---

## 📦 CLIENT SDK

### Installation

Le client est inclus dans `client.js`.

### Utilisation

```javascript
const KOFOnlineClient = require('./client.js');

const client = new KOFOnlineClient('http://localhost:3100', 'ws://localhost:3101');

// Inscription
await client.register('username', 'email@example.com', 'password');

// Connexion
await client.login('username', 'password');

// Connecter au matchmaking
await client.connectMatchmaking('username', 1250);

// Rejoindre la file d'attente
client.joinMatchmaking('quick', 1250);

// Écouter les événements
client.on('match_found', (data) => {
  console.log('Match trouvé!', data.opponent);
});

client.on('match_complete', (data) => {
  console.log('Match terminé:', data.result);
  console.log('Nouveau ELO:', data.newElo);
});
```

---

## 🧪 TESTS

```bash
# Test connexion API
npm run test

# Ou manuellement
curl http://localhost:3100/api/health
```

---

## 🔒 SÉCURITÉ

### Production

**IMPORTANT:** Avant de déployer en production:

1. **Changer JWT_SECRET** dans .env
2. **Utiliser HTTPS** uniquement
3. **Activer rate limiting**
4. **Valider toutes les entrées**
5. **Ajouter logs de sécurité**

### Rate Limiting

À implémenter avec `express-rate-limit`:

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // max 100 requests par IP
});

app.use('/api/', limiter);
```

---

## 📞 SUPPORT

- Documentation: Ce fichier
- Issues: GitHub
- Discord: [Lien Discord]

---

## 📝 CHANGELOG

### v2.0.0 (2025-01-25)

- ✅ Architecture complète backend
- ✅ API REST avec authentification JWT
- ✅ Serveur matchmaking WebSocket
- ✅ Base de données SQLite
- ✅ Système ELO
- ✅ Salles personnalisées
- ✅ Cloudflare Worker
- ✅ Client SDK
- ✅ Documentation complète

---

**Créé pour KOF Ultimate Online v2.0**
