import argparse
import sys
import time
from tqdm import tqdm
from .core import search_parallel, READER_REGISTRY
from .tui import start_tui

def main():
    parser = argparse.ArgumentParser(description="Advanced Document Search")
    parser.add_argument("--tui", action="store_true", help="Launch TUI (GUI)")
    parser.add_argument("path", nargs="?", help="Directory to search")
    parser.add_argument("regex", nargs="?", help="Regex pattern")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-r", "--recursive", action="store_true", default=True)
    parser.add_argument("--no-recursive", action="store_false", dest="recursive")

    args = parser.parse_args()

    if args.tui:
        start_tui()
        return

    if not args.path or not args.regex:
        parser.print_help()
        print("\nError: 'path' and 'regex' are required unless using --tui")
        sys.exit(1)

    print(f"\n🔍 Searching: '{args.regex}' in '{args.path}' (Recursive: {args.recursive})")
    start_time = time.time()
    matches = []

    try:
        with tqdm(unit=" files", desc="Scanning") as pbar:
            for match in search_parallel(args.path, args.regex, args.ignore_case, args.recursive):
                matches.append(match)
                pbar.write(f"  ✅ MATCH: {match}")
                pbar.update(1)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)

    print(f"\nDone. {len(matches)} matches in {time.time()-start_time:.2f}s.")

if __name__ == "__main__":
    main()
