#!/bin/bash
echo "--- Configuração do Ambiente ---"
read -p "Usuário padrão (admin): " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}

read -sp "Senha padrão: " ADMIN_PASS
echo ""

read -p "Porta do Servidor Web (81): " WEB_PORT
WEB_PORT=${WEB_PORT:-81}

cat <<EOF > .env
PUID=$(id -u)
PGID=$(id -g)
TZ=America/Sao_Paulo
BASE_DATA_PATH=$HOME/DATA
BASE_CONFIG_PATH=$HOME/appdata

# Credenciais (usadas no script 03)
ADMIN_USER=$ADMIN_USER
ADMIN_PASS=$ADMIN_PASS

# Portas
WEB_PORT=$WEB_PORT
PROWLARR_PORT=9696
RADARR_PORT=7878
SONARR_PORT=8989
QBIT_PORT=8090
EOF