import pytest
import os
import tempfile
import shutil
from pathlib import Path
from mdtoc.core.path_utils import (
    expand_file_paths,
    find_markdown_files,
    get_relative_path,
    normalize_path,
    fnmatch,
)


class TestExpandFilePaths:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        
        file1 = os.path.join(self.test_dir, "doc1.md")
        with open(file1, "w") as f:
            f.write("# Doc 1")
        
        file2 = os.path.join(self.test_dir, "doc2.markdown")
        with open(file2, "w") as f:
            f.write("# Doc 2")
        
        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.sub_dir)
        
        file3 = os.path.join(self.sub_dir, "doc3.md")
        with open(file3, "w") as f:
            f.write("# Doc 3")
        
        self.txt_file = os.path.join(self.test_dir, "readme.txt")
        with open(self.txt_file, "w") as f:
            f.write("Not markdown")
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir)
    
    def test_expand_single_file(self):
        file_path = os.path.join(self.test_dir, "doc1.md")
        paths = expand_file_paths([file_path])
        
        assert len(paths) == 1
        assert os.path.basename(paths[0]) == "doc1.md"
    
    def test_expand_directory_non_recursive(self):
        paths = expand_file_paths([self.test_dir], recursive=False)
        
        assert len(paths) == 2
        basenames = [os.path.basename(p) for p in paths]
        assert "doc1.md" in basenames
        assert "doc2.markdown" in basenames
        assert "doc3.md" not in basenames
    
    def test_expand_directory_recursive(self):
        paths = expand_file_paths([self.test_dir], recursive=True)
        
        assert len(paths) == 3
        basenames = [os.path.basename(p) for p in paths]
        assert "doc1.md" in basenames
        assert "doc2.markdown" in basenames
        assert "doc3.md" in basenames
    
    def test_expand_with_exclude_patterns(self):
        paths = expand_file_paths(
            [self.test_dir],
            recursive=True,
            exclude_patterns=["*doc1*"]
        )
        
        basenames = [os.path.basename(p) for p in paths]
        assert "doc1.md" not in basenames
        assert "doc2.markdown" in basenames
        assert "doc3.md" in basenames
    
    def test_expand_multiple_files(self):
        file1 = os.path.join(self.test_dir, "doc1.md")
        file2 = os.path.join(self.test_dir, "doc2.markdown")
        
        paths = expand_file_paths([file1, file2])
        
        assert len(paths) == 2
    
    def test_expand_removes_duplicates(self):
        file1 = os.path.join(self.test_dir, "doc1.md")
        
        paths = expand_file_paths([file1, file1])
        
        assert len(paths) == 1


class TestFindMarkdownFiles:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        
        with open(os.path.join(self.test_dir, "a.md"), "w") as f:
            f.write("# A")
        with open(os.path.join(self.test_dir, "b.markdown"), "w") as f:
            f.write("# B")
        with open(os.path.join(self.test_dir, "c.mdown"), "w") as f:
            f.write("# C")
        with open(os.path.join(self.test_dir, "d.txt"), "w") as f:
            f.write("# D")
        
        self.sub_dir = os.path.join(self.test_dir, "sub")
        os.makedirs(self.sub_dir)
        with open(os.path.join(self.sub_dir, "e.md"), "w") as f:
            f.write("# E")
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir)
    
    def test_find_markdown_extensions(self):
        files = find_markdown_files(self.test_dir, recursive=False)
        
        assert len(files) == 3
        basenames = [os.path.basename(f) for f in files]
        assert "a.md" in basenames
        assert "b.markdown" in basenames
        assert "c.mdown" in basenames
        assert "d.txt" not in basenames
    
    def test_find_recursive(self):
        files = find_markdown_files(self.test_dir, recursive=True)
        
        assert len(files) == 4
        basenames = [os.path.basename(f) for f in files]
        assert "e.md" in basenames


class TestRelativePath:
    def test_relative_path_same_directory(self):
        base = "/home/user/docs"
        file_path = "/home/user/docs/file.md"
        
        rel = get_relative_path(file_path, base)
        assert rel == "file.md"
    
    def test_relative_path_subdirectory(self):
        base = "/home/user/docs"
        file_path = "/home/user/docs/sub/file.md"
        
        rel = get_relative_path(file_path, base)
        assert rel == os.path.join("sub", "file.md")
    
    def test_relative_path_uses_cwd_as_default(self):
        rel = get_relative_path(__file__)
        assert os.path.isabs(__file__)
        assert not os.path.isabs(rel) or rel == __file__


class TestNormalizePath:
    def test_normalize_expand_user(self):
        if os.name == "nt":
            path = "~\\documents"
        else:
            path = "~/documents"
        
        normalized = normalize_path(path)
        
        assert "~" not in normalized
        assert os.path.isabs(normalized)
    
    def test_normalize_dots(self):
        path = "/home/../home/user/./docs"
        normalized = normalize_path(path)
        
        assert ".." not in normalized
        assert "/./" not in normalized


class TestFnmatch:
    def test_fnmatch_basic(self):
        assert fnmatch("/path/to/file.md", "*.md") is True
        assert fnmatch("/path/to/file.md", "*.txt") is False
    
    def test_fnmatch_against_basename(self):
        assert fnmatch("/some/long/path/document.md", "document.*") is True
        assert fnmatch("/some/long/path/document.md", "other.*") is False
