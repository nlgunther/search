import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Iterator, Set
from .readers import READER_REGISTRY

def _worker_process_file(args: Tuple[str, str, str, bool]) -> Tuple[str, bool]:
    filepath, filename, pattern, ignore_case = args
    ext = os.path.splitext(filename)[1].lower()
    
    reader_cls = READER_REGISTRY.get(ext)
    if not reader_cls:
        return filename, False

    content = reader_cls().read(filepath)
    flags = re.IGNORECASE if ignore_case else 0
    
    if re.search(pattern, content, flags):
        return filename, True
    return filename, False

def find_files(directory: str, extensions: Set[str], recursive: bool) -> Iterator[Tuple[str, str]]:
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    yield os.path.join(root, file), file
    else:
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                if os.path.splitext(file)[1].lower() in extensions:
                    yield os.path.join(directory, file), file

def search_parallel(directory: str, pattern: str, ignore_case: bool = False, recursive: bool = True) -> Iterator[str]:
    supported_exts = set(READER_REGISTRY.keys())
    tasks = []

    for full_path, filename in find_files(directory, supported_exts, recursive):
        tasks.append((full_path, filename, pattern, ignore_case))

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(_worker_process_file, task) for task in tasks]
        for future in as_completed(futures):
            filename, found = future.result()
            if found:
                yield filename
