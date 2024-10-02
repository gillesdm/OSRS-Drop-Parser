from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import DOUBLE
from rich.style import Style
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

def create_header():
    return Panel("OSRS Scraper by @demuynckgilles", border_style="bold green")

def create_layout():
    layout = Layout()
    layout.split(
        Layout(name="title", size=3),
        Layout(name="main", ratio=1),
        Layout(name="progress", size=5)
    )
    layout["main"].split_row(
        Layout(name="drops", ratio=1),
        Layout(name="monsters", ratio=1)
    )
    layout["progress"].split_row(
        Layout(name="drop_progress", ratio=1),
        Layout(name="monster_progress", ratio=1)
    )
    return layout

def update_monsters_panel(monsters_list, console_height, layout):
    panel_height = console_height - layout["title"].size - layout["progress"].size - 2
    return Panel(
        Group(monsters_list),
        title="Monsters",
        border_style="blue",
        height=panel_height,
        expand=True
    )

def create_progress_bars():
    progress_monsters = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.completed]{task.completed:>3}/{task.total}"),
        TimeRemainingColumn()
    )
    progress_drops = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.completed]{task.completed:>3}/{task.total}")
    )
    return progress_monsters, progress_drops

def create_drops_table(drops):
    drops_table = Table(title="Drop Table", box=DOUBLE, border_style="yellow", header_style="bold yellow")
    drops_table.add_column("Item", style="green")
    drops_table.add_column("ID", style="cyan")
    
    if drops:
        for drop, item_id in drops:
            id_str = str(item_id) if item_id is not None else "Not found"
            id_style = "cyan" if item_id is not None else "red"
            drops_table.add_row(drop, id_str, style=Style(color="green", dim=(item_id is None)))
    else:
        drops_table.add_row("No drops found", "N/A", style="red")
    
    return drops_table
