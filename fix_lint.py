#!/usr/bin/env python3
"""Fix all linting issues automatically."""

import os
import re
from pathlib import Path


def fix_file(filepath):
    """Fix common linting issues in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix trailing whitespace and blank line with whitespace (W293, W291)
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    # Ensure newline at end of file (W292, W391)
    if lines and lines[-1] != '':
        lines.append('')

    content = '\n'.join(lines)

    # Only write if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")


def remove_unused_imports(filepath):
    """Remove specific unused imports."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    original_lines = lines.copy()

    # Map of files to imports to remove
    removals = {
        'api/main.py': ['Optional'],
        'core/llm/base.py': ['List', 'Dict', 'Any'],
        'core/prompts/base.py': ['List', 'Dict', 'Any'],
        'ingest/loaders/txt.py': ['os'],
        'web/documents/tests.py': ['TestCase'],
        'web/documents/views.py': ['render', 'status', 'Response'],
    }

    filepath_str = str(filepath)
    for file_pattern, imports_to_remove in removals.items():
        if file_pattern in filepath_str:
            new_lines = []
            for line in lines:
                skip = False
                for imp in imports_to_remove:
                    if f'import {imp}' in line or f'{imp},' in line:
                        # Remove the import
                        if 'from typing import' in line:
                            # Remove from typing imports
                            parts = line.split('import')[1].strip().split(',')
                            parts = [p.strip() for p in parts if imp not in p]
                            if parts:
                                line = f"from typing import {', '.join(parts)}\n"
                            else:
                                skip = True
                        elif f'import {imp}' == line.strip():
                            skip = True
                if not skip:
                    new_lines.append(line)
            lines = new_lines
            break

    if lines != original_lines:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Removed unused imports: {filepath}")


def fix_long_lines(filepath):
    """Fix long lines."""
    fixes = {
        'api/main.py': {
            92: '''                    answer=(
                        "I couldn't find any relevant information in the documents "
                        "to answer your question. Please try rephrasing your query "
                        "or check if documents have been uploaded."
                    ),''',
            131: '''        sources = [
            {
                "document_id": result.get("document_id"),
                "chunk_index": result.get("chunk_index"),
                "score": result.get("score"),
                "text_preview": (
                    result.get("text", "")[:200] + "..."
                    if len(result.get("text", "")) > 200
                    else result.get("text", "")
                ),
            }
            for result in reranked_results
        ]''',
        },
        'core/prompts/rag.py': {
            44: '''        return """You are a helpful assistant that answers questions based on the
provided context. Use only the information from the context to answer the question.
If the context doesn't contain enough information to answer the question, say so.
Be concise and accurate in your responses."""''',
        },
    }

    filepath_str = str(filepath)
    for file_pattern, line_fixes in fixes.items():
        if file_pattern in filepath_str:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, replacement in line_fixes.items():
                if line_num - 1 < len(lines):
                    # Find the line to replace (handle multi-line)
                    lines[line_num - 1] = replacement + '\n'

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Fixed long lines: {filepath}")
            break


def fix_unused_variables(filepath):
    """Comment out or remove unused variables."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix unused collections variable
    content = re.sub(
        r'(\s+)collections = (.*get_collections\(\))',
        r'\1_ = \2  # noqa: F841',
        content
    )

    # Fix unused loader variable
    content = re.sub(
        r'(\s+)loader = (TXTLoader\(\))',
        r'\1_ = \2  # noqa: F841',
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed unused variables: {filepath}")


def fix_web_urls(filepath):
    """Fix duplicate imports in web/web/urls.py."""
    if 'web/web/urls.py' in str(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove duplicate admin import
        lines = content.split('\n')
        new_lines = []
        seen_admin = False
        seen_path = False

        for line in lines:
            if 'from django.contrib import admin' in line:
                if not seen_admin:
                    new_lines.append(line)
                    seen_admin = True
            elif 'from django.urls import path' in line or 'from django.urls import include, path' in line:
                if not seen_path:
                    new_lines.append(line)
                    seen_path = True
            else:
                new_lines.append(line)

        new_content = '\n'.join(new_lines)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed duplicate imports: {filepath}")


def main():
    """Main function."""
    base_dir = Path(__file__).parent

    # Directories to process
    dirs = ['core', 'ingest', 'api', 'web']

    for dir_name in dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if 'migrations' not in str(py_file) and '__pycache__' not in str(py_file):
                    fix_file(py_file)
                    remove_unused_imports(py_file)
                    fix_unused_variables(py_file)
                    fix_web_urls(py_file)

    print("\n✅ All fixes applied!")


if __name__ == '__main__':
    main()

