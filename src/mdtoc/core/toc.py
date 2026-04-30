from typing import List, Optional, Dict
from .parser import Heading


def generate_toc_list(headings: List[Heading],
                      max_level: Optional[int] = None,
                      min_level: int = 1,
                      ordered: bool = False) -> List[str]:
    toc_lines = []
    counters: Dict[int, int] = {}
    
    for heading in headings:
        if heading.level < min_level:
            continue
        if max_level is not None and heading.level > max_level:
            continue
        
        effective_level = heading.level - min_level
        indent = "  " * effective_level
        text = heading.text
        link = f"#{heading.slug}"
        
        if ordered:
            counters[effective_level] = counters.get(effective_level, 0) + 1
            for level in list(counters.keys()):
                if level > effective_level:
                    del counters[level]
            
            toc_lines.append(f"{indent}{counters[effective_level]}. [{text}]({link})")
        else:
            toc_lines.append(f"{indent}- [{text}]({link})")
    
    return toc_lines


def generate_toc_string(headings: List[Heading],
                        max_level: Optional[int] = None,
                        min_level: int = 1,
                        ordered: bool = False,
                        title: Optional[str] = None) -> str:
    lines = []
    
    if title:
        lines.append(title)
        lines.append("")
    
    toc_lines = generate_toc_list(
        headings, max_level=max_level, min_level=min_level, ordered=ordered
    )
    lines.extend(toc_lines)
    
    return "\n".join(lines)


class TOCNode:
    def __init__(self, heading: Optional[Heading] = None):
        self.heading = heading
        self.children: List[TOCNode] = []
    
    def add_child(self, node: "TOCNode"):
        self.children.append(node)


def build_toc_tree(headings: List[Heading]) -> TOCNode:
    root = TOCNode()
    stack: List[TOCNode] = [root]
    
    for heading in headings:
        node = TOCNode(heading)
        
        while len(stack) > 1 and stack[-1].heading is not None:
            if stack[-1].heading.level >= heading.level:
                stack.pop()
            else:
                break
        
        stack[-1].add_child(node)
        stack.append(node)
    
    return root


def tree_to_list(node: TOCNode, level: int = 0, ordered: bool = False) -> List[str]:
    lines = []
    
    if node.heading is not None:
        indent = "  " * level
        text = node.heading.text
        link = f"#{node.heading.slug}"
        lines.append(f"{indent}- [{text}]({link})")
        level += 1
    
    for child in node.children:
        lines.extend(tree_to_list(child, level, ordered))
    
    return lines
