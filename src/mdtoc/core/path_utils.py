import os
import glob
from typing import List, Optional
from pathlib import Path


def expand_file_paths(
    paths: List[str],
    recursive: bool = False,
    exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    expanded_paths: List[str] = []
    exclude_patterns = exclude_patterns or []
    
    for path in paths:
        if os.path.isdir(path):
            md_files = find_markdown_files(path, recursive=recursive)
            expanded_paths.extend(md_files)
        else:
            matched_files = glob.glob(path, recursive=recursive)
            for matched in matched_files:
                if os.path.isfile(matched):
                    expanded_paths.append(matched)
    
    filtered_paths = []
    for file_path in expanded_paths:
        should_exclude = any(
            fnmatch(file_path, pattern) or fnmatch(os.path.basename(file_path), pattern)
            for pattern in exclude_patterns
        )
        if not should_exclude and file_path.endswith((".md", ".markdown", ".mdown")):
            absolute_path = os.path.abspath(file_path)
            if absolute_path not in filtered_paths:
                filtered_paths.append(absolute_path)
    
    return filtered_paths


def find_markdown_files(directory: str, recursive: bool = False) -> List[str]:
    md_files = []
    extensions = (".md", ".markdown", ".mdown")
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extensions):
                    md_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith(extensions):
                md_files.append(os.path.join(directory, file))
    
    return [os.path.abspath(f) for f in md_files]


def fnmatch(path: str, pattern: str) -> bool:
    import fnmatch as fnm
    return fnm.fnmatch(path, pattern) or fnm.fnmatch(os.path.basename(path), pattern)


def get_relative_path(file_path: str, base_path: Optional[str] = None) -> str:
    if base_path is None:
        base_path = os.getcwd()
    
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path


def normalize_path(path: str) -> str:
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    return path
