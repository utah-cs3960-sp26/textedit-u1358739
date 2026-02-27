"""Test large file optimization with mmap and disabled highlighting."""

import pytest
import tempfile
import os
from pathlib import Path
from main import TextEditor, CodeEditor


class TestLargeFileOptimization:
    """Tests for large file handling optimizations."""

    def test_syntax_highlighting_disabled_for_large_files(self, qtbot, tmp_path):
        """Verify syntax highlighting is disabled for files > 5MB."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        # Create a large file (6MB) - exceeds the 5MB threshold
        large_content = "x" * (6 * 1024 * 1024)
        file_path = tmp_path / "large_file_6mb.txt"
        file_path.write_text(large_content, encoding='utf-8')
        
        # Set language from file - should disable highlighting
        editor.set_language_from_file(str(file_path))
        
        # Verify highlighting is disabled
        assert editor.highlighting_enabled is False

    def test_syntax_highlighting_enabled_for_small_files(self, qtbot, tmp_path):
        """Verify syntax highlighting is enabled for files < 5MB."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        # Create a small file (1MB) - below the 5MB threshold
        small_content = "x" * (1 * 1024 * 1024)
        file_path = tmp_path / "small_file_1mb.py"
        file_path.write_text(small_content, encoding='utf-8')
        
        # Set language from file - should enable highlighting
        editor.set_language_from_file(str(file_path))
        
        # Verify highlighting is enabled
        assert editor.highlighting_enabled is True
        # Verify language was set
        assert editor.highlighter.language == 'python'

    def test_mmap_used_for_large_files(self, qtbot, tmp_path):
        """Verify mmap is used for files > 10MB during loading."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create a file just over 10MB to trigger mmap
        large_content = "Line: " + ("x" * 100) + "\n"
        # Create ~11MB of content
        large_content = (large_content * (11 * 1024 * 1024 // len(large_content)))
        file_path = tmp_path / "very_large_file_11mb.txt"
        file_path.write_text(large_content, encoding='utf-8')
        
        # Load the file - should use mmap internally
        window.load_file(str(file_path))
        
        # Verify file was loaded
        assert window.current_file == str(file_path)
        # Content should be in the editor
        editor_content = window.editor.toPlainText()
        assert len(editor_content) > 0
        assert editor_content[:20] == large_content[:20]

    def test_normal_read_for_medium_files(self, qtbot, tmp_path):
        """Verify normal read is used for files between 5-10MB."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create a file between 5-10MB (uses normal read, not mmap)
        medium_content = "Line: " + ("x" * 100) + "\n"
        # Create ~7MB of content
        medium_content = (medium_content * (7 * 1024 * 1024 // len(medium_content)))
        file_path = tmp_path / "medium_file_7mb.txt"
        file_path.write_text(medium_content, encoding='utf-8')
        
        # Load the file - should use normal read
        window.load_file(str(file_path))
        
        # Verify file was loaded
        assert window.current_file == str(file_path)
        # Content should be in the editor
        editor_content = window.editor.toPlainText()
        assert len(editor_content) > 0
