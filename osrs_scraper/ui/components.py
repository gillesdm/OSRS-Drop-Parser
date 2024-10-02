from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import DOUBLE
from rich.style import Style
from rich.columns import Columns
from rich.prompt import Prompt
from art import text2art

def create_welcome_screen(console: Console) -> Panel:
    welcome_text = Text()
    title_art = text2art("Drops", font="block", chr_ignore=True)
    welcome_text.append(title_art + "\n", style="bold magenta")
    welcome_text.append("Welcome to the OSRS Wiki Category Search Tool!\n\n", style="bold green")
    welcome_text.append("This tool allows you to search for monsters in a specific category and retrieve their drop tables.\n\n")
    welcome_text.append("Some example categories you can try:\n", style="cyan")
    welcome_text.append("- Monsters\n")
    welcome_text.append("- Slayer monsters\n")
    welcome_text.append("- Boss monsters\n")
    welcome_text.append("- Wilderness monsters\n\n")
    welcome_text.append("Press Enter to continue...", style="bold yellow")
    
    return Panel(welcome_text, title="Welcome", border_style="bold blue", expand=True, height=console.height)

def get_category_input(console: Console) -> str:
    category_input_text = Text()
    category_input_text.append("Enter the OSRS Wiki category to search:\n\n", style="bold cyan")
    category_input_text.append("Some example categories:\n", style="cyan")
    category_input_text.append("- Monsters\n")
    category_input_text.append("- Slayer monsters\n")
    category_input_text.append("- Boss monsters\n")
    category_input_text.append("- Wilderness monsters\n\n")

    category_panel = Panel(
        category_input_text,
        title="Category Input",
        border_style="bold blue",
        expand=True,
        height=console.height
    )

    console.print(category_panel)
    return Prompt.ask("Category")

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
