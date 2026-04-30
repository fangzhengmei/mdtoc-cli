import pytest
import os
import tempfile
from mdtoc.core.parser import (
    extract_headings,
    generate_slug,
    parse_md_file,
    Heading,
    _github_slugify,
    _gitlab_slugify,
    _simple_slugify,
)


class TestHeadingExtraction:
    def test_extract_simple_headings(self):
        content = """# Header 1
Some text
## Header 2
More text
### Header 3
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].level == 1
        assert headings[0].text == "Header 1"
        assert headings[1].level == 2
        assert headings[1].text == "Header 2"
        assert headings[2].level == 3
        assert headings[2].text == "Header 3"
    
    def test_extract_with_special_characters(self):
        content = """# Header with spaces and !symbols@#$
## 中文标题
### CamelCaseTitle
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].text == "Header with spaces and !symbols@#$"
        assert headings[1].text == "中文标题"
        assert headings[2].text == "CamelCaseTitle"
    
    def test_ignore_non_heading_lines(self):
        content = """This is not a heading
# This is a heading
This is also not a heading
## Another heading
Not a heading either
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "This is a heading"
        assert headings[1].text == "Another heading"
    
    def test_line_numbers(self):
        content = """Line 1
# Heading 1
Line 3
## Heading 2
Line 5
"""
        headings = extract_headings(content)
        
        assert headings[0].line_number == 2
        assert headings[1].line_number == 4


class TestSlugGeneration:
    def test_github_slugify_basic(self):
        assert _github_slugify("Hello World") == "hello-world"
        assert _github_slugify("Hello   World") == "hello-world"
        assert _github_slugify("Hello-World_Test") == "hello-world-test"
    
    def test_github_slugify_special_chars(self):
        assert _github_slugify("Hello!@#$%^&*()World") == "helloworld"
        assert _github_slugify("Header with spaces") == "header-with-spaces"
    
    def test_slug_duplicate_handling(self):
        existing_slugs = {}
        
        slug1 = generate_slug("Header", existing_slugs, "github")
        assert slug1 == "header"
        assert existing_slugs["header"] == 1
        
        slug2 = generate_slug("Header", existing_slugs, "github")
        assert slug2 == "header-1"
        assert existing_slugs["header"] == 2
        
        slug3 = generate_slug("Header", existing_slugs, "github")
        assert slug3 == "header-2"
        assert existing_slugs["header"] == 3
    
    def test_slug_generation_in_headings(self):
        content = """# Header
## Header
### Header
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].slug == "header"
        assert headings[1].slug == "header-1"
        assert headings[2].slug == "header-2"
    
    def test_gitlab_slugify(self):
        assert _gitlab_slugify("Hello World") == "hello-world"
        assert _gitlab_slugify("Hello   World") == "hello-world"
    
    def test_simple_slugify(self):
        assert _simple_slugify("Hello World") == "hello-world"


class TestParseMdFile:
    def test_parse_file(self):
        content = """# Main Title
Some content
## Section 1
More content
### Subsection 1.1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            read_content, headings = parse_md_file(temp_path)
            
            assert read_content == content
            assert len(headings) == 3
            assert headings[0].text == "Main Title"
            assert headings[1].text == "Section 1"
            assert headings[2].text == "Subsection 1.1"
        finally:
            os.unlink(temp_path)
    
    def test_parse_file_with_slug_style(self):
        content = """# Header One
# Header One
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            _, headings = parse_md_file(temp_path, slug_style="github")
            
            assert headings[0].slug == "header-one"
            assert headings[1].slug == "header-one-1"
        finally:
            os.unlink(temp_path)
