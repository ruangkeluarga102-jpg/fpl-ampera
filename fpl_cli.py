import sys
import os
import argparse
from typing import Optional

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fpl_api import FPLApiClient
from fpl_analytics import FPLMiniLeagueAnalyzer
from exporter import FPLExporter

def run_cli():
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        from rich import box
    except ImportError:
        print("Rich library not found. Please install it using: pip install rich")
        return

    console = Console(highlight=False)
    console.print(Panel.fit(
        "[bold cyan]⚽ FPL Mini-League Data Extractor & Analytics[/bold cyan]\n"
        "[dim]Tarik data klasemen, kapten, kepemilikan pemain (EO), dan chip mini-league secara instan.[/dim]",
        border_style="magenta"
    ))

    parser = argparse.ArgumentParser(description="FPL Mini-League Data Extractor")
    parser.add_argument("--league", "-l", type=int, help="Mini-League ID (misal: 123456)")
    parser.add_argument("--gw", "-g", type=int, help="Gameweek (default: Gameweek saat ini)")
    parser.add_argument("--export", "-e", choices=["excel", "csv", "both"], default="excel", help="Format ekspor (excel/csv/both)")
    parser.add_argument("--limit", type=int, default=None, help="Batasi jumlah manajer teratas")
    
    args = parser.parse_args()

    api = FPLApiClient()

    # Get league ID
    league_id = args.league
    if not league_id:
        try:
            val = console.input("[bold yellow]➤ Masukkan League ID FPL [default: 1004418]: [/bold yellow]").strip()
            if not val:
                league_id = 1004418
            else:
                league_id = int(val)
        except ValueError:
            console.print("[red]League ID harus berupa angka![/red]")
            return

    # Determine gameweek
    current_gw = api.get_current_gameweek()
    gameweek = args.gw
    if not gameweek:
        gw_input = console.input(f"[bold yellow]➤ Masukkan Gameweek [default: GW{current_gw}]: [/bold yellow]").strip()
        gameweek = int(gw_input) if gw_input.isdigit() else current_gw

    console.print(f"\n[cyan]Menghubungi FPL API untuk League ID: [bold]{league_id}[/bold] (GW{gameweek})...[/cyan]")

    analyzer = FPLMiniLeagueAnalyzer(api)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Mengambil & Memproses Data Manajer...", total=100)

        def update_progress(curr, total):
            pct = int((curr / total) * 100) if total > 0 else 0
            progress.update(task, completed=pct, description=f"[cyan]Mengambil squad manajer ({curr}/{total})...")

        try:
            data = analyzer.fetch_full_league_data(
                league_id=league_id, 
                gameweek=gameweek, 
                max_entries=args.limit,
                progress_callback=update_progress
            )
            progress.update(task, completed=100, description="[green]Selesai!")
        except Exception as e:
            console.print(f"[bold red]Gagal mengambil data mini-league:[/bold red] {e}")
            return

    league_name = data.get("league_info", {}).get("name", f"League #{league_id}")
    total_mgrs = data.get("total_managers", 0)

    console.print(Panel(
        f"[bold green]🏆 Liga: {league_name}[/bold green]\n"
        f"👥 Total Manajer: [bold]{total_mgrs}[/bold] | 📅 Gameweek: [bold]GW{gameweek}[/bold]",
        title="Ringkasan Mini-League",
        border_style="green"
    ))

    # 1. Standings Table
    standings_df = data.get("standings_df")
    if standings_df is not None and not standings_df.empty:
        table = Table(title=f"🏆 Klasemen Mini-League GW{gameweek}", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Rank", justify="center", style="cyan")
        table.add_column("Move", justify="center")
        table.add_column("Team Name", style="bold white")
        table.add_column("Manager", style="white")
        table.add_column("GW Pts", justify="right", style="green")
        table.add_column("Total Pts", justify="right", style="bold yellow")
        table.add_column("Captain (GW)", style="bright_cyan")
        table.add_column("Active Chip", justify="center", style="red")
        table.add_column("Hits", justify="right", style="dim red")

        for _, row in standings_df.head(20).iterrows():
            table.add_row(
                str(row["Rank"]),
                str(row["Move"]),
                str(row["Team Name"]),
                str(row["Manager"]),
                str(row["GW Points"]),
                str(row["Total Points"]),
                str(row["Captain"]),
                str(row["Active Chip"]),
                str(row["Transfer Cost"])
            )
        console.print(table)
        if len(standings_df) > 20:
            console.print(f"[dim](Menampilkan 20 dari {len(standings_df)} manajer. Lihat file Excel untuk data lengkap)[/dim]\n")

    # 2. Captaincy Summary
    captaincy_df = data.get("captaincy_df")
    if captaincy_df is not None and not captaincy_df.empty:
        cap_table = Table(title="👑 Pilihan Kapten Terbanyak", box=box.SIMPLE_HEAVY, header_style="bold yellow")
        cap_table.add_column("Pemain", style="bold white")
        cap_table.add_column("Dipilih (Manajer)", justify="right", style="green")
        cap_table.add_column("% di Liga", justify="right", style="cyan")

        for _, row in captaincy_df.head(8).iterrows():
            cap_table.add_row(str(row["Captain"]), str(row["Count"]), f"{row['% of League']}%")
        console.print(cap_table)

    # 3. Ownership / Effective Ownership Top 10
    ownership_df = data.get("ownership_df")
    if ownership_df is not None and not ownership_df.empty:
        own_table = Table(title="📊 Top 10 Effective Ownership (EO) di Mini-League", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        own_table.add_column("Pemain", style="bold white")
        own_table.add_column("Klub", justify="center")
        own_table.add_column("Pos", justify="center")
        own_table.add_column("Harga", justify="right")
        own_table.add_column("League Own %", justify="right", style="yellow")
        own_table.add_column("Effective Own % (EO)", justify="right", style="bold green")
        own_table.add_column("Captain", justify="right")

        for _, row in ownership_df.head(10).iterrows():
            own_table.add_row(
                str(row["Player"]),
                str(row["Team"]),
                str(row["Pos"]),
                f"£{row['Cost (£m)']:.1f}",
                f"{row['League Own %']}%",
                f"{row['Effective Own % (EO)']}%",
                str(row["Captain Count"])
            )
        console.print(own_table)

    # Export Process
    exporter = FPLExporter(data)
    if args.export in ("excel", "both"):
        excel_path = exporter.export_to_excel()
        console.print(f"[bold green]✔ Sukses mengekspor ke Excel:[/bold green] [underline]{excel_path}[/underline]")

    if args.export in ("csv", "both"):
        csv_path = exporter.export_to_csv()
        console.print(f"[bold green]✔ Sukses mengekspor ke CSV:[/bold green] [underline]{csv_path}[/underline]")

    console.print("\n[dim]Tips: Jalankan 'streamlit run app.py' untuk membuka Dashboard Web Interaktif yang lengkap![/dim]\n")

if __name__ == "__main__":
    run_cli()
