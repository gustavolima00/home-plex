# 🎬 Home-Plex

A complete, self-hosted media server stack with automated setup.

## 📦 Included Services

| Service | Description | Default Port |
|---------|-------------|--------------|
| **Plex** | Media server for streaming | 32400 |
| **Prowlarr** | Indexer manager | 9696 |
| **Radarr** | Movie collection manager | 7878 |
| **Sonarr** | TV series collection manager | 8989 |
| **qBittorrent** | Torrent client | 8090 |
| **FlareSolverr** | Cloudflare bypass for indexers | 8191 |

## 🚀 Quick Start

### Prerequisites

- Linux (Ubuntu/Debian recommended)
- `curl` installed

### Installation

```bash
git clone https://github.com/your-username/home-plex.git
cd home-plex
./install.sh
```

The installer will:
1. ✅ Install [uv](https://github.com/astral-sh/uv) (if not present)
2. ✅ Install Docker and Docker Compose
3. ✅ Prompt you for configuration (username, password, API keys, ports)
4. ✅ Create necessary directories
5. ✅ Start all containers
6. ✅ Configure Prowlarr with FlareSolverr

### Uninstallation

```bash
./uninstall.sh
```

This will:
- Stop and remove all containers
- Optionally remove Docker images
- Optionally delete data and config directories

## ⚙️ Configuration

During installation, you'll be prompted for:

| Setting | Default | Description |
|---------|---------|-------------|
| Admin username | `admin` | Username for apps |
| Admin password | `admin` | Password for apps |
| Prowlarr API Key | *auto-generated* | API key for Prowlarr/Sonarr/Radarr integration |
| Data path | `~/DATA` | Where media files are stored |
| Config path | `~/appdata` | Where app configs are stored |

All configuration is saved to `.env` file.

## 📁 Directory Structure

```
~/DATA/
├── media/
│   ├── movies/      # Downloaded movies
│   └── tv/          # Downloaded TV shows
└── torrents/
    ├── movies/      # Movie torrents
    └── tv/          # TV torrents

~/appdata/
├── plex/           # Plex configuration
├── prowlarr/       # Prowlarr configuration
├── radarr/         # Radarr configuration
├── sonarr/         # Sonarr configuration
└── qbittorrent/    # qBittorrent configuration
```

## 🌐 Access Your Services

After installation, access your services at:

- **Plex**: http://localhost:32400/web
- **Prowlarr**: http://localhost:9696
- **Radarr**: http://localhost:7878
- **Sonarr**: http://localhost:8989
- **qBittorrent**: http://localhost:8090

## 🔧 Manual Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart a specific service
docker compose restart prowlarr
```

## 📝 Files

| File | Description |
|------|-------------|
| `install.sh` | Main installer (bootstraps uv + runs setup) |
| `uninstall.sh` | Uninstaller |
| `docker-compose.yml` | Docker service definitions |
| `.env` | Configuration (created during install) |
| `scripts/setup.py` | Python setup script |
| `scripts/uninstall.py` | Python uninstall script |

## 🛠️ Tech Stack

- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal UI
- **[Docker](https://www.docker.com/)** - Container runtime
- **[LinuxServer.io](https://www.linuxserver.io/)** - Container images

## 📄 License

MIT
