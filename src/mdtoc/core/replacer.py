import re
from typing import List, Tuple
from .parser import Heading
from .toc import generate_toc_list


TOC_PLACEHOLDERS = [
    r"<!--\s*TOC\s*-->",
    r"\[TOC\]",
    r"\[toc\]",
    r"<!--\s*toc\s*-->",
]


def find_placeholder(content: str) -> Tuple[int, int, str]:
    for pattern in TOC_PLACEHOLDERS:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.start(), match.end(), match.group(0)
    return -1, -1, ""


def find_toc_block(content: str) -> Tuple[int, int, bool]:
    toc_start_marker = "<!-- TOC START -->"
    toc_end_marker = "<!-- TOC END -->"
    
    start_idx = content.find(toc_start_marker)
    if start_idx == -1:
        return -1, -1, False
    
    end_idx = content.find(toc_end_marker, start_idx)
    if end_idx == -1:
        return -1, -1, False
    
    return start_idx, end_idx + len(toc_end_marker), True


def replace_placeholder(
    content: str,
    headings: List[Heading],
    max_level: int = 6,
    min_level: int = 1,
    ordered: bool = False,
    title: str = "## Table of Contents"
) -> Tuple[str, bool]:
    toc_start_marker = "<!-- TOC START -->"
    toc_end_marker = "<!-- TOC END -->"
    
    block_start, block_end, has_block = find_toc_block(content)
    
    if has_block:
        toc_list = generate_toc_list(
            headings, max_level=max_level, min_level=min_level, ordered=ordered
        )
        toc_content = "\n".join(toc_list)
        
        new_block = f"{toc_start_marker}\n{title}\n\n{toc_content}\n{toc_end_marker}"
        new_content = content[:block_start] + new_block + content[block_end:]
        return new_content, True
    
    placeholder_start, placeholder_end, placeholder = find_placeholder(content)
    
    if placeholder_start == -1:
        return content, False
    
    toc_list = generate_toc_list(
        headings, max_level=max_level, min_level=min_level, ordered=ordered
    )
    toc_content = "\n".join(toc_list)
    
    toc_block = f"{toc_start_marker}\n{title}\n\n{toc_content}\n{toc_end_marker}"
    
    new_content = content[:placeholder_start] + toc_block + content[placeholder_end:]
    return new_content, True
