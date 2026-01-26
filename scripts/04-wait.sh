#!/bin/bash
wait_for_http() {
    local url=$1
    local name=$2
    local timeout=60
    local count=0

    echo -n "Aguardando $name iniciar"
    until $(curl --output /dev/null --silent --head --fail --connect-timeout 2 "$url"); do
        printf '.'
        sleep 2
        ((count+=2))
        if [ $count -ge $timeout ]; then
            echo " [ERRO: Timeout]"
            return 1
        fi
    done
    echo " [PRONTO]"
}

source .env
wait_for_http "http://localhost:$PROWLARR_PORT" "Prowlarr"
wait_for_http "http://localhost:$RADARR_PORT" "Radarr"
wait_for_http "http://localhost:$SONARR_PORT" "Sonarr"