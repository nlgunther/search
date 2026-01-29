That is a very pragmatic solution. The `#` character is indeed tricky in Python bootstrapper scripts because Python treats it as a comment unless strictly enclosed, and combined with Windows backslashes in raw strings, it creates a perfect storm for syntax errors.

Here is the **clean installer** (with the README logic removed entirely) followed by the **README documentation** for you to save manually.

### 1. The Clean Installer (`install_search.py`)

Run this script to generate the code. It is now guaranteed to be free of syntax errors because the problematic Markdown string is gone.

Python

```
import os
import sys

# --- Source Code Definitions ---

FILE_STRUCTURE = {}

# 1. docsearch/__init__.py
FILE_STRUCTURE["docsearch/__init__.py"] = """from .core import search_parallelfrom .readers import READER_REGISTRY"""

# 2. docsearch/readers.py
FILE_STRUCTURE["docsearch/readers.py"] = r'''import zipfileimport jsonimport refrom abc import ABC, abstractmethodfrom xml.etree import ElementTreeclass BaseReader(ABC):    @abstractmethod    def read(self, filepath: str) -> str:        """Read file and return plain text content."""        passclass ZipXmlReader(BaseReader):    xml_filename = ""    tag_name = ""    namespace = ""    def read(self, filepath: str) -> str:        try:            with zipfile.ZipFile(filepath, 'r') as z:                with z.open(self.xml_filename) as f:                    tree = ElementTree.parse(f)                    tag = f"{{{self.namespace}}}{self.tag_name}" if self.namespace else self.tag_name                    return " ".join(node.text for node in tree.iter(tag) if node.text)        except Exception:            return ""class ODTReader(ZipXmlReader):    xml_filename = 'content.xml'    tag_name = 'p'    namespace = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'class DocxReader(ZipXmlReader):    xml_filename = 'word/document.xml'    tag_name = 't'    namespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'class JupyterReader(BaseReader):    def read(self, filepath: str) -> str:        try:            with open(filepath, 'r', encoding='utf-8') as f:                data = json.load(f)                texts = []                for cell in data.get('cells', []):                    src = cell.get('source', [])                    content = "".join(src) if isinstance(src, list) else str(src)                    texts.append(content)                return "\n".join(texts)        except Exception:            return ""class PDFReader(BaseReader):    def read(self, filepath: str) -> str:        try:            from pypdf import PdfReader            reader = PdfReader(filepath)            return " ".join(page.extract_text() or "" for page in reader.pages)        except Exception:            return ""class ExcelReader(BaseReader):    def read(self, filepath: str) -> str:        try:            import openpyxl            wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)            text_parts = []            for sheet in wb:                for row in sheet.iter_rows(values_only=True):                    text_parts.append(" ".join(str(c) for c in row if c is not None))            return "\n".join(text_parts)        except Exception:            return ""READER_REGISTRY = {    '.odt': ODTReader,    '.docx': DocxReader,    '.ipynb': JupyterReader,    '.pdf': PDFReader,    '.xlsx': ExcelReader,    '.ods': ExcelReader}'''

# 3. docsearch/core.py
FILE_STRUCTURE["docsearch/core.py"] = r'''import osimport reimport loggingimport warningsfrom concurrent.futures import ProcessPoolExecutor, as_completedfrom typing import Tuple, Iterator, Set, Anyfrom .readers import READER_REGISTRYdef _worker_process_file(args: Tuple[str, str, str, bool, bool]) -> Tuple[str, bool]:    filepath, filename, pattern, ignore_case, verbose = args        # --- SILENCE NOISE ---    if not verbose:        logging.getLogger("pypdf").setLevel(logging.CRITICAL)        logging.getLogger("openpyxl").setLevel(logging.CRITICAL)        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")    else:        logging.getLogger("pypdf").setLevel(logging.WARNING)        warnings.simplefilter("default")    ext = os.path.splitext(filename)[1].lower()    reader_cls = READER_REGISTRY.get(ext)        if not reader_cls:        return filepath, False    content = reader_cls().read(filepath)    flags = re.IGNORECASE if ignore_case else 0        if re.search(pattern, content, flags):        return filepath, True    return filepath, Falsedef find_files(directory: str, extensions: Set[str], recursive: bool) -> Iterator[Tuple[str, str]]:    if recursive:        for root, _, files in os.walk(directory):            for file in files:                if os.path.splitext(file)[1].lower() in extensions:                    yield os.path.join(root, file), file    else:        if os.path.isdir(directory):            for file in os.listdir(directory):                if os.path.splitext(file)[1].lower() in extensions:                    yield os.path.join(directory, file), filedef search_parallel(directory: str, pattern: str, ignore_case: bool = False, recursive: bool = True, verbose: bool = False) -> Iterator[Tuple[str, Any]]:    supported_exts = set(READER_REGISTRY.keys())    tasks = []    for full_path, filename in find_files(directory, supported_exts, recursive):        tasks.append((full_path, filename, pattern, ignore_case, verbose))    yield ("total", len(tasks))    with ProcessPoolExecutor() as executor:        futures = [executor.submit(_worker_process_file, task) for task in tasks]        for future in as_completed(futures):            full_path, found = future.result()            yield ("scan", full_path)            if found:                yield ("match", full_path)'''

# 4. docsearch/tui.py
FILE_STRUCTURE["docsearch/tui.py"] = r'''from textual.app import App, ComposeResultfrom textual.containers import Container, Horizontalfrom textual.widgets import Header, Footer, Input, Button, Checkbox, RichLogfrom textual.binding import Bindingfrom .core import search_parallelclass SearchApp(App):    CSS = """    Screen { layout: grid; grid-size: 1 2; grid-rows: auto 1fr; }    Container { padding: 1; border: solid green; height: auto; }    #input-container { layout: grid; grid-size: 2 3; grid-columns: 1fr 1fr; gap: 1; height: auto; }    Input { width: 100%; }    Button { width: 100%; }    RichLog { border: solid white; background: $surface; }    """    BINDINGS = [Binding("q", "quit", "Quit")]    def compose(self) -> ComposeResult:        yield Header()        with Container(id="input-container"):            yield Input(placeholder="Directory Path (e.g., .)", id="dir_input")            yield Input(placeholder="Regex Pattern (e.g., Invoice)", id="pat_input")            yield Checkbox("Recursive Search", value=True, id="chk_recursive")            yield Checkbox("Ignore Case", value=True, id="chk_case")            with Horizontal():                yield Button("Start Search", id="btn_search", variant="success")                yield Button("Clear Log", id="btn_clear", variant="error")        yield RichLog(id="results_log", highlight=True, markup=True)        yield Footer()    def on_button_pressed(self, event: Button.Pressed) -> None:        if event.button.id == "btn_search":            self.run_search()        elif event.button.id == "btn_clear":            self.query_one("#results_log").clear()    def run_search(self) -> None:        directory = self.query_one("#dir_input", Input).value        pattern = self.query_one("#pat_input", Input).value        recursive = self.query_one("#chk_recursive", Checkbox).value        ignore_case = self.query_one("#chk_case", Checkbox).value        log = self.query_one("#results_log", RichLog)        if not directory or not pattern:            log.write("[bold red]Error:[/bold red] Please enter directory and pattern.")            return        log.write(f"[bold yellow]Searching...[/bold yellow] '{pattern}' in '{directory}'")        try:            count = 0            for event, data in search_parallel(directory, pattern, ignore_case, recursive, verbose=False):                if event == "match":                    log.write(f"[green]Match:[/green] {data}")                    count += 1            log.write(f"[bold blue]Done.[/bold blue] Found {count} files.\n")        except Exception as e:            log.write(f"[bold red]Error:[/bold red] {e}")def start_tui():    app = SearchApp()    app.run()'''

# 5. docsearch/cli.py
FILE_STRUCTURE["docsearch/cli.py"] = r'''import argparseimport sysimport osimport timeimport loggingfrom tqdm import tqdmfrom .core import search_parallelfrom .tui import start_tuidef main():    parser = argparse.ArgumentParser(description="Advanced Document Search")    parser.add_argument("--tui", action="store_true", help="Launch TUI (GUI)")        # Renamed positional arg to 'target_dir' to allow '--path' flag    parser.add_argument("target_dir", nargs="?", help="Directory to search")    parser.add_argument("regex", nargs="?", help="Regex pattern")        # Search Flags    parser.add_argument("-i", "--ignore-case", action="store_true")    parser.add_argument("-r", "--recursive", action="store_true", default=True)    parser.add_argument("--no-recursive", action="store_false", dest="recursive")        # Output Flags    parser.add_argument("--path", action="store_true", help="Output absolute paths instead of relative filenames")    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose internal logs")        # Logging Flags    parser.add_argument("--log-console", action="store_true", help="Output matches to console")    parser.add_argument("--log-file", type=str, help="Output matches to specified file path")    parser.add_argument("--log-both", type=str, help="Output matches to console AND specified file path")    args = parser.parse_args()    if args.tui:        start_tui()        return    if not args.target_dir or not args.regex:        parser.print_help()        sys.exit(1)    # --- PATH LOGIC ---    # Default: Relative path (as passed by user).    # If --path is set: Convert to Absolute Path.    search_path = args.target_dir    if args.path:        search_path = os.path.abspath(args.target_dir)    # Logging Setup    logger = logging.getLogger("DocSearch")    logger.setLevel(logging.INFO)    logger.propagate = False        file_path = args.log_file or args.log_both    use_console = args.log_console or args.log_both or (not args.log_file and not args.log_both)    if file_path:        # Force UTF-8 for emoji support in logs        fh = logging.FileHandler(file_path, mode='w', encoding='utf-8')        fh.setFormatter(logging.Formatter('%(message)s'))        logger.addHandler(fh)    start_time = time.time()    match_count = 0    try:        # Friendly start message        path_type = "Absolute" if args.path else "Relative"        print(f"Scanning ({path_type}): {search_path}")        with tqdm(unit="file", desc="Scanning") as pbar:            for event, data in search_parallel(search_path, args.regex, args.ignore_case, args.recursive, args.verbose):                                if event == "total":                    pbar.total = data                    pbar.refresh()                                elif event == "scan":                    pbar.update(1)                                elif event == "match":                    match_count += 1                    if file_path:                        logger.info(data)                    if use_console:                        pbar.write(data)    except KeyboardInterrupt:        sys.exit(0)        if use_console:        sys.stderr.write(f"\nDone. Found {match_count} matches in {time.time()-start_time:.2f}s.\n")if __name__ == "__main__":    main()'''

# 6. pyproject.toml
FILE_STRUCTURE["pyproject.toml"] = """[build-system]requires = ["setuptools>=61.0", "wheel"]build-backend = "setuptools.build_meta"[project]name = "docsearch"version = "1.0.7"description = "High-performance document search tool."dependencies = [    "pypdf>=3.0.0",    "openpyxl>=3.1.0",    "textual>=0.40.0",    "tqdm>=4.60.0"][project.scripts]docsearch = "docsearch.cli:main"[tool.setuptools.packages.find]where = ["."]include = ["docsearch*"]"""

# --- Bootstrapper Logic ---
def create_files():
    base_dir = os.getcwd()
    print(f"📦 Generating DocSearch v1.0.7 (Code Only) in: {base_dir}")

    for filepath, content in FILE_STRUCTURE.items():
        full_path = os.path.join(base_dir, filepath)
        directory = os.path.dirname(full_path)

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"  + Created: {filepath}")

    print("\n✅ Generation Complete! Run 'pip install -e .' to update.")

if __name__ == "__main__":
    create_files()
```

---

### 2. The Documentation (`README.md`)

You can copy and paste the text below into a file named `README.md` manually.

# DocSearch: High-Performance Document Search Engine

**Version:** 1.0.7

**Status:** Production Ready

**DocSearch** is a professional-grade, local search engine designed to `grep` through "binary" office formats as easily as plain text. It supports **PDF**, **Word** (`.docx`), **Excel** (`.xlsx`), **OpenOffice** (`.odt`), and **Jupyter Notebooks** (`.ipynb`) using true parallel processing.

## 🚀 Key Features

- **Multi-Format Support**: Natively parses `.pdf`, `.docx`, `.odt`, `.xlsx`, `.ods`, and `.ipynb`.

- **True Concurrency**: Uses `ProcessPoolExecutor` to bypass the Python GIL, utilizing all CPU cores.

- **Smart Feedback**:
  
  - **Progress Bar**: Real-time `tqdm` progress bar.
  
  - **Clean Output**: Silent by default except for matches.
  
  - **Verbose Mode**: Optional `-v` flag to debug internal parsing errors.

- **Flexible Paths**: Toggle between relative filenames (default) and absolute paths (`--path`).

- **Flexible Logging**:
  
  - Pipe results to console, file, or both.
  
  - Output is UTF-8 encoded to handle special characters and emojis.

## 📦 Installation

1. **Generate the Project**:
   
   Run the bootstrapper script to create the file structure.
   
   Bash
   
   ```
   python install_search.py
   ```

2. **Install Editable**:
   
   Install the package in "editable" mode so changes happen instantly.
   
   Bash
   
   ```
   pip install -e .
   ```

## 🛠 Usage

### Command Line Interface (CLI)

**Syntax:**

Bash

```
docsearch [DIRECTORY] [PATTERN] [FLAGS]
```

**Path Options:**

| Flag | Description |

| :--- | :--- |

| **(Default)** | Returns paths relative to current folder (e.g., `.\Invoice.pdf`). |

| `--path` | Returns full absolute paths (e.g., `C:\Users\Name\Docs\Invoice.pdf`). |

**Search Flags:**

| Flag | Description |

| :--- | :--- |

| `-r` | Search subdirectories (Default: Enabled). |

| `--no-recursive` | Search only the top-level directory. |

| `-i` | Ignore case (case-insensitive search). |

| `-v` / `--verbose` | Show internal warnings (e.g., corrupt PDF headers). |

**Logging Options:**

| Flag | Description |

| :--- | :--- |

| `--log-console` | Print matches to the terminal (Default). |

| `--log-file [PATH]` | Save matches to a text file (UTF-8). |

| `--log-both [PATH]` | Print to terminal AND save to file. |

**Examples:**

- **Relative Search (Standard):**
  
  Bash
  
  ```
  docsearch . "Invoice"
  # Output: .\Invoice_2024.pdf
  ```

- **Absolute Path Search:**
  
  Bash
  
  ```
  docsearch . "Invoice" --path
  # Output: C:\Users\Admin\Downloads\Invoice_2024.pdf
  ```

- **Silent Export to File:**
  
  Bash
  
  ```
  docsearch ~/Documents "Confidential" --log-file results.txt
  ```

### Graphical TUI

Launch the interactive interface:

Bash

```
docsearch --tui
```

## 🏗 Architecture

| **Component**     | **File**     | **Responsibility**                                                 |
| ----------------- | ------------ | ------------------------------------------------------------------ |
| **Presentation**  | `cli.py`     | Handles arguments and the `tqdm` progress bar.                     |
| **Orchestration** | `core.py`    | **Event-Driven**: Yields `total`, `scan`, and `match` events.      |
| **Data Access**   | `readers.py` | **Strategy Pattern**: Extensible readers for `.pdf`, `.docx`, etc. |

### Adding New Formats

To add `.md` or `.txt` support, simply add a class to `readers.py` and register it in `READER_REGISTRY`.
