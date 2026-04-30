import pytest
from mdtoc.core.parser import Heading, extract_headings
from mdtoc.core.toc import (
    generate_toc_list,
    generate_toc_string,
    build_toc_tree,
    tree_to_list,
    TOCNode,
)


class TestGenerateTOCList:
    def test_generate_simple_toc(self):
        content = """# Main Title
## Section 1
### Subsection 1.1
## Section 2
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings)
        
        assert len(toc) == 4
        assert toc[0] == "- [Main Title](#main-title)"
        assert toc[1] == "  - [Section 1](#section-1)"
        assert toc[2] == "    - [Subsection 1.1](#subsection-11)"
        assert toc[3] == "  - [Section 2](#section-2)"
    
    def test_toc_with_max_level(self):
        content = """# Main Title
## Section 1
### Subsection 1.1
#### Sub-subsection
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, max_level=2)
        
        assert len(toc) == 2
        assert "Subsection" not in toc[1] if len(toc) > 1 else True
        assert "Sub-subsection" not in "".join(toc)
    
    def test_toc_with_min_level(self):
        content = """# Main Title
## Section 1
### Subsection 1.1
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, min_level=2)
        
        assert len(toc) == 2
        assert "Main Title" not in "".join(toc)
        assert toc[0] == "- [Section 1](#section-1)"
        assert toc[1] == "  - [Subsection 1.1](#subsection-11)"
    
    def test_toc_with_level_range(self):
        content = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, min_level=2, max_level=4)
        
        assert len(toc) == 3
        assert "Level 2" in toc[0]
        assert "Level 4" in toc[2]
        assert "Level 1" not in "".join(toc)
        assert "Level 5" not in "".join(toc)
        assert "Level 6" not in "".join(toc)
    
    def test_empty_headings(self):
        toc = generate_toc_list([])
        assert toc == []


class TestOrderedTOCList:
    def test_ordered_toc_simple(self):
        content = """# Level 1
## Level 2a
## Level 2b
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, ordered=True)
        
        assert len(toc) == 3
        assert toc[0] == "1. [Level 1](#level-1)"
        assert toc[1] == "  1. [Level 2a](#level-2a)"
        assert toc[2] == "  2. [Level 2b](#level-2b)"
    
    def test_ordered_toc_multiple_levels(self):
        content = """# A
## B
### C
## D
# E
## F
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, ordered=True)
        
        assert len(toc) == 6
        assert toc[0] == "1. [A](#a)"
        assert toc[1] == "  1. [B](#b)"
        assert toc[2] == "    1. [C](#c)"
        assert toc[3] == "  2. [D](#d)"
        assert toc[4] == "2. [E](#e)"
        assert toc[5] == "  1. [F](#f)"
    
    def test_ordered_toc_with_min_level(self):
        content = """# Level 1
## Level 2a
### Level 3
## Level 2b
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, ordered=True, min_level=2)
        
        assert len(toc) == 3
        assert toc[0] == "1. [Level 2a](#level-2a)"
        assert toc[1] == "  1. [Level 3](#level-3)"
        assert toc[2] == "2. [Level 2b](#level-2b)"
    
    def test_ordered_toc_with_max_level(self):
        content = """# 1
## 2
### 3
#### 4
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings, ordered=True, max_level=2)
        
        assert len(toc) == 2
        assert toc[0] == "1. [1](#1)"
        assert toc[1] == "  1. [2](#2)"
    
    def test_ordered_vs_unordered(self):
        content = """# A
# B
"""
        headings = extract_headings(content)
        
        toc_unordered = generate_toc_list(headings, ordered=False)
        toc_ordered = generate_toc_list(headings, ordered=True)
        
        assert toc_unordered[0] == "- [A](#a)"
        assert toc_unordered[1] == "- [B](#b)"
        assert toc_ordered[0] == "1. [A](#a)"
        assert toc_ordered[1] == "2. [B](#b)"


class TestGenerateTOCString:
    def test_generate_toc_with_title(self):
        content = """# Title
## Section
"""
        headings = extract_headings(content)
        toc_str = generate_toc_string(headings, title="## Contents")
        
        assert "## Contents" in toc_str
        assert "- [Title](#title)" in toc_str
        assert "- [Section](#section)" in toc_str
    
    def test_generate_toc_without_title(self):
        content = """# Title
## Section
"""
        headings = extract_headings(content)
        toc_str = generate_toc_string(headings, title=None)
        
        assert "##" not in toc_str or "## " not in toc_str
        assert "- [Title](#title)" in toc_str
    
    def test_generate_toc_empty(self):
        toc_str = generate_toc_string([])
        assert toc_str == ""


class TestTOCTree:
    def test_build_tree_simple(self):
        content = """# Level 1
## Level 2
### Level 3
## Another Level 2
"""
        headings = extract_headings(content)
        tree = build_toc_tree(headings)
        
        assert tree.heading is None
        assert len(tree.children) == 1
        
        level1 = tree.children[0]
        assert level1.heading.text == "Level 1"
        assert len(level1.children) == 2
        
        level2_1 = level1.children[0]
        assert level2_1.heading.text == "Level 2"
        assert len(level2_1.children) == 1
        
        level3 = level2_1.children[0]
        assert level3.heading.text == "Level 3"
        assert len(level3.children) == 0
        
        level2_2 = level1.children[1]
        assert level2_2.heading.text == "Another Level 2"
        assert len(level2_2.children) == 0
    
    def test_tree_to_list(self):
        content = """# Main
## Sub 1
### Deep
## Sub 2
"""
        headings = extract_headings(content)
        tree = build_toc_tree(headings)
        toc_list = tree_to_list(tree)
        
        assert len(toc_list) == 4
        assert "Main" in toc_list[0]
        assert "Sub 1" in toc_list[1]
        assert "Deep" in toc_list[2]
        assert "Sub 2" in toc_list[3]


class TestComplexHeadingStructures:
    def test_skipped_levels(self):
        content = """# Level 1
### Level 3 (skipped 2)
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings)
        
        assert len(toc) == 2
        # Level 3 should be indented one level from level 1, not two
        # Because it's the next heading after level 1
    
    def test_same_level_headings(self):
        content = """# A
# B
# C
"""
        headings = extract_headings(content)
        toc = generate_toc_list(headings)
        
        assert len(toc) == 3
        assert toc[0].startswith("- [A]")
        assert toc[1].startswith("- [B]")
        assert toc[2].startswith("- [C]")
