#!/bin/bash

# 1. Configurar Hostname (.local)
sudo hostnamectl set-hostname inspiron-server
sudo apt-get update && sudo apt-get install avahi-daemon -y

# 2. Instalar Docker (se não existir)
if ! [ -x "$(command -v docker)" ]; then
  curl -fsSL https://get.docker.com | sh
fi

# 3. Criar estrutura de pastas
mkdir -p $BASE_DATA_PATH/{downloads,media/{filmes,series}}
mkdir -p $BASE_CONFIG_PATH/{plex,prowlarr,radarr,sonarr,qbittorrent}

# 4. Subir a Stack
docker compose up -d

echo "Aguardando inicialização para configurar APIs..."
sleep 30

# 5. Aqui você pode rodar comandos curl para injetar as API Keys
# (Conforme discutimos no passo anterior de automação de API)