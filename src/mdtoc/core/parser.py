import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Heading:
    level: int
    text: str
    slug: str
    line_number: int


def generate_slug(text: str, existing_slugs: Dict[str, int],
                  slug_style: str = "github") -> str:
    if slug_style == "github":
        slug = _github_slugify(text)
    elif slug_style == "gitlab":
        slug = _gitlab_slugify(text)
    else:
        slug = _simple_slugify(text)
    
    if slug in existing_slugs:
        count = existing_slugs[slug]
        new_slug = f"{slug}-{count}"
        existing_slugs[slug] += 1
        return new_slug
    else:
        existing_slugs[slug] = 1
        return slug


def _github_slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\-]", "", text)
    text = text.strip()
    text = re.sub(r"[\s\-_]+", "-", text)
    return text


def _gitlab_slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text


def _simple_slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\-]", "-", text)
    return text


def is_code_block(line: str, in_code_block: bool, code_fence: str = "") -> Tuple[bool, str]:
    fenced_pattern = r"^(\s*)(```|~~~)([^\s`~]*)\s*$"
    
    match = re.match(fenced_pattern, line)
    if match:
        fence = match.group(2)
        if not in_code_block:
            return True, fence
        elif fence == code_fence:
            return False, ""
    
    return in_code_block, code_fence


def detect_yaml_front_matter(lines: List[str]) -> int:
    if not lines:
        return 0
    
    first_line = lines[0].strip()
    if first_line != "---":
        return 0
    
    for i in range(1, len(lines)):
        stripped = lines[i].strip()
        if stripped in ("---", "..."):
            return i + 1
    
    return len(lines)


def extract_headings(content: str, slug_style: str = "github") -> List[Heading]:
    lines = content.split("\n")
    headings = []
    existing_slugs: Dict[str, int] = {}
    in_code_block = False
    code_fence = ""
    
    front_matter_end = detect_yaml_front_matter(lines)
    
    for line_num, line in enumerate(lines, 1):
        if line_num <= front_matter_end:
            continue
        
        in_code_block, code_fence = is_code_block(line, in_code_block, code_fence)
        if in_code_block:
            continue
        
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            slug = generate_slug(text, existing_slugs, slug_style)
            headings.append(Heading(level=level, text=text, slug=slug, line_number=line_num))
    
    return headings


def parse_md_file(file_path: str, slug_style: str = "github") -> Tuple[str, List[Heading]]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    headings = extract_headings(content, slug_style)
    return content, headings
