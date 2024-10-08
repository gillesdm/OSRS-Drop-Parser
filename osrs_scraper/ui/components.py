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
from rich.live import Live
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
    welcome_text.append("When searching by category, you can enter a number to quickly select from the example categories.\n\n")
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
        input_text.append("You can find all valid categories at:\n", style="cyan")
        input_text.append("https://oldschool.runescape.wiki/w/Special:Categories\n\n", style="bold blue underline")
        input_text.append("Warning: Not all categories will contain item drops.\n\n", style="bold yellow")
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
    user_input = Prompt.ask(input_type.capitalize())
    
    # Simulating a redirect (you'll need to implement the actual redirect check)
    redirected_name = check_redirect(user_input)
    if redirected_name and redirected_name.lower() != user_input.lower():
        warning_panel = create_warning_panel(user_input, redirected_name)
        with Live(warning_panel, console=console, refresh_per_second=10) as live:
            console.input()  # Wait for user input to continue
        return redirected_name
    
    return user_input

def check_redirect(name: str) -> str:
    # This is a placeholder function. You need to implement the actual redirect check
    # using your wiki API or other means to determine if a search is redirected.
    # For now, it just returns the input name.
    return name

def create_warning_panel(original_name: str, redirected_name: str) -> Panel:
    warning_text = Text()
    warning_text.append("Search redirected\n\n", style="bold yellow")
    warning_text.append(f"Your search for ", style="yellow")
    warning_text.append(f"'{original_name}' ", style="bold white")
    warning_text.append(f"was redirected to ", style="yellow")
    warning_text.append(f"'{redirected_name}'", style="bold white")
    warning_text.append("\n\nPress any key to continue...", style="italic cyan")
    
    return Panel(
        warning_text,
        title="[bold yellow]Search Redirected",
        border_style="yellow",
        expand=False,
        padding=(1, 1)
    )

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

def create_summary_message(search_type: str, search_input: str, monsters: list, total_items: int, file_path: str, args) -> Panel:
    summary_text = Text()
    summary_text.append("Search Complete!\n\n", style="bold green")
    
    if search_type == "category":
        summary_text.append(f"Category: ", style="cyan")
        summary_text.append(f"{search_input}\n", style="bold white")
        summary_text.append(f"Monsters scanned: ", style="cyan")
        summary_text.append(f"{len(monsters)}\n", style="bold white")
    else:
        summary_text.append(f"Monster: ", style="cyan")
        summary_text.append(f"{search_input}\n", style="bold white")
    
    summary_text.append(f"Total items found: ", style="cyan")
    summary_text.append(f"{total_items}\n\n", style="bold white")
    
    summary_text.append("Files saved:\n", style="yellow")
    if args.id and not args.banklayout:
        summary_text.append(f"- Item IDs: ", style="green")
        summary_text.append(f"{file_path.rsplit('.', 1)[0]}_ids.txt\n", style="italic white")
    if args.banklayout:
        summary_text.append(f"- RuneLite bank layout: ", style="green")
        summary_text.append(f"{file_path.rsplit('.', 1)[0]}_banklayout.txt\n", style="italic white")
    if not args.id and not args.banklayout:
        summary_text.append(f"- Drop tables: ", style="green")
        summary_text.append(f"{file_path}\n", style="italic white")
    
    return Panel(summary_text, title="Summary", border_style="bold blue", expand=False, padding=(1, 1))

def ask_for_another_search(console: Console) -> bool:
    options = ["Yes, do another search", "No, exit the tool"]
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

    console.print("\nDo you want to do another search?", style="bold cyan")
    
    application = Application(
        layout=Layout(Window(FormattedTextControl(get_formatted_text))),
        key_bindings=kb,
        full_screen=True,
    )

    result = application.run()
    return result == "Yes, do another search"
