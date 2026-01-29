from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Input, Button, Checkbox, RichLog
from textual.binding import Binding
from .core import search_parallel

class SearchApp(App):
    CSS = """
    Screen { layout: grid; grid-size: 1 2; grid-rows: auto 1fr; }
    Container { padding: 1; border: solid green; height: auto; }
    #input-container { layout: grid; grid-size: 2 3; grid-columns: 1fr 1fr; gap: 1; height: auto; }
    Input { width: 100%; }
    Button { width: 100%; }
    RichLog { border: solid white; background: $surface; }
    """
    BINDINGS = [Binding("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="input-container"):
            yield Input(placeholder="Directory Path (e.g., .)", id="dir_input")
            yield Input(placeholder="Regex Pattern (e.g., Invoice)", id="pat_input")
            yield Checkbox("Recursive Search", value=True, id="chk_recursive")
            yield Checkbox("Ignore Case", value=True, id="chk_case")
            with Horizontal():
                yield Button("Start Search", id="btn_search", variant="success")
                yield Button("Clear Log", id="btn_clear", variant="error")
        yield RichLog(id="results_log", highlight=True, markup=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_search":
            self.run_search()
        elif event.button.id == "btn_clear":
            self.query_one("#results_log").clear()

    def run_search(self) -> None:
        directory = self.query_one("#dir_input", Input).value
        pattern = self.query_one("#pat_input", Input).value
        recursive = self.query_one("#chk_recursive", Checkbox).value
        ignore_case = self.query_one("#chk_case", Checkbox).value
        log = self.query_one("#results_log", RichLog)

        if not directory or not pattern:
            log.write("[bold red]Error:[/bold red] Please enter directory and pattern.")
            return

        log.write(f"[bold yellow]Searching...[/bold yellow] '{pattern}' in '{directory}'")
        try:
            count = 0
            for event, data in search_parallel(directory, pattern, ignore_case, recursive, verbose=False):
                if event == "match":
                    log.write(f"[green]Match:[/green] {data}")
                    count += 1
            log.write(f"[bold blue]Done.[/bold blue] Found {count} files.\n")
        except Exception as e:
            log.write(f"[bold red]Error:[/bold red] {e}")

def start_tui():
    app = SearchApp()
    app.run()
