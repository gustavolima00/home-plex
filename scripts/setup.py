#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
#     "requests>=2.28.0",
# ]
# ///
"""
Home-Plex Server Setup
A beautiful, interactive setup for your home media server using Python + Rich.
"""

import os
import subprocess
import secrets
import time
from pathlib import Path
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box
import requests

console = Console()


@dataclass
class Config:
    """Server configuration"""

    admin_user: str = "admin"
    admin_pass: str = "admin"
    prowlarr_api_key: str = ""
    base_data_path: str = ""
    base_config_path: str = ""
    plex_port: int = 32400
    prowlarr_port: int = 9696
    flaresolverr_port: int = 8191
    radarr_port: int = 7878
    sonarr_port: int = 8989
    qbit_webui_port: int = 8090
    qbit_port: int = 6881
    puid: int = field(default_factory=lambda: os.getuid())
    pgid: int = field(default_factory=lambda: os.getgid())

    def __post_init__(self):
        home = os.path.expanduser("~")
        if not self.base_data_path:
            self.base_data_path = f"{home}/DATA"
        if not self.base_config_path:
            self.base_config_path = f"{home}/appdata"
        if not self.prowlarr_api_key:
            self.prowlarr_api_key = secrets.token_hex(16)


def print_banner():
    """Display the welcome banner."""
    banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]                                                                      [bold cyan]║[/]
[bold cyan]║[/]   [bold white]██╗  ██╗ ██████╗ ███╗   ███╗███████╗    ██████╗ ██╗     ███████╗██╗  ██╗[/]   [bold cyan]║[/]
[bold cyan]║[/]   [bold white]██║  ██║██╔═══██╗████╗ ████║██╔════╝    ██╔══██╗██║     ██╔════╝╚██╗██╔╝[/]   [bold cyan]║[/]
[bold cyan]║[/]   [bold white]███████║██║   ██║██╔████╔██║█████╗█████╗██████╔╝██║     █████╗   ╚███╔╝ [/]   [bold cyan]║[/]
[bold cyan]║[/]   [bold white]██╔══██║██║   ██║██║╚██╔╝██║██╔══╝╚════╝██╔═══╝ ██║     ██╔══╝   ██╔██╗ [/]   [bold cyan]║[/]
[bold cyan]║[/]   [bold white]██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗    ██║     ███████╗███████╗██╔╝ ██╗[/]   [bold cyan]║[/]
[bold cyan]║[/]   [bold white]╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝    ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝[/]   [bold cyan]║[/]
[bold cyan]║[/]                                                                      [bold cyan]║[/]
[bold cyan]║[/]              [bold yellow]🎬 Your Personal Media Server Setup 🎬[/]                   [bold cyan]║[/]
[bold cyan]║[/]                                                                      [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════════════╝[/]
"""
    console.print(banner)


def run_command(
    cmd: list[str], sudo: bool = False, capture: bool = False, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command."""
    if sudo and os.geteuid() != 0:
        cmd = ["sudo"] + cmd

    return subprocess.run(cmd, capture_output=capture, text=True, check=check)


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists."""
    result = subprocess.run(["which", cmd], capture_output=True)
    return result.returncode == 0


def get_prowlarr_api_key(config_path: str) -> str | None:
    """Read the actual API key from Prowlarr's config.xml."""
    config_file = Path(config_path) / "prowlarr" / "config.xml"

    if not config_file.exists():
        return None

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(config_file)
        root = tree.getroot()
        api_key_elem = root.find("ApiKey")
        if api_key_elem is not None and api_key_elem.text:
            return api_key_elem.text
    except Exception:
        pass

    return None


def get_configuration() -> Config:
    """Prompt user for configuration values."""
    console.print(
        Panel.fit(
            "[bold magenta]Please provide the following configuration values.\n"
            "[dim]Press ENTER to accept the default value shown.[/]",
            title="[bold white]📌 Configuration[/]",
            border_style="cyan",
        )
    )
    console.print()

    config = Config()

    # User credentials
    config.admin_user = Prompt.ask("  [cyan]➜[/] Admin username", default="admin")
    config.admin_pass = Prompt.ask(
        "  [cyan]➜[/] Admin password", default="admin", password=True
    )

    # API Key
    console.print()
    console.print(
        "  [blue]ℹ[/] An API key is needed for Prowlarr/Sonarr/Radarr integration"
    )
    default_api_key = secrets.token_hex(16)
    config.prowlarr_api_key = Prompt.ask(
        "  [cyan]➜[/] Prowlarr API Key", default=default_api_key
    )

    # Paths
    console.print()
    home = os.path.expanduser("~")
    config.base_data_path = Prompt.ask(
        "  [cyan]➜[/] Media data path", default=f"{home}/DATA"
    )
    config.base_config_path = Prompt.ask(
        "  [cyan]➜[/] App config path", default=f"{home}/appdata"
    )

    # Ports
    console.print()
    console.print("  [blue]ℹ[/] Configure service ports (press ENTER for defaults)")

    config.plex_port = int(Prompt.ask("  [cyan]➜[/] Plex port", default="32400"))
    config.prowlarr_port = int(Prompt.ask("  [cyan]➜[/] Prowlarr port", default="9696"))
    config.flaresolverr_port = int(
        Prompt.ask("  [cyan]➜[/] FlareSolverr port", default="8191")
    )
    config.radarr_port = int(Prompt.ask("  [cyan]➜[/] Radarr port", default="7878"))
    config.sonarr_port = int(Prompt.ask("  [cyan]➜[/] Sonarr port", default="8989"))
    config.qbit_webui_port = int(
        Prompt.ask("  [cyan]➜[/] qBittorrent WebUI port", default="8090")
    )
    config.qbit_port = int(Prompt.ask("  [cyan]➜[/] qBittorrent port", default="6881"))

    return config


def install_dependencies():
    """Install system dependencies."""
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Installing system dependencies...[/]",
            title="[bold white]📦 Dependencies[/]",
            border_style="cyan",
        )
    )
    console.print()

    # Update package lists
    console.print("  [cyan]○[/] Updating package lists...")
    result = subprocess.run(
        ["sudo", "apt-get", "update"], capture_output=True, text=True
    )
    if result.returncode == 0:
        console.print("  [green]✓[/] Package lists updated")
    else:
        console.print("  [yellow]⚠[/] Package update had warnings (continuing...)")

    # Install prerequisites
    console.print("  [cyan]○[/] Installing prerequisites...")
    subprocess.run(
        [
            "sudo",
            "apt-get",
            "install",
            "-y",
            "apt-transport-https",
            "ca-certificates",
            "curl",
            "gnupg",
            "lsb-release",
            "jq",
        ],
        capture_output=True,
    )
    console.print("  [green]✓[/] Prerequisites installed")

    # Install Docker
    if not check_command_exists("docker"):
        console.print("  [cyan]○[/] Installing Docker (this may take a minute)...")
        subprocess.run(
            "curl -fsSL https://get.docker.com | sudo sh",
            shell=True,
            capture_output=True,
        )

        # Add user to docker group
        user = os.environ.get("USER", "")
        if user and user != "root":
            subprocess.run(
                ["sudo", "usermod", "-aG", "docker", user], capture_output=True
            )

        console.print("  [green]✓[/] Docker installed")
    else:
        console.print("  [green]✓[/] Docker already installed")

    # Check Docker Compose
    docker_compose_exists = (
        check_command_exists("docker-compose")
        or subprocess.run(
            ["docker", "compose", "version"], capture_output=True
        ).returncode
        == 0
    )

    if not docker_compose_exists:
        console.print("  [cyan]○[/] Installing Docker Compose...")
        subprocess.run(
            ["sudo", "apt-get", "install", "-y", "docker-compose-plugin"],
            capture_output=True,
        )
        console.print("  [green]✓[/] Docker Compose installed")
    else:
        console.print("  [green]✓[/] Docker Compose already installed")

    console.print()
    console.print("  [bold green]✓ All dependencies installed![/]")


def create_env_file(config: Config, project_dir: Path):
    """Create the .env file."""
    env_content = f"""# ============================================
# HOME-PLEX CONFIGURATION
# Generated by setup.py
# ============================================

# User & Group IDs
PUID={config.puid}
PGID={config.pgid}
TZ=America/Sao_Paulo

# Paths
BASE_DATA_PATH={config.base_data_path}
BASE_CONFIG_PATH={config.base_config_path}

# Credentials
ADMIN_USER={config.admin_user}
ADMIN_PASS={config.admin_pass}

# API Keys
PROWLARR_API_KEY={config.prowlarr_api_key}

# Service Ports
PLEX_PORT={config.plex_port}
PROWLARR_PORT={config.prowlarr_port}
FLARESOLVERR_PORT={config.flaresolverr_port}
RADARR_PORT={config.radarr_port}
SONARR_PORT={config.sonarr_port}
QBIT_WEBUI_PORT={config.qbit_webui_port}
QBIT_PORT={config.qbit_port}
"""

    env_path = project_dir / ".env"
    env_path.write_text(env_content)
    console.print(f"  [green]✓[/] Created [magenta].env[/] file")


def create_directories(config: Config):
    """Create necessary directories."""
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Creating directories...[/]",
            title="[bold white]📁 Directories[/]",
            border_style="cyan",
        )
    )

    data_path = Path(config.base_data_path)
    config_path = Path(config.base_config_path)

    # Data directories
    for subdir in ["media/movies", "media/tv", "torrents/movies", "torrents/tv"]:
        (data_path / subdir).mkdir(parents=True, exist_ok=True)
    console.print(f"  [green]✓[/] Created media directories at [magenta]{data_path}[/]")

    # Config directories
    for app in ["plex", "prowlarr", "radarr", "sonarr", "qbittorrent"]:
        (config_path / app).mkdir(parents=True, exist_ok=True)
    console.print(
        f"  [green]✓[/] Created config directories at [magenta]{config_path}[/]"
    )


def get_docker_compose_cmd() -> list[str]:
    """Get the correct docker compose command for this system."""
    # Try new plugin syntax first
    result = subprocess.run(["docker", "compose", "version"], capture_output=True)
    if result.returncode == 0:
        return ["docker", "compose"]

    # Fall back to old standalone command
    result = subprocess.run(["docker-compose", "version"], capture_output=True)
    if result.returncode == 0:
        return ["docker-compose"]

    # Default to new syntax
    return ["docker", "compose"]


def start_containers(project_dir: Path):
    """Start Docker containers."""
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Starting Docker containers...[/]",
            title="[bold white]🐳 Docker[/]",
            border_style="cyan",
        )
    )

    docker_compose = get_docker_compose_cmd()

    # List of container names to manage
    container_names = [
        "plex",
        "prowlarr",
        "flaresolverr",
        "radarr",
        "sonarr",
        "qbittorrent",
    ]

    # First, forcefully stop and remove any existing containers with these names
    console.print("  [cyan]○[/] Removing existing containers (if any)...")
    for name in container_names:
        subprocess.run(["docker", "stop", name], capture_output=True)
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)

    # Also run docker-compose down to clean up networks
    subprocess.run(
        docker_compose + ["down", "--remove-orphans"],
        cwd=project_dir,
        capture_output=True,
    )
    console.print("  [green]✓[/] Existing containers removed")

    # Now start fresh
    console.print("  [cyan]○[/] Starting containers...")
    result = subprocess.run(
        docker_compose + ["up", "-d"], cwd=project_dir, capture_output=True, text=True
    )

    if result.returncode == 0:
        console.print("  [green]✓[/] Containers started")
    else:
        console.print(f"  [red]✗[/] Error starting containers:")
        console.print(f"      {result.stderr.strip()}")
        raise RuntimeError("Failed to start containers")


def wait_for_service(url: str, name: str, timeout: int = 120) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)

    return False


def wait_for_services(config: Config):
    """Wait for all services to be ready."""
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Waiting for services to start...[/]",
            title="[bold white]⏳ Services[/]",
            border_style="cyan",
        )
    )

    services = [
        ("Prowlarr", f"http://localhost:{config.prowlarr_port}"),
        ("Radarr", f"http://localhost:{config.radarr_port}"),
        ("Sonarr", f"http://localhost:{config.sonarr_port}"),
        ("qBittorrent", f"http://localhost:{config.qbit_webui_port}"),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for name, url in services:
            task = progress.add_task(f"[cyan]Waiting for {name}...", total=None)
            if wait_for_service(url, name):
                progress.update(task, description=f"[green]✓ {name} is ready")
            else:
                progress.update(
                    task,
                    description=f"[yellow]⚠ {name} timeout (may still be starting)",
                )


def configure_prowlarr_flaresolverr(config: Config) -> bool:
    """Configure FlareSolverr in Prowlarr."""
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Configuring Prowlarr with FlareSolverr...[/]",
            title="[bold white]🔧 Prowlarr Configuration[/]",
            border_style="cyan",
        )
    )

    # Read the actual API key from Prowlarr's config.xml
    actual_api_key = get_prowlarr_api_key(config.base_config_path)

    if not actual_api_key:
        console.print("  [yellow]⚠[/] Could not read Prowlarr API key from config")
        console.print("      [dim]Prowlarr may need manual configuration[/]")
        return False

    console.print(f"  [green]✓[/] Found Prowlarr API key: {actual_api_key[:8]}...")

    base_url = f"http://localhost:{config.prowlarr_port}"
    headers = {"X-Api-Key": actual_api_key, "Content-Type": "application/json"}

    # Wait a bit more for Prowlarr to fully initialize
    time.sleep(3)

    try:
        # Create the FlareSolverr tag
        tag_url = f"{base_url}/api/v1/tag"

        response = requests.get(tag_url, headers=headers, timeout=10)
        existing_tags = response.json() if response.status_code == 200 else []
        flaresolverr_tag = next(
            (t for t in existing_tags if t["label"].lower() == "flaresolverr"), None
        )

        if not flaresolverr_tag:
            tag_data = {"label": "flaresolverr"}
            response = requests.post(
                tag_url, headers=headers, json=tag_data, timeout=10
            )
            if response.status_code in [200, 201]:
                flaresolverr_tag = response.json()
                console.print("  [green]✓[/] Created 'flaresolverr' tag")
            else:
                console.print(f"  [yellow]⚠[/] Could not create tag: {response.text}")
                return False
        else:
            console.print("  [blue]ℹ[/] Tag 'flaresolverr' already exists")

        tag_id = flaresolverr_tag["id"]

        # Configure FlareSolverr as an indexer proxy
        proxy_url = f"{base_url}/api/v1/indexerProxy"

        response = requests.get(proxy_url, headers=headers, timeout=10)
        existing_proxies = response.json() if response.status_code == 200 else []
        flaresolverr_proxy = next(
            (
                p
                for p in existing_proxies
                if p.get("name", "").lower() == "flaresolverr"
            ),
            None,
        )

        if flaresolverr_proxy:
            console.print("  [blue]ℹ[/] FlareSolverr proxy already configured")
            return True

        # Create FlareSolverr proxy
        flaresolverr_url = f"http://flaresolverr:{config.flaresolverr_port}"

        proxy_data = {
            "name": "FlareSolverr",
            "implementation": "FlareSolverr",
            "implementationName": "FlareSolverr",
            "configContract": "FlareSolverrSettings",
            "fields": [
                {"name": "host", "value": flaresolverr_url},
                {"name": "requestTimeout", "value": 60},
            ],
            "tags": [tag_id],
        }

        response = requests.post(
            proxy_url, headers=headers, json=proxy_data, timeout=10
        )

        if response.status_code in [200, 201]:
            console.print("  [green]✓[/] FlareSolverr configured as indexer proxy")
            console.print(f"      URL: [yellow]{flaresolverr_url}[/]")
            console.print(f"      Tag: [yellow]flaresolverr[/] (ID: {tag_id})")
            return True
        else:
            console.print(
                f"  [red]✗[/] Failed to configure FlareSolverr: {response.status_code}"
            )
            return False

    except Exception as e:
        console.print(f"  [yellow]⚠[/] Error configuring FlareSolverr: {e}")
        console.print("      [dim]You may need to configure this manually[/]")
        return False


def print_summary(config: Config):
    """Print the final summary."""
    console.print()

    # Configuration summary table
    table = Table(title="Configuration Summary", box=box.ROUNDED, border_style="cyan")
    table.add_column("Setting", style="white")
    table.add_column("Value", style="magenta")

    table.add_row("Admin User", config.admin_user)
    table.add_row("Data Path", config.base_data_path)
    table.add_row("Config Path", config.base_config_path)
    table.add_row("API Key", f"{config.prowlarr_api_key[:8]}...")

    console.print(table)
    console.print()

    # Services table
    services_table = Table(title="Service URLs", box=box.ROUNDED, border_style="cyan")
    services_table.add_column("Service", style="white")
    services_table.add_column("URL", style="yellow")

    services_table.add_row("Plex", f"http://localhost:{config.plex_port}/web")
    services_table.add_row("Prowlarr", f"http://localhost:{config.prowlarr_port}")
    services_table.add_row("Radarr", f"http://localhost:{config.radarr_port}")
    services_table.add_row("Sonarr", f"http://localhost:{config.sonarr_port}")
    services_table.add_row("qBittorrent", f"http://localhost:{config.qbit_webui_port}")
    services_table.add_row(
        "FlareSolverr", f"http://localhost:{config.flaresolverr_port}"
    )

    console.print(services_table)
    console.print()

    console.print(
        Panel.fit(
            "[bold green]✓ Installation Complete![/]\n\n"
            "[white]Your home media server is now running.[/]\n"
            "[dim]Enjoy your movies and TV shows! 🎬[/]",
            border_style="green",
        )
    )


def main():
    """Main entry point."""
    # Get project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    # Clear screen and show banner
    console.clear()
    print_banner()

    # Get configuration
    config = get_configuration()

    # Install dependencies
    install_dependencies()

    # Create environment file
    console.print()
    console.print(
        Panel.fit(
            "[bold white]Creating configuration files...[/]",
            title="[bold white]⚙️ Configuration[/]",
            border_style="cyan",
        )
    )
    create_env_file(config, project_dir)

    # Create directories
    create_directories(config)

    # Start containers
    start_containers(project_dir)

    # Wait for services
    wait_for_services(config)

    # Configure Prowlarr with FlareSolverr
    configure_prowlarr_flaresolverr(config)

    # Print summary
    print_summary(config)


if __name__ == "__main__":
    main()
