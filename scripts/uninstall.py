#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///
"""
Home-Plex Uninstaller
Removes containers, images, and optionally data/config directories.
"""

import os
import subprocess
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

console = Console()


def load_env() -> dict[str, str]:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars


def print_banner():
    """Display the uninstall banner."""
    banner = """
[bold red]╔══════════════════════════════════════════════════════════════════════╗[/]
[bold red]║[/]                                                                      [bold red]║[/]
[bold red]║[/]   [bold white]🗑️  HOME-PLEX UNINSTALLER[/]                                          [bold red]║[/]
[bold red]║[/]                                                                      [bold red]║[/]
[bold red]╚══════════════════════════════════════════════════════════════════════╝[/]
"""
    console.print(banner)


def get_container_status() -> list[tuple[str, str, str]]:
    """Get status of home-plex containers."""
    containers = ["plex", "prowlarr", "flaresolverr", "radarr", "sonarr", "qbittorrent"]
    statuses = []

    for name in containers:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            status = result.stdout.strip()
            statuses.append((name, status, "exists"))
        else:
            statuses.append((name, "not found", "missing"))

    return statuses


def main():
    """Main entry point."""
    project_dir = Path(__file__).parent.parent
    env_vars = load_env()

    console.clear()
    print_banner()

    # Show current status
    console.print(
        Panel.fit(
            "[bold white]Checking current installation...[/]",
            title="[bold white]📊 Status[/]",
            border_style="cyan",
        )
    )
    console.print()

    statuses = get_container_status()

    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Container", style="white")
    table.add_column("Status", style="white")

    for name, status, _ in statuses:
        if status == "running":
            table.add_row(name, f"[green]● {status}[/]")
        elif status == "not found":
            table.add_row(name, f"[dim]○ {status}[/]")
        else:
            table.add_row(name, f"[yellow]○ {status}[/]")

    console.print(table)
    console.print()

    # Confirm uninstall
    console.print(
        Panel.fit(
            "[bold yellow]⚠️  Warning: This will stop and remove all Home-Plex containers![/]",
            border_style="yellow",
        )
    )
    console.print()

    if not Confirm.ask("  [cyan]➜[/] Do you want to continue?", default=False):
        console.print("  [dim]Uninstall cancelled.[/]")
        return

    console.print()

    # Stop and remove containers
    console.print(
        Panel.fit(
            "[bold white]Removing containers...[/]",
            title="[bold white]🐳 Docker Cleanup[/]",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Stop containers
        task = progress.add_task("[cyan]Stopping containers...", total=None)
        subprocess.run(
            ["docker", "compose", "down"], cwd=project_dir, capture_output=True
        )
        progress.update(task, description="[green]✓ Containers stopped")

        # Remove volumes
        task = progress.add_task("[cyan]Removing volumes...", total=None)
        subprocess.run(
            ["docker", "compose", "down", "-v"], cwd=project_dir, capture_output=True
        )
        progress.update(task, description="[green]✓ Volumes removed")

    console.print()

    # Ask about removing images
    if Confirm.ask("  [cyan]➜[/] Remove Docker images too?", default=False):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Removing images...", total=None)

            images = [
                "lscr.io/linuxserver/plex",
                "lscr.io/linuxserver/prowlarr",
                "lscr.io/linuxserver/radarr",
                "lscr.io/linuxserver/sonarr",
                "lscr.io/linuxserver/qbittorrent",
                "ghcr.io/flaresolverr/flaresolverr",
            ]

            for image in images:
                subprocess.run(["docker", "rmi", image], capture_output=True)

            progress.update(task, description="[green]✓ Images removed")

    console.print()

    # Ask about removing data directories
    data_path = env_vars.get("BASE_DATA_PATH", os.path.expanduser("~/DATA"))
    config_path = env_vars.get("BASE_CONFIG_PATH", os.path.expanduser("~/appdata"))

    console.print(
        Panel.fit(
            f"[bold yellow]Data directories:[/]\n"
            f"  • {data_path}\n"
            f"  • {config_path}",
            title="[bold white]📁 Data Cleanup[/]",
            border_style="yellow",
        )
    )
    console.print()

    if Confirm.ask(
        "  [red]➜[/] [bold red]DELETE all data and config directories?[/]",
        default=False,
    ):
        console.print()
        if Confirm.ask(
            "  [red]➜[/] [bold red]Are you REALLY sure? This cannot be undone![/]",
            default=False,
        ):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:

                task = progress.add_task(
                    "[cyan]Removing data directories...", total=None
                )

                if Path(data_path).exists():
                    shutil.rmtree(data_path, ignore_errors=True)
                if Path(config_path).exists():
                    shutil.rmtree(config_path, ignore_errors=True)

                progress.update(task, description="[green]✓ Data directories removed")

            console.print("  [green]✓[/] Data directories deleted")
        else:
            console.print("  [dim]Keeping data directories.[/]")
    else:
        console.print("  [dim]Keeping data directories.[/]")

    console.print()

    # Remove .env file
    env_file = project_dir / ".env"
    if env_file.exists():
        if Confirm.ask("  [cyan]➜[/] Remove .env configuration file?", default=True):
            env_file.unlink()
            console.print("  [green]✓[/] .env file removed")

    console.print()
    console.print(
        Panel.fit(
            "[bold green]✓ Uninstall Complete![/]\n\n"
            "[white]Home-Plex has been removed from your system.[/]\n"
            "[dim]Run ./install.sh to reinstall anytime.[/]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
