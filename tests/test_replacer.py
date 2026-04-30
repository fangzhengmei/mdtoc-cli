import pytest
from mdtoc.core.parser import extract_headings
from mdtoc.core.replacer import (
    replace_placeholder,
    find_placeholder,
    find_toc_block,
    TOC_PLACEHOLDERS,
)


class TestFindPlaceholder:
    def test_find_html_comment_toc(self):
        content = """# Title
<!-- TOC -->
## Section
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start != -1
        assert placeholder == "<!-- TOC -->"
    
    def test_find_bracket_toc(self):
        content = """# Title
[TOC]
## Section
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start != -1
        assert placeholder == "[TOC]"
    
    def test_find_lowercase_toc(self):
        content = """# Title
[toc]
## Section
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start != -1
        assert placeholder == "[toc]"
    
    def test_find_html_comment_lowercase(self):
        content = """# Title
<!-- toc -->
## Section
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start != -1
        assert placeholder == "<!-- toc -->"
    
    def test_no_placeholder(self):
        content = """# Title
## Section
Some content
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start == -1
        assert end == -1
        assert placeholder == ""
    
    def test_placeholder_in_content(self):
        content = """# Title
Here is some text.
<!-- TOC -->
More text here.
## Section
"""
        start, end, placeholder = find_placeholder(content)
        
        assert start != -1
        assert content[start:end] == "<!-- TOC -->"


class TestFindTOCBlock:
    def test_find_existing_toc_block(self):
        content = """# Title
<!-- TOC START -->
## Table of Contents

- [Title](#title)
- [Section](#section)
<!-- TOC END -->
## Section
"""
        start, end, found = find_toc_block(content)
        
        assert found is True
        assert start != -1
        assert end != -1
    
    def test_no_toc_block(self):
        content = """# Title
## Section
"""
        start, end, found = find_toc_block(content)
        
        assert found is False
        assert start == -1
        assert end == -1
    
    def test_toc_block_without_end(self):
        content = """# Title
<!-- TOC START -->
- [Title](#title)
## Section
"""
        start, end, found = find_toc_block(content)
        
        assert found is False


class TestReplacePlaceholder:
    def test_replace_html_placeholder(self):
        content = """# Main Title
<!-- TOC -->
## Section 1
### Subsection
## Section 2
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, title="## Contents"
        )
        
        assert was_replaced is True
        assert "<!-- TOC -->" not in new_content
        assert "<!-- TOC START -->" in new_content
        assert "<!-- TOC END -->" in new_content
        assert "## Contents" in new_content
        assert "[Main Title](#main-title)" in new_content
        assert "[Section 1](#section-1)" in new_content
        assert "[Subsection](#subsection)" in new_content
        assert "[Section 2](#section-2)" in new_content
    
    def test_replace_bracket_placeholder(self):
        content = """# Main Title
[TOC]
## Section
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, title="## Contents"
        )
        
        assert was_replaced is True
        assert "[TOC]" not in new_content
        assert "<!-- TOC START -->" in new_content
    
    def test_no_placeholder_no_replace(self):
        content = """# Main Title
## Section
Some text
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, title="## Contents"
        )
        
        assert was_replaced is False
        assert new_content == content
    
    def test_replace_existing_toc_block(self):
        content = """# Main Title
<!-- TOC START -->
## Contents (Old)

- [Link that should be replaced](#old-link)
<!-- TOC END -->
## New Section
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, title="## Table of Contents"
        )
        
        assert was_replaced is True
        assert "old-link" not in new_content
        assert "Table of Contents" in new_content
        assert "[Main Title](#main-title)" in new_content
        assert "[New Section](#new-section)" in new_content
    
    def test_replace_with_level_filters(self):
        content = """# Title 1
<!-- TOC -->
## Title 2
### Title 3
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, min_level=2, max_level=2, title="## Contents"
        )
        
        assert was_replaced is True
        assert "# Title 1" in new_content
        assert "[Title 1](#title-1)" not in new_content
        assert "[Title 2](#title-2)" in new_content
        assert "[Title 3](#title-3)" not in new_content
    
    def test_replace_with_duplicate_slugs(self):
        content = """# Header
<!-- TOC -->
# Header
"""
        headings = extract_headings(content)
        
        new_content, was_replaced = replace_placeholder(
            content, headings, title="## Contents"
        )
        
        assert was_replaced is True
        assert "[Header](#header)" in new_content
        assert "[Header](#header-1)" in new_content
