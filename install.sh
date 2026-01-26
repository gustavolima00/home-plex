#!/bin/bash

./scripts/01-system.sh
./scripts/02-env.sh
./scripts/03-preconfig.sh

# 2. Subir o Docker
docker compose up -d

# 3. Wait for Ready
./scripts/04-wait.sh

# 4. Finalização
source .env
echo "--- Setup Finalizado ---"
echo "Acesse: http://$(hostname).local:$WEB_PORT"
echo "Login padrão injetado nos arquivos de config."