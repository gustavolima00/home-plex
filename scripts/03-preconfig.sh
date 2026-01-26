#!/bin/bash
source .env

setup_app_auth() {
    local app_dir="$BASE_CONFIG_PATH/$1"
    mkdir -p "$app_dir"
    cat <<EOF > "$app_dir/config.xml"
<Config>
  <AuthenticationMethod>Forms</AuthenticationMethod>
  <InstanceName>$1</InstanceName>
</Config>
EOF
    # Aqui o app usará o login padrão na primeira vez, ou 
    # você pode usar ferramentas de hash para injetar a senha direto no XML.
}

for app in prowlarr radarr sonarr; do
    setup_app_auth $app
done