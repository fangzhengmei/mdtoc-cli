import pytest
import os
import tempfile
from mdtoc.core.parser import (
    extract_headings,
    generate_slug,
    parse_md_file,
    is_code_block,
    detect_yaml_front_matter,
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
```
# This is a code block, not a heading
```
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "This is a heading"
        assert headings[1].text == "Another heading"
    
    def test_skip_code_block_backticks(self):
        content = """# Real Heading
```python
# This is a comment, not a heading
def hello():
    pass
```
## Another Real Heading
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Real Heading"
        assert headings[1].text == "Another Real Heading"
    
    def test_skip_code_block_tilde(self):
        content = """# Real Heading
~~~python
# This is a comment, not a heading
def hello():
    pass
~~~
## Another Real Heading
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Real Heading"
        assert headings[1].text == "Another Real Heading"
    
    def test_skip_code_block_with_language(self):
        content = """# Before Code
```javascript
// # This is not a heading
const x = 1;
```
# After Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before Code"
        assert headings[1].text == "After Code"
    
    def test_nested_headings_around_code_blocks(self):
        content = """# Level 1
## Level 2
```
# Not a heading
## Also not
```
### Level 3
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].level == 1
        assert headings[1].level == 2
        assert headings[2].level == 3
    
    def test_multiple_code_blocks(self):
        content = """# Heading 1
```
# Fake
```
# Heading 2
~~~
# Also fake
~~~
# Heading 3
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].text == "Heading 1"
        assert headings[1].text == "Heading 2"
        assert headings[2].text == "Heading 3"
    
    def test_unclosed_code_block(self):
        content = """# Valid Heading
```
# This is in an unclosed block
# Another one
"""
        headings = extract_headings(content)
        
        assert len(headings) == 1
        assert headings[0].text == "Valid Heading"
    
    def test_indented_code_block_fence(self):
        content = """# Real Heading
    ```python
    # Indented code block
    ```
## After Indented Block
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Real Heading"
        assert headings[1].text == "After Indented Block"
    
    def test_skip_cpp_code_block(self):
        content = """# Before C++ Code
```c++
// This is a C++ comment
# define MACRO // not a heading
int main() {
    return 0;
}
```
## After C++ Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before C++ Code"
        assert headings[1].text == "After C++ Code"
    
    def test_skip_bash_session_code_block(self):
        content = """# Before Bash Session
```bash-session
$ echo "hello"
# This is a shell comment, not a heading
$ ls
```
## After Bash Session
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before Bash Session"
        assert headings[1].text == "After Bash Session"
    
    def test_skip_csharp_code_block(self):
        content = """# Before C# Code
```c#
// C# comment
#region MyRegion // not a heading
public class Hello { }
```
## After C# Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before C# Code"
        assert headings[1].text == "After C# Code"
    
    def test_skip_fsharp_code_block(self):
        content = """# Before F# Code
```f#
// F# comment
#nowarn "40" // compiler directive, not a heading
let hello = "world"
```
## After F# Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before F# Code"
        assert headings[1].text == "After F# Code"
    
    def test_skip_objective_c_code_block(self):
        content = """# Before Objective-C Code
```objective-c
// Objective-C comment
#import <Foundation/Foundation.h> // #import, not a heading
int main() { }
```
## After Objective-C Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before Objective-C Code"
        assert headings[1].text == "After Objective-C Code"
    
    def test_skip_html_jinja_code_block(self):
        content = """# Before HTML+Jinja
```html+jinja
<!-- HTML comment -->
{# Jinja comment, not a heading #}
<h1>Title</h1>
```
## After HTML+Jinja
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before HTML+Jinja"
        assert headings[1].text == "After HTML+Jinja"
    
    def test_tilde_cpp_code_block(self):
        content = """# Before Code
~~~c++
# define SOMETHING
~~~
## After Code
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Before Code"
        assert headings[1].text == "After Code"
    
    def test_multiple_special_language_blocks(self):
        content = """# Start
```c++
# define
```
## Middle
```bash-session
# shell comment
```
### End
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].text == "Start"
        assert headings[1].text == "Middle"
        assert headings[2].text == "End"
    
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


class TestCodeBlockDetection:
    def test_is_code_block_backtick_start(self):
        in_code, fence = is_code_block("```", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_backtick_end(self):
        in_code, fence = is_code_block("```", True, "```")
        assert in_code is False
        assert fence == ""
    
    def test_is_code_block_tilde_start(self):
        in_code, fence = is_code_block("~~~", False, "")
        assert in_code is True
        assert fence == "~~~"
    
    def test_is_code_block_tilde_end(self):
        in_code, fence = is_code_block("~~~", True, "~~~")
        assert in_code is False
        assert fence == ""
    
    def test_is_code_block_with_language(self):
        in_code, fence = is_code_block("```python", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_indented_fence(self):
        in_code, fence = is_code_block("    ```", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_not_fence(self):
        in_code, fence = is_code_block("# This is a heading", False, "")
        assert in_code is False
        assert fence == ""
    
    def test_is_code_block_different_fence_mismatch(self):
        in_code, fence = is_code_block("~~~", True, "```")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_cpp_language(self):
        in_code, fence = is_code_block("```c++", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_bash_session(self):
        in_code, fence = is_code_block("```bash-session", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_csharp(self):
        in_code, fence = is_code_block("```c#", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_fsharp(self):
        in_code, fence = is_code_block("```f#", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_with_dots(self):
        in_code, fence = is_code_block("```objective-c", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_tilde_with_symbols(self):
        in_code, fence = is_code_block("~~~c++", False, "")
        assert in_code is True
        assert fence == "~~~"
    
    def test_is_code_block_complex_language_tag(self):
        in_code, fence = is_code_block("```html+jinja", False, "")
        assert in_code is True
        assert fence == "```"
    
    def test_is_code_block_ending_with_special_language(self):
        in_code, fence = is_code_block("```c++", True, "```")
        assert in_code is False
        assert fence == ""


class TestYAMLFrontMatterDetection:
    def test_detect_front_matter_simple(self):
        lines = ["---", "title: Test", "---", "# Heading"]
        end = detect_yaml_front_matter(lines)
        assert end == 3
    
    def test_detect_front_matter_with_dots_end(self):
        lines = ["---", "title: Test", "...", "# Heading"]
        end = detect_yaml_front_matter(lines)
        assert end == 3
    
    def test_detect_front_matter_no_start(self):
        lines = ["# Heading", "---", "content"]
        end = detect_yaml_front_matter(lines)
        assert end == 0
    
    def test_detect_front_matter_empty(self):
        lines = []
        end = detect_yaml_front_matter(lines)
        assert end == 0
    
    def test_detect_front_matter_unclosed(self):
        lines = ["---", "title: Test", "# Heading"]
        end = detect_yaml_front_matter(lines)
        assert end == 3
    
    def test_detect_front_matter_with_comments(self):
        lines = [
            "---",
            "title: My Document",
            "# This is a YAML comment",
            "tags: [test]",
            "---",
            "# Real Heading"
        ]
        end = detect_yaml_front_matter(lines)
        assert end == 5


class TestYAMLFrontMatterIntegration:
    def test_skip_yaml_comments_in_front_matter(self):
        content = """---
title: My Document
# This is a YAML comment
tags: [test]
---

# First Heading
## Second Heading
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "First Heading"
        assert headings[1].text == "Second Heading"
    
    def test_yaml_front_matter_at_start_only(self):
        content = """# Heading Before
---
This is not front matter
---
# Heading After
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Heading Before"
        assert headings[1].text == "Heading After"
    
    def test_complex_yaml_front_matter(self):
        content = """---
# YAML comment at start
title: Test Document
# Another YAML comment
author: John Doe
---

## Section 1
### Subsection
"""
        headings = extract_headings(content)
        
        assert len(headings) == 2
        assert headings[0].text == "Section 1"
        assert headings[1].text == "Subsection"
    
    def test_yaml_front_matter_with_dots_ending(self):
        content = """---
title: Test
...

# First Heading
"""
        headings = extract_headings(content)
        
        assert len(headings) == 1
        assert headings[0].text == "First Heading"
    
    def test_no_front_matter_normal_document(self):
        content = """# Heading 1
## Heading 2
### Heading 3
"""
        headings = extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0].text == "Heading 1"
        assert headings[1].text == "Heading 2"
        assert headings[2].text == "Heading 3"
