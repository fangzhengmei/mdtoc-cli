import click
import os
import sys
from typing import List, Optional

from .core.parser import extract_headings, parse_md_file
from .core.toc import generate_toc_string
from .core.replacer import replace_placeholder
from .core.path_utils import expand_file_paths


@click.group()
@click.version_option(package_name="mdtoc")
def main():
    """Markdown Table of Contents generator."""
    pass


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--max-level", "-L", type=int, default=6, help="Maximum heading level to include (default: 6)")
@click.option("--min-level", "-l", type=int, default=1, help="Minimum heading level to include (default: 1)")
@click.option("--title", "-t", type=str, default="## Table of Contents", help="TOC title (default: '## Table of Contents')")
@click.option("--slug-style", "-s", type=click.Choice(["github", "gitlab", "simple"]), default="github", help="Slug generation style (default: github)")
@click.option("--recursive", "-R", is_flag=True, help="Recursively search directories for markdown files")
@click.option("--ordered", "-o", is_flag=True, help="Use ordered list instead of unordered")
@click.option("--no-title", is_flag=True, help="Do not include title in TOC output")
def generate(files: List[str], max_level: int, min_level: int, title: str,
             slug_style: str, recursive: bool, ordered: bool, no_title: bool):
    """Generate table of contents for markdown files.
    
    FILES can be one or more markdown files or directories.
    """
    if not files:
        click.echo("Error: No files specified", err=True)
        sys.exit(1)
    
    file_paths = expand_file_paths(list(files), recursive=recursive)
    
    if not file_paths:
        click.echo("Error: No markdown files found", err=True)
        sys.exit(1)
    
    toc_title = None if no_title else title
    
    for file_path in file_paths:
        try:
            content, headings = parse_md_file(file_path, slug_style=slug_style)
            
            if not headings:
                click.echo(f"# {file_path}")
                click.echo("(No headings found)")
                click.echo("")
                continue
            
            toc = generate_toc_string(
                headings,
                max_level=max_level,
                min_level=min_level,
                ordered=ordered,
                title=toc_title
            )
            
            click.echo(f"# {file_path}")
            click.echo(toc)
            click.echo("")
        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}", err=True)
            sys.exit(1)


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--max-level", "-L", type=int, default=6, help="Maximum heading level to include (default: 6)")
@click.option("--min-level", "-l", type=int, default=1, help="Minimum heading level to include (default: 1)")
@click.option("--title", "-t", type=str, default="## Table of Contents", help="TOC title (default: '## Table of Contents')")
@click.option("--slug-style", "-s", type=click.Choice(["github", "gitlab", "simple"]), default="github", help="Slug generation style (default: github)")
@click.option("--recursive", "-R", is_flag=True, help="Recursively search directories for markdown files")
@click.option("--dry-run", "-d", is_flag=True, help="Show changes without modifying files")
@click.option("--ordered", "-o", is_flag=True, help="Use ordered list instead of unordered")
def replace(files: List[str], max_level: int, min_level: int, title: str,
            slug_style: str, recursive: bool, dry_run: bool, ordered: bool):
    """Replace TOC placeholder in markdown files with generated TOC.
    
    Looks for placeholders like <!-- TOC --> or [TOC] in the file and
    replaces them with the generated table of contents.
    """
    if not files:
        click.echo("Error: No files specified", err=True)
        sys.exit(1)
    
    file_paths = expand_file_paths(list(files), recursive=recursive)
    
    if not file_paths:
        click.echo("Error: No markdown files found", err=True)
        sys.exit(1)
    
    for file_path in file_paths:
        try:
            content, headings = parse_md_file(file_path, slug_style=slug_style)
            
            new_content, was_replaced = replace_placeholder(
                content,
                headings,
                max_level=max_level,
                min_level=min_level,
                ordered=ordered,
                title=title
            )
            
            if dry_run:
                if was_replaced:
                    click.echo(f"# {file_path} (would be updated)")
                    click.echo("---")
                else:
                    click.echo(f"# {file_path} (no changes)")
            else:
                if was_replaced:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    click.echo(f"Updated: {file_path}")
                else:
                    click.echo(f"No placeholder found in: {file_path}")
        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}", err=True)
            sys.exit(1)


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--recursive", "-R", is_flag=True, help="Recursively search directories for markdown files")
@click.option("--slug-style", "-s", type=click.Choice(["github", "gitlab", "simple"]), default="github", help="Slug generation style (default: github)")
def list_headings(files: List[str], recursive: bool, slug_style: str):
    """List all headings with their slugs for debugging.
    
    Shows each heading, its level, and the generated slug.
    """
    if not files:
        click.echo("Error: No files specified", err=True)
        sys.exit(1)
    
    file_paths = expand_file_paths(list(files), recursive=recursive)
    
    if not file_paths:
        click.echo("Error: No markdown files found", err=True)
        sys.exit(1)
    
    for file_path in file_paths:
        try:
            _, headings = parse_md_file(file_path, slug_style=slug_style)
            
            click.echo(f"# {file_path}")
            if not headings:
                click.echo("  (No headings found)")
            else:
                for heading in headings:
                    indent = "  " * (heading.level - 1)
                    hashes = "#" * heading.level
                    click.echo(f"  {indent}{hashes} {heading.text}")
                    click.echo(f"  {indent}  → slug: #{heading.slug}")
            click.echo("")
        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
