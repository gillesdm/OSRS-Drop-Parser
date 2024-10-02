from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text

def create_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="title", size=3),
        Layout(name="steps", size=3),
        Layout(name="main", ratio=1),
        Layout(name="progress", size=5)
    )
    layout["main"].split_row(
        Layout(name="left_column", ratio=1),
        Layout(name="right_column", ratio=1)
    )
    layout["left_column"].split(
        Layout(name="monster_search", size=3),
        Layout(name="monsters", ratio=1)
    )
    layout["right_column"].split(
        Layout(name="drops", ratio=1)
    )
    layout["progress"].split_row(
        Layout(name="drop_progress", ratio=1),
        Layout(name="monster_progress", ratio=1)
    )
    return layout

def create_header() -> Panel:
    return Panel("OSRS Scraper by @demuynckgilles", border_style="bold green")

def create_steps_panel(current_step: int) -> Panel:
    steps = [
        "1. Looking for monsters",
        "2. Fetching drops",
        "3. Saving data"
    ]
    step_renderable = "\n".join([
        f"[{'green' if i + 1 <= current_step else 'dim'}]{step}[/]"
        for i, step in enumerate(steps)
    ])
    return Panel(step_renderable, title="Progress", border_style="cyan", expand=True)

def create_monster_search_panel(progress: float) -> Panel:
    return Panel(f"Checking for monsters... {progress:.1f}%", title="Monster Search", border_style="cyan")

def update_monsters_panel(monsters_list: str, console_height: int, layout: Layout) -> Panel:
    panel_height = console_height - layout["title"].size - layout["progress"].size - 2
    return Panel(monsters_list, title="Monsters", border_style="blue", height=panel_height, expand=True)

def create_progress_bar() -> Progress:
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.completed]{task.completed:>3}/{task.total}")
    )

def update_layout(layout: Layout, category: str, monsters: list, console_height: int, current_monster: str = None, drops_table = None) -> None:
    layout["title"].update(create_header())
    layout["steps"].update(create_steps_panel(2 if current_monster else 1))
    
    if not monsters:
        layout["monster_search"].update(Panel(f"[red]No monsters found in the category '{category}'.[/red]", title="Monster Search", border_style="cyan"))
        return
    
    layout["monster_search"].update(Panel(f"Found {len(monsters)} monsters", title="Monster Search", border_style="cyan"))
    
    monsters_list = "\n".join(["✓ " + m if m == current_monster else m for m in monsters])
    monsters_panel = update_monsters_panel(monsters_list, console_height, layout)
    layout["monsters"].update(monsters_panel)
    
    if drops_table:
        layout["drops"].update(Panel(drops_table, title=f"Drops for {current_monster}", border_style="yellow"))
