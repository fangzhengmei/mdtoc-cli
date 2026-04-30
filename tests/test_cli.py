import pytest
import os
import tempfile
import shutil
from click.testing import CliRunner
from mdtoc.cli import main


class TestCLIGenerate:
    def setup_method(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        
        self.test_file = os.path.join(self.test_dir, "test.md")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("""# Main Title
Some content
## Section 1
More content
### Subsection 1.1
## Section 2
""")
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir)
    
    def test_generate_single_file(self):
        result = self.runner.invoke(main, ["generate", self.test_file])
        
        assert result.exit_code == 0
        assert "Main Title" in result.output
        assert "Section 1" in result.output
        assert "Subsection 1.1" in result.output
        assert "Table of Contents" in result.output
    
    def test_generate_with_level_filters(self):
        result = self.runner.invoke(
            main, ["generate", "--min-level", "2", "--max-level", "2", self.test_file]
        )
        
        assert result.exit_code == 0
        assert "Main Title" not in result.output
        assert "Section 1" in result.output
        assert "Section 2" in result.output
        assert "Subsection 1.1" not in result.output
    
    def test_generate_without_title(self):
        result = self.runner.invoke(main, ["generate", "--no-title", self.test_file])
        
        assert result.exit_code == 0
        assert "## Table of Contents" not in result.output
        assert "[Main Title](#main-title)" in result.output
    
    def test_generate_no_files(self):
        result = self.runner.invoke(main, ["generate"])
        
        assert result.exit_code != 0
        assert "No files specified" in result.output
    
    def test_generate_directory(self):
        result = self.runner.invoke(main, ["generate", self.test_dir])
        
        assert result.exit_code == 0
        assert "Main Title" in result.output
    
    def test_generate_recursive(self):
        sub_dir = os.path.join(self.test_dir, "sub")
        os.makedirs(sub_dir)
        sub_file = os.path.join(sub_dir, "sub.md")
        with open(sub_file, "w", encoding="utf-8") as f:
            f.write("# Sub Document")
        
        result = self.runner.invoke(main, ["generate", "-R", self.test_dir])
        
        assert result.exit_code == 0
        assert "Main Title" in result.output
        assert "Sub Document" in result.output


class TestCLIReplace:
    def setup_method(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        
        self.test_file = os.path.join(self.test_dir, "test.md")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("""# Main Title
Some intro text
<!-- TOC -->
## Section 1
### Subsection
## Section 2
""")
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir)
    
    def test_replace_placeholder(self):
        result = self.runner.invoke(main, ["replace", self.test_file])
        
        assert result.exit_code == 0
        assert "Updated" in result.output or "No placeholder" in result.output
        
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "<!-- TOC START -->" in content
        assert "<!-- TOC END -->" in content
        assert "[Main Title](#main-title)" in content
        assert "[Section 1](#section-1)" in content
        assert "[Section 2](#section-2)" in content
    
    def test_replace_dry_run(self):
        with open(self.test_file, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        result = self.runner.invoke(main, ["replace", "--dry-run", self.test_file])
        
        assert result.exit_code == 0
        assert "would be updated" in result.output
        
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert content == original_content
        assert "<!-- TOC START -->" not in content
    
    def test_replace_no_placeholder(self):
        no_placeholder_file = os.path.join(self.test_dir, "no_placeholder.md")
        with open(no_placeholder_file, "w", encoding="utf-8") as f:
            f.write("""# Title
## Section
""")
        
        result = self.runner.invoke(main, ["replace", no_placeholder_file])
        
        assert result.exit_code == 0
        assert "No placeholder found" in result.output


class TestCLIListHeadings:
    def setup_method(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        
        self.test_file = os.path.join(self.test_dir, "test.md")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("""# Title A
## Section 1
# Title A
""")
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir)
    
    def test_list_headings(self):
        result = self.runner.invoke(main, ["list-headings", self.test_file])
        
        assert result.exit_code == 0
        assert "# Title A" in result.output
        assert "## Section 1" in result.output
        assert "slug: #" in result.output
        assert "#title-a" in result.output
        assert "#title-a-1" in result.output
    
    def test_list_no_headings(self):
        no_headings_file = os.path.join(self.test_dir, "no_headings.md")
        with open(no_headings_file, "w", encoding="utf-8") as f:
            f.write("""Just some text
No headings here
""")
        
        result = self.runner.invoke(main, ["list-headings", no_headings_file])
        
        assert result.exit_code == 0
        assert "No headings found" in result.output


class TestCLIVersion:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        
        assert result.exit_code == 0
        assert "mdtoc" in result.output or "version" in result.output.lower()


class TestCLIHelp:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "generate" in result.output
        assert "replace" in result.output
        assert "list-headings" in result.output
    
    def test_generate_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate", "--help"])
        
        assert result.exit_code == 0
        assert "--max-level" in result.output
        assert "--min-level" in result.output
        assert "--recursive" in result.output
    
    def test_replace_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["replace", "--help"])
        
        assert result.exit_code == 0
        assert "--dry-run" in result.output
        assert "--recursive" in result.output
