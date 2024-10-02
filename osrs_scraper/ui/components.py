from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import DOUBLE
from rich.style import Style
from rich.columns import Columns
from rich.prompt import Prompt
from rich.console import Group
from rich.padding import Padding
from art import text2art
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout

def create_welcome_screen(console: Console) -> Panel:
    welcome_text = Text()
    title_art = text2art("Drops", font="block", chr_ignore=True)
    welcome_text.append(title_art + "\n", style="bold magenta")
    welcome_text.append("Welcome to the OSRS Wiki Search Tool!\n\n", style="bold green")
    welcome_text.append("This tool allows you to search for monsters in a specific category or get drops for a specific monster.\n\n")
    welcome_text.append("Press Enter to continue...", style="bold yellow")
    
    return Panel(welcome_text, title="Welcome", border_style="bold blue", expand=True, height=console.height)

def get_search_type() -> str:
    options = ["Search by Category", "Search by Monster"]
    selected = 0

    def get_formatted_text():
        result = []
        for i, option in enumerate(options):
            if i == selected:
                result.append(("class:selected", f">> {option}"))
            else:
                result.append(("", f"   {option}"))
            result.append(("", "\n"))
        return result

    kb = KeyBindings()

    @kb.add("up")
    def _(event):
        nonlocal selected
        selected = (selected - 1) % len(options)

    @kb.add("down")
    def _(event):
        nonlocal selected
        selected = (selected + 1) % len(options)

    @kb.add("enter")
    def _(event):
        event.app.exit(result=options[selected])

    application = Application(
        layout=Layout(Window(FormattedTextControl(get_formatted_text))),
        key_bindings=kb,
        full_screen=True,
    )

    result = application.run()
    return "category" if result == "Search by Category" else "monster"

def get_input(console: Console, input_type: str) -> str:
    input_text = Text()
    input_text.append(f"Enter the OSRS Wiki {input_type} to search:\n\n", style="bold cyan")
    
    if input_type == "category":
        input_text.append("Some example categories:\n", style="cyan")
        input_text.append("- Monsters\n")
        input_text.append("- Slayer monsters\n")
        input_text.append("- Boss monsters\n")
        input_text.append("- Wilderness monsters\n\n")
    else:
        input_text.append("Enter the name of the monster (e.g., 'Zulrah', 'Abyssal demon'):\n\n")

    input_panel = Panel(
        input_text,
        title=f"{input_type.capitalize()} Input",
        border_style="bold blue",
        expand=True,
        height=console.height
    )

    console.print(input_panel)
    return Prompt.ask(input_type.capitalize())

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
