import argparse
import sys
import os
import time
import logging
from tqdm import tqdm
from .core import search_parallel
from .tui import start_tui

def main():
    parser = argparse.ArgumentParser(description="Advanced Document Search")
    parser.add_argument("--tui", action="store_true", help="Launch TUI (GUI)")
    
    # Renamed positional arg to 'target_dir' to allow '--path' flag
    parser.add_argument("target_dir", nargs="?", help="Directory to search")
    parser.add_argument("regex", nargs="?", help="Regex pattern")
    
    # Search Flags
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-r", "--recursive", action="store_true", default=True)
    parser.add_argument("--no-recursive", action="store_false", dest="recursive")
    
    # Output Flags
    parser.add_argument("--path", action="store_true", help="Output absolute paths instead of relative filenames")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose internal logs")
    
    # Logging Flags
    parser.add_argument("--log-console", action="store_true", help="Output matches to console")
    parser.add_argument("--log-file", type=str, help="Output matches to specified file path")
    parser.add_argument("--log-both", type=str, help="Output matches to console AND specified file path")

    args = parser.parse_args()

    if args.tui:
        start_tui()
        return

    if not args.target_dir or not args.regex:
        parser.print_help()
        sys.exit(1)

    # --- PATH LOGIC ---
    # Default: Relative path (as passed by user).
    # If --path is set: Convert to Absolute Path.
    search_path = args.target_dir
    if args.path:
        search_path = os.path.abspath(args.target_dir)

    # Logging Setup
    logger = logging.getLogger("DocSearch")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    file_path = args.log_file or args.log_both
    use_console = args.log_console or args.log_both or (not args.log_file and not args.log_both)

    if file_path:
        # Force UTF-8 for emoji support in logs
        fh = logging.FileHandler(file_path, mode='w', encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(fh)

    start_time = time.time()
    match_count = 0

    try:
        # Friendly start message
        path_type = "Absolute" if args.path else "Relative"
        print(f"Scanning ({path_type}): {search_path}")

        with tqdm(unit="file", desc="Scanning") as pbar:
            for event, data in search_parallel(search_path, args.regex, args.ignore_case, args.recursive, args.verbose):
                
                if event == "total":
                    pbar.total = data
                    pbar.refresh()
                
                elif event == "scan":
                    pbar.update(1)
                
                elif event == "match":
                    match_count += 1
                    if file_path:
                        logger.info(data)
                    if use_console:
                        pbar.write(data)

    except KeyboardInterrupt:
        sys.exit(0)
    
    if use_console:
        sys.stderr.write(f"\nDone. Found {match_count} matches in {time.time()-start_time:.2f}s.\n")

if __name__ == "__main__":
    main()
