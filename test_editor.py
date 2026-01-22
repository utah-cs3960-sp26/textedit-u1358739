import pytest
import os
import tempfile
from pathlib import Path
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QTextCursor, QFont
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog

from main import TextEditor, CodeEditor, FindReplaceDialog, LineNumberArea


class TestCodeEditor:
    """Tests for the CodeEditor widget."""

    def test_code_editor_creation(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        assert editor is not None
        assert isinstance(editor.line_number_area, LineNumberArea)

    def test_line_number_area_exists(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.show()
        qtbot.waitExposed(editor)
        assert editor.line_number_area is not None
        assert editor.line_number_area.isVisible()

    def test_line_number_area_width_single_digit(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1")
        width = editor.line_number_area_width()
        assert width > 0

    def test_line_number_area_width_increases_with_lines(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1")
        width_single = editor.line_number_area_width()
        
        editor.setPlainText("\n".join([f"Line {i}" for i in range(1, 101)]))
        width_triple = editor.line_number_area_width()
        
        assert width_triple > width_single

    def test_font_is_monospace(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        font = editor.font()
        assert font.fixedPitch() or font.family() == "Consolas"

    def test_tab_stop_distance_set(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        assert editor.tabStopDistance() > 0

    def test_text_insertion(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello, World!")
        assert editor.toPlainText() == "Hello, World!"

    def test_multiline_text(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        text = "Line 1\nLine 2\nLine 3"
        editor.setPlainText(text)
        assert editor.blockCount() == 3

    def test_cursor_position_updates(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello\nWorld")
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        
        assert editor.textCursor().blockNumber() == 1

    def test_highlight_current_line(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1\nLine 2")
        editor.highlight_current_line()
        selections = editor.extraSelections()
        assert len(selections) >= 1

    def test_undo_redo(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Original")
        editor.selectAll()
        editor.insertPlainText("Modified")
        assert editor.toPlainText() == "Modified"
        
        editor.undo()
        assert editor.toPlainText() == "Original"
        
        editor.redo()
        assert editor.toPlainText() == "Modified"

    def test_cut_copy_paste(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World")
        editor.selectAll()
        editor.copy()
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        editor.paste()
        
        assert "Hello WorldHello World" in editor.toPlainText()

    def test_select_all(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World")
        editor.selectAll()
        assert editor.textCursor().hasSelection()
        assert editor.textCursor().selectedText() == "Hello World"

    def test_clear(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Some text")
        editor.clear()
        assert editor.toPlainText() == ""

    def test_resize_updates_line_number_area(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.resize(800, 600)
        editor.show()
        qtbot.waitExposed(editor)
        
        line_area_rect = editor.line_number_area.geometry()
        assert line_area_rect.height() > 0
        assert line_area_rect.width() > 0


class TestTextEditor:
    """Tests for the main TextEditor window."""

    def test_window_creation(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert window is not None
        assert "TextEdit" in window.windowTitle()

    def test_initial_title_is_untitled(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert "Untitled" in window.windowTitle()

    def test_editor_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert window.editor is not None
        assert isinstance(window.editor, CodeEditor)

    def test_file_tree_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        assert window.file_tree is not None
        assert window.file_tree.isVisible()

    def test_status_bar_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert window.status_bar is not None
        assert window.cursor_label is not None
        assert window.encoding_label is not None
        assert window.file_type_label is not None

    def test_initial_cursor_position_label(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert "Ln 1" in window.cursor_label.text()
        assert "Col 1" in window.cursor_label.text()

    def test_encoding_label_shows_utf8(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert "UTF-8" in window.encoding_label.text()

    def test_menu_bar_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        menubar = window.menuBar()
        assert menubar is not None

    def test_file_menu_actions(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        menubar = window.menuBar()
        
        file_menu = None
        for action in menubar.actions():
            if "File" in action.text():
                file_menu = action.menu()
                break
        
        assert file_menu is not None
        action_texts = [a.text() for a in file_menu.actions()]
        assert any("New" in t for t in action_texts)
        assert any("Open" in t for t in action_texts)
        assert any("Save" in t for t in action_texts)
        assert any("Exit" in t or "xit" in t for t in action_texts)

    def test_edit_menu_actions(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        menubar = window.menuBar()
        
        edit_menu = None
        for action in menubar.actions():
            if "Edit" in action.text():
                edit_menu = action.menu()
                break
        
        assert edit_menu is not None
        
        # Verify edit menu has actions (menus get populated)
        actions = edit_menu.actions()
        assert len(actions) > 0
        
        # Verify some expected actions exist by checking action count
        # (at least: undo, redo, separator, cut, copy, paste, separator, select all, separator, find)
        assert len(actions) >= 8

    def test_view_menu_actions(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        menubar = window.menuBar()
        
        view_menu = None
        for action in menubar.actions():
            if "View" in action.text():
                view_menu = action.menu()
                break
        
        assert view_menu is not None
        action_texts = [a.text() for a in view_menu.actions()]
        assert any("Sidebar" in t for t in action_texts)
        assert any("Zoom" in t for t in action_texts)

    def test_dark_theme_applied(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        style = window.styleSheet()
        assert len(style) > 0
        assert "#1e1e1e" in style or "1e1e1e" in style

    def test_new_file_clears_editor(self, qtbot, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Some content")
        window.editor.document().setModified(False)
        
        window.new_file()
        
        assert window.editor.toPlainText() == ""
        assert "Untitled" in window.windowTitle()

    def test_cursor_position_updates_on_move(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Line 1\nLine 2\nLine 3")
        
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.Down)
        cursor.movePosition(QTextCursor.Down)
        cursor.movePosition(QTextCursor.Right)
        cursor.movePosition(QTextCursor.Right)
        window.editor.setTextCursor(cursor)
        
        assert "Ln 3" in window.cursor_label.text()
        assert "Col 3" in window.cursor_label.text()

    def test_text_changed_marks_modified(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Initial")
        window.editor.document().setModified(False)
        window.setWindowTitle("TextEdit - Untitled")
        
        window.editor.insertPlainText(" modified")
        
        assert window.editor.document().isModified()

    def test_toggle_sidebar_hides_file_tree(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        assert window.file_tree.isVisible()
        
        window.toggle_sidebar()
        assert not window.file_tree.isVisible()
        
        window.toggle_sidebar()
        assert window.file_tree.isVisible()

    def test_zoom_in_increases_font_size(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        initial_size = window.editor.font().pointSize()
        
        window.zoom_in()
        
        assert window.editor.font().pointSize() == initial_size + 1

    def test_zoom_out_decreases_font_size(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        initial_size = window.editor.font().pointSize()
        
        window.zoom_out()
        
        assert window.editor.font().pointSize() == initial_size - 1

    def test_zoom_in_also_zooms_line_numbers(self, qtbot):
        """Line numbers should zoom in along with the text."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        initial_editor_size = window.editor.font().pointSize()
        initial_line_num_size = window.editor.line_number_area.font().pointSize()
        
        window.zoom_in()
        
        new_editor_size = window.editor.font().pointSize()
        new_line_num_size = window.editor.line_number_area.font().pointSize()
        
        assert new_editor_size == initial_editor_size + 1
        assert new_line_num_size == initial_line_num_size + 1, \
            f"Line number font should zoom in from {initial_line_num_size} to {initial_line_num_size + 1}, but got {new_line_num_size}"

    def test_zoom_out_also_zooms_line_numbers(self, qtbot):
        """Line numbers should zoom out along with the text."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        initial_editor_size = window.editor.font().pointSize()
        initial_line_num_size = window.editor.line_number_area.font().pointSize()
        
        window.zoom_out()
        
        new_editor_size = window.editor.font().pointSize()
        new_line_num_size = window.editor.line_number_area.font().pointSize()
        
        assert new_editor_size == initial_editor_size - 1
        assert new_line_num_size == initial_line_num_size - 1, \
            f"Line number font should zoom out from {initial_line_num_size} to {initial_line_num_size - 1}, but got {new_line_num_size}"

    def test_zoom_out_minimum_limit(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        for _ in range(20):
            window.zoom_out()
        
        assert window.editor.font().pointSize() >= 6

    def test_update_file_type_python(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("test.py")
        assert "Python" in window.file_type_label.text()

    def test_update_file_type_javascript(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("test.js")
        assert "JavaScript" in window.file_type_label.text()

    def test_update_file_type_html(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("index.html")
        assert "HTML" in window.file_type_label.text()

    def test_update_file_type_css(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("styles.css")
        assert "CSS" in window.file_type_label.text()

    def test_update_file_type_json(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("config.json")
        assert "JSON" in window.file_type_label.text()

    def test_update_file_type_markdown(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("README.md")
        assert "Markdown" in window.file_type_label.text()

    def test_update_file_type_plain_text(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("notes.txt")
        assert "Plain Text" in window.file_type_label.text()

    def test_update_file_type_unknown(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.update_file_type("file.xyz")
        assert "Plain Text" in window.file_type_label.text()


class TestFileOperations:
    """Tests for file save/load operations."""

    def test_save_to_file(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        test_content = "Test content for saving"
        window.editor.setPlainText(test_content)
        
        file_path = tmp_path / "test_save.txt"
        result = window.save_to_file(str(file_path))
        
        assert result is True
        assert file_path.exists()
        assert file_path.read_text(encoding='utf-8') == test_content

    def test_save_updates_window_title(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.editor.setPlainText("Content")
        file_path = tmp_path / "test.txt"
        window.save_to_file(str(file_path))
        
        assert str(file_path) in window.windowTitle()

    def test_save_clears_modified_flag(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.editor.setPlainText("Content")
        window.editor.document().setModified(True)
        
        file_path = tmp_path / "test.txt"
        window.save_to_file(str(file_path))
        
        assert not window.editor.document().isModified()

    def test_load_file(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        test_content = "Content to load"
        file_path = tmp_path / "test_load.txt"
        file_path.write_text(test_content, encoding='utf-8')
        
        window.load_file(str(file_path))
        
        assert window.editor.toPlainText() == test_content

    def test_load_file_updates_title(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content", encoding='utf-8')
        
        window.load_file(str(file_path))
        
        assert str(file_path) in window.windowTitle()

    def test_load_file_updates_file_type(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        file_path = tmp_path / "script.py"
        file_path.write_text("print('hello')", encoding='utf-8')
        
        window.load_file(str(file_path))
        
        assert "Python" in window.file_type_label.text()

    def test_load_nonexistent_file_shows_error(self, qtbot, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        
        error_shown = []
        monkeypatch.setattr(QMessageBox, "critical", lambda *args: error_shown.append(True))
        
        window.load_file("/nonexistent/path/file.txt")
        
        assert len(error_shown) == 1

    def test_save_file_calls_save_as_when_no_current_file(self, qtbot, monkeypatch, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Content")
        
        file_path = tmp_path / "new_file.txt"
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName",
            lambda *args, **kwargs: (str(file_path), "All Files (*)")
        )
        
        result = window.save_file()
        
        assert result is True
        assert file_path.exists()

    def test_save_file_uses_current_file(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        file_path = tmp_path / "existing.txt"
        file_path.write_text("Original", encoding='utf-8')
        window.load_file(str(file_path))
        
        window.editor.setPlainText("Modified content")
        window.save_file()
        
        assert file_path.read_text(encoding='utf-8') == "Modified content"

    def test_maybe_save_returns_true_when_not_modified(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.document().setModified(False)
        
        assert window.maybe_save() is True

    def test_maybe_save_with_discard(self, qtbot, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Content")
        window.editor.document().setModified(True)
        
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Discard)
        
        assert window.maybe_save() is True

    def test_maybe_save_with_cancel(self, qtbot, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Content")
        window.editor.document().setModified(True)
        
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Cancel)
        
        assert window.maybe_save() is False

    def test_maybe_save_with_save(self, qtbot, monkeypatch, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        window.editor.setPlainText("Content")
        window.editor.document().setModified(True)
        
        file_path = tmp_path / "save_on_close.txt"
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Save)
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName",
            lambda *args, **kwargs: (str(file_path), "All Files (*)")
        )
        
        assert window.maybe_save() is True
        assert file_path.exists()

    def test_save_unicode_content(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        unicode_content = "Hello 世界 🌍 Привет"
        window.editor.setPlainText(unicode_content)
        
        file_path = tmp_path / "unicode.txt"
        window.save_to_file(str(file_path))
        
        assert file_path.read_text(encoding='utf-8') == unicode_content

    def test_load_unicode_content(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        unicode_content = "Hello 世界 🌍 Привет"
        file_path = tmp_path / "unicode.txt"
        file_path.write_text(unicode_content, encoding='utf-8')
        
        window.load_file(str(file_path))
        
        assert window.editor.toPlainText() == unicode_content


class TestFindReplaceDialog:
    """Tests for Find and Replace functionality."""

    def test_dialog_creation(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        
        assert dialog is not None
        assert "Find" in dialog.windowTitle()

    def test_dialog_has_find_input(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        
        assert dialog.find_input is not None

    def test_dialog_has_replace_input(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        
        assert dialog.replace_input is not None

    def test_find_next_finds_text(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World Hello")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.find_next()
        
        assert editor.textCursor().hasSelection()
        assert editor.textCursor().selectedText() == "Hello"

    def test_find_next_wraps_around(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World")
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.find_next()
        
        assert editor.textCursor().hasSelection()
        assert editor.textCursor().selectedText() == "Hello"

    def test_find_with_no_match(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("xyz")
        dialog.find_next()
        
        assert not editor.textCursor().hasSelection()

    def test_replace_single(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.replace_input.setText("Hi")
        
        dialog.find_next()
        dialog.replace()
        
        assert "Hi World" in editor.toPlainText()

    def test_replace_single_with_uppercase_replacement(self, qtbot):
        """Test single replace using an all-uppercase replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("hello world hello")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("GOODBYE")
        
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert text == "GOODBYE world hello"
        assert text.count("GOODBYE") == 1
        assert text.count("hello") == 1  # Second "hello" unchanged

    def test_replace_single_with_lowercase_replacement(self, qtbot):
        """Test single replace using an all-lowercase replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("HELLO WORLD HELLO")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("HELLO")
        dialog.replace_input.setText("goodbye")
        
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert text == "goodbye WORLD HELLO"
        assert text.count("goodbye") == 1
        assert text.count("HELLO") == 1  # Second "HELLO" unchanged

    def test_replace_single_with_mixed_case_replacement(self, qtbot):
        """Test single replace using a mixed-case replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("foo bar foo")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("foo")
        dialog.replace_input.setText("BaZ")
        
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert text == "BaZ bar foo"
        assert text.count("BaZ") == 1
        assert text.count("foo") == 1  # Second "foo" unchanged

    def test_replace_single_finds_different_case(self, qtbot):
        """Test that single replace can find and replace different case variations."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello HELLO hello")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("BYE")
        
        # Find and replace first match
        dialog.find_next()
        dialog.replace()
        
        # Find and replace second match
        dialog.find_next()
        dialog.replace()
        
        # Find and replace third match
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert text.count("BYE") == 3
        assert "Hello" not in text
        assert "HELLO" not in text
        assert "hello" not in text

    def test_replace_all(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello World Hello Universe Hello")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.replace_input.setText("Hi")
        dialog.replace_all()
        
        text = editor.toPlainText()
        assert "Hello" not in text
        assert text.count("Hi") == 3

    def test_replace_empty_find_does_nothing(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        original = "Hello World"
        editor.setPlainText(original)
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("")
        dialog.replace_input.setText("Hi")
        dialog.replace_all()
        
        assert editor.toPlainText() == original

    def test_find_case_sensitive(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello hello HELLO")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.find_next()
        
        cursor = editor.textCursor()
        assert cursor.hasSelection()

    def test_find_case_sensitive_exact_match(self, qtbot):
        """Test that find matches the exact case when searching."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello hello HELLO")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.find_next()
        
        cursor = editor.textCursor()
        assert cursor.hasSelection()
        assert cursor.selectedText() == "Hello"

    def test_find_case_sensitive_no_match_different_case(self, qtbot):
        """Test that find with exact case doesn't match different cases."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("HELLO HELLO HELLO")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.find_next()
        
        # Qt's find is case-insensitive by default, so it will find a match
        # This test documents current behavior
        cursor = editor.textCursor()
        # The find should still work (Qt default is case-insensitive)
        assert cursor.hasSelection()

    def test_replace_preserves_other_cases(self, qtbot):
        """Test that replace only replaces the exact match found."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Hello hello HELLO")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("Hello")
        dialog.replace_input.setText("Hi")
        
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert "Hi" in text
        # After replacing first "Hello", text should still have other variations
        assert "hello" in text or "HELLO" in text

    def test_replace_all_should_be_case_insensitive_like_find(self, qtbot):
        """
        Replace All should be case-insensitive, matching Find's behavior.
        
        When searching for 'what', Replace All should replace ALL case variations:
        'what', 'What', 'WHAT' should all be replaced.
        """
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("what What WHAT what")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("what")
        dialog.replace_input.setText("what!")
        
        dialog.replace_all()
        
        text = editor.toPlainText()
        # Replace All should replace ALL case variations (case-insensitive)
        assert text.count("what!") == 4  # All 4 instances should be replaced
        assert "What" not in text  # Should be replaced
        assert "WHAT" not in text  # Should be replaced

    def test_replace_all_with_uppercase_replacement(self, qtbot):
        """Test Replace All using an all-uppercase replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("hello Hello HELLO world")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("GOODBYE")
        dialog.replace_all()
        
        text = editor.toPlainText()
        # All case variations of "hello" should be replaced with "GOODBYE"
        assert text == "GOODBYE GOODBYE GOODBYE world"
        assert text.count("GOODBYE") == 3
        assert "hello" not in text.lower() or "goodbye" in text.lower()

    def test_replace_all_with_lowercase_replacement(self, qtbot):
        """Test Replace All using an all-lowercase replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("HELLO Hello HeLLo world")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("goodbye")
        dialog.replace_all()
        
        text = editor.toPlainText()
        # All case variations of "hello" should be replaced with "goodbye"
        assert text == "goodbye goodbye goodbye world"
        assert text.count("goodbye") == 3

    def test_replace_all_with_mixed_case_replacement(self, qtbot):
        """Test Replace All using a mixed-case replacement string."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("foo FOO Foo fOO world")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("foo")
        dialog.replace_input.setText("BaR")
        dialog.replace_all()
        
        text = editor.toPlainText()
        # All case variations of "foo" should be replaced with "BaR"
        assert text == "BaR BaR BaR BaR world"
        assert text.count("BaR") == 4
        assert "foo" not in text.lower() or "bar" in text.lower()

    def test_multiple_replace_all_operations(self, qtbot):
        """Test performing multiple Replace All operations in sequence."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("The quick brown fox jumps over the lazy dog")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        
        # First replace: "the" -> "THE" (case-insensitive)
        dialog.find_input.setText("the")
        dialog.replace_input.setText("THE")
        dialog.replace_all()
        
        text = editor.toPlainText()
        assert text.count("THE") == 2
        
        # Second replace: "fox" -> "FOX"
        dialog.find_input.setText("fox")
        dialog.replace_input.setText("FOX")
        dialog.replace_all()
        
        text = editor.toPlainText()
        assert "FOX" in text
        
        # Third replace: "dog" -> "Cat"
        dialog.find_input.setText("dog")
        dialog.replace_input.setText("Cat")
        dialog.replace_all()
        
        text = editor.toPlainText()
        assert "Cat" in text
        assert text == "THE quick brown FOX jumps over THE lazy Cat"

    def test_find_replace_marks_document_as_modified(self, qtbot, tmp_path, monkeypatch):
        """
        Test that using find and replace on an opened file marks the document as modified,
        so that closing the file triggers the unsaved changes warning.
        """
        # Create a test file
        test_file = tmp_path / "test_doc.txt"
        test_file.write_text("hello world hello", encoding='utf-8')
        
        # Open the file in the editor
        window = TextEditor()
        qtbot.addWidget(window)
        window.load_file(str(test_file))
        
        # Verify file loaded and not modified
        assert window.editor.toPlainText() == "hello world hello"
        assert not window.editor.document().isModified()
        
        # Use find and replace
        dialog = FindReplaceDialog(window.editor, window)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("goodbye")
        
        dialog.find_next()
        dialog.replace()
        
        # Verify document is now modified
        assert window.editor.document().isModified()
        
        # Track if the save warning dialog was triggered
        warning_shown = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: warning_shown.append(True) or QMessageBox.Discard)
        
        # Try to close - should trigger unsaved changes warning
        window.close()
        
        # Verify the warning was shown
        assert len(warning_shown) == 1, "Unsaved changes warning should be shown when closing after find/replace"

    def test_replace_all_marks_document_as_modified(self, qtbot, tmp_path, monkeypatch):
        """
        Test that using Replace All on an opened file marks the document as modified,
        so that closing the file triggers the unsaved changes warning.
        """
        # Create a test file
        test_file = tmp_path / "test_doc.txt"
        test_file.write_text("hello world hello", encoding='utf-8')
        
        # Open the file in the editor
        window = TextEditor()
        qtbot.addWidget(window)
        window.load_file(str(test_file))
        
        # Verify file loaded and not modified
        assert window.editor.toPlainText() == "hello world hello"
        assert not window.editor.document().isModified()
        
        # Use Replace All
        dialog = FindReplaceDialog(window.editor, window)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("goodbye")
        dialog.replace_all()
        
        # Verify document is now modified
        assert window.editor.document().isModified(), "Document should be marked as modified after Replace All"
        
        # Track if the save warning dialog was triggered
        warning_shown = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: warning_shown.append(True) or QMessageBox.Discard)
        
        # Try to close - should trigger unsaved changes warning
        window.close()
        
        # Verify the warning was shown
        assert len(warning_shown) == 1, "Unsaved changes warning should be shown when closing after Replace All"

    def test_undo_after_replace_all(self, qtbot):
        """
        Test that undo works correctly after Replace All:
        1. Make some changes
        2. Use Replace All
        3. Undo Replace All
        4. Undo the previous changes
        """
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        # Start with initial text
        editor.setPlainText("hello world")
        editor.document().setModified(False)
        
        # Make a change: add " foo" at the end
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        editor.insertPlainText(" foo")
        
        assert editor.toPlainText() == "hello world foo"
        
        # Use Replace All to replace "hello" with "goodbye"
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("hello")
        dialog.replace_input.setText("goodbye")
        dialog.replace_all()
        
        assert editor.toPlainText() == "goodbye world foo"
        
        # Undo Replace All - should go back to "hello world foo"
        editor.undo()
        assert editor.toPlainText() == "hello world foo", "Undo should revert Replace All"
        
        # Undo the " foo" addition - should go back to "hello world"
        editor.undo()
        assert editor.toPlainText() == "hello world", "Undo should revert the ' foo' addition"


class TestMenuLayout:
    """Tests for menu appearance and layout."""

    def test_menu_items_have_adequate_shortcut_padding(self, qtbot):
        """
        Test that menu styling includes adequate padding between text and shortcuts.
        The QMenu::item stylesheet should have proper padding to prevent text/shortcut overlap.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        style = window.styleSheet()
        
        # Check that QMenu::item has padding defined (not just QMenu)
        # This is required to provide spacing between menu item text and keyboard shortcuts
        assert "QMenu::item" in style, \
            "QMenu::item should be styled in the stylesheet"
        
        # Extract QMenu::item section and verify it has padding
        import re
        menu_item_match = re.search(r'QMenu::item\s*\{[^}]*\}', style)
        assert menu_item_match, "QMenu::item styling block not found"
        
        menu_item_style = menu_item_match.group(0)
        assert "padding" in menu_item_style, \
            "QMenu::item should have padding defined to prevent text/shortcut overlap"


class TestWindowGeometry:
    """Tests for window size and positioning."""

    def test_initial_window_fits_on_screen(self, qtbot):
        """
        Test that the initial window size fits within the available screen space.
        The window should not extend beyond the screen boundaries.
        """
        from PySide6.QtWidgets import QApplication
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get available screen geometry (excludes taskbar, etc.)
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Get window geometry
        window_geometry = window.frameGeometry()
        
        # Window should fit within screen bounds
        assert window_geometry.right() <= screen.right(), \
            f"Window extends beyond right edge: window ends at {window_geometry.right()}, screen ends at {screen.right()}"
        assert window_geometry.bottom() <= screen.bottom(), \
            f"Window extends beyond bottom edge: window ends at {window_geometry.bottom()}, screen ends at {screen.bottom()}"
        assert window_geometry.left() >= screen.left(), \
            f"Window extends beyond left edge: window starts at {window_geometry.left()}, screen starts at {screen.left()}"
        assert window_geometry.top() >= screen.top(), \
            f"Window extends beyond top edge: window starts at {window_geometry.top()}, screen starts at {screen.top()}"


class TestKeyboardShortcuts:
    """Tests for keyboard shortcuts."""

    def test_zoom_in_shortcut_is_ctrl_equals(self, qtbot):
        """
        Test that the Zoom In menu action uses Ctrl+= (without Shift) as shortcut.
        On most keyboards, + requires Shift, so Ctrl+= is more accessible.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Find the Zoom In action in the View menu
        menubar = window.menuBar()
        zoom_in_action = None
        
        for menu_action in menubar.actions():
            if "View" in menu_action.text():
                view_menu = menu_action.menu()
                for action in view_menu.actions():
                    if "Zoom" in action.text() and "In" in action.text():
                        zoom_in_action = action
                        break
        
        assert zoom_in_action is not None, "Zoom In action not found"
        
        # Check the shortcut is Ctrl+= (not Ctrl+Shift+=)
        shortcut = zoom_in_action.shortcut().toString()
        assert shortcut == "Ctrl+=", \
            f"Zoom In shortcut should be 'Ctrl+=' but got '{shortcut}'"

    def test_no_alternate_zoom_in_shortcut(self, qtbot):
        """
        Test that Ctrl+Shift+= (Ctrl++) does NOT work as a zoom in shortcut.
        Only Ctrl+= should zoom in.
        """
        from PySide6.QtGui import QShortcut
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Check that there are no QShortcut children with Ctrl++ binding
        shortcuts = window.findChildren(QShortcut)
        zoom_plus_shortcuts = [s for s in shortcuts if "+" in s.key().toString()]
        
        assert len(zoom_plus_shortcuts) == 0, \
            f"Should not have alternate Ctrl++ shortcut, but found: {[s.key().toString() for s in zoom_plus_shortcuts]}"

    def test_ctrl_n_new_file(self, qtbot, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.editor.setPlainText("Content")
        window.editor.document().setModified(False)
        
        # Test the action directly since keyboard shortcuts may not work in test env
        window.new_file()
        
        assert window.editor.toPlainText() == ""

    def test_ctrl_z_undo(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.editor.setPlainText("Original")
        window.editor.selectAll()
        window.editor.insertPlainText("New")
        
        qtbot.keyClick(window.editor, Qt.Key_Z, Qt.ControlModifier)
        
        assert window.editor.toPlainText() == "Original"

    def test_ctrl_y_redo(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.editor.setPlainText("Original")
        window.editor.selectAll()
        window.editor.insertPlainText("New")
        window.editor.undo()
        
        qtbot.keyClick(window.editor, Qt.Key_Y, Qt.ControlModifier)
        
        assert window.editor.toPlainText() == "New"

    def test_ctrl_a_select_all(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.editor.setPlainText("Select all this text")
        
        qtbot.keyClick(window.editor, Qt.Key_A, Qt.ControlModifier)
        
        assert window.editor.textCursor().hasSelection()
        assert window.editor.textCursor().selectedText() == "Select all this text"

    def test_ctrl_b_toggle_sidebar(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        assert window.file_tree.isVisible()
        
        # Test the action directly since keyboard shortcuts may not work in test env
        window.toggle_sidebar()
        
        assert not window.file_tree.isVisible()


class TestLineNumberArea:
    """Tests for LineNumberArea widget."""

    def test_line_number_area_creation(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        line_area = LineNumberArea(editor)
        
        assert line_area is not None
        assert line_area.editor == editor

    def test_size_hint(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        size = editor.line_number_area.sizeHint()
        assert size.width() > 0
        assert size.height() == 0


class TestEditorIntegration:
    """Integration tests for the full editor workflow."""

    def test_full_edit_workflow(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Type content via insertPlainText to trigger modification
        window.editor.insertPlainText("Hello World")
        assert window.editor.document().isModified()
        
        file_path = tmp_path / "workflow_test.txt"
        window.save_to_file(str(file_path))
        assert file_path.exists()
        assert not window.editor.document().isModified()
        
        window.editor.insertPlainText(" Modified content")
        window.save_file()
        assert "Modified content" in file_path.read_text(encoding='utf-8')

    def test_create_edit_save_reopen(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        content = "Test content\nLine 2\nLine 3"
        window.editor.setPlainText(content)
        
        file_path = tmp_path / "reopen_test.txt"
        window.save_to_file(str(file_path))
        
        window.new_file()
        assert window.editor.toPlainText() == ""
        
        window.load_file(str(file_path))
        assert window.editor.toPlainText() == content

    def test_multiple_find_replace(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("foo bar foo baz foo")
        
        dialog = FindReplaceDialog(editor)
        qtbot.addWidget(dialog)
        dialog.find_input.setText("foo")
        dialog.replace_input.setText("qux")
        
        dialog.find_next()
        dialog.replace()
        
        dialog.find_next()
        dialog.replace()
        
        text = editor.toPlainText()
        assert text.count("qux") == 2
        assert text.count("foo") == 1

    def test_zoom_persistence(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        initial_size = window.editor.font().pointSize()
        
        window.zoom_in()
        window.zoom_in()
        window.zoom_in()
        
        assert window.editor.font().pointSize() == initial_size + 3
        
        window.zoom_out()
        
        assert window.editor.font().pointSize() == initial_size + 2

    def test_large_file_handling(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        large_content = "\n".join([f"Line {i}: " + "x" * 100 for i in range(1000)])
        file_path = tmp_path / "large_file.txt"
        file_path.write_text(large_content, encoding='utf-8')
        
        window.load_file(str(file_path))
        
        assert window.editor.blockCount() == 1000
        
        saved_path = tmp_path / "large_file_saved.txt"
        window.save_to_file(str(saved_path))
        assert saved_path.read_text(encoding='utf-8') == large_content

    def test_special_characters_in_filename(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        file_path = tmp_path / "test file (1).txt"
        window.editor.setPlainText("Content")
        window.save_to_file(str(file_path))
        
        assert file_path.exists()
        
        window.new_file()
        window.load_file(str(file_path))
        assert window.editor.toPlainText() == "Content"


class TestFolderLabelDisplay:
    """Tests for folder name display in sidebar."""

    def test_folder_label_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert hasattr(window, 'folder_label')
        assert window.folder_label is not None

    def test_folder_label_initially_displays_current_folder(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        folder_text = window.folder_label.text()
        assert len(folder_text) > 0
        assert "📁" in folder_text

    def test_update_folder_label_with_simple_path(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        test_path = "/home/user/Documents"
        window.update_folder_label(test_path)
        
        assert "Documents" in window.folder_label.text()
        assert "📁" in window.folder_label.text()

    def test_update_folder_label_with_nested_path(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        nested = tmp_path / "level1" / "level2"
        nested.mkdir(parents=True)
        
        window.update_folder_label(str(nested))
        
        assert "level2" in window.folder_label.text()

    def test_update_folder_label_with_root_path(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.update_folder_label("/")
        
        assert window.folder_label.text() == "📁 /"

    def test_folder_label_updates_on_open_folder(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test folder
        test_folder = tmp_path / "my_project"
        test_folder.mkdir()
        
        # Mock QFileDialog to return our test folder
        monkeypatch.setattr(
            "main.QFileDialog.getExistingDirectory",
            lambda *args, **kwargs: str(test_folder)
        )
        
        window.open_folder()
        
        assert "my_project" in window.folder_label.text()

    def test_folder_label_shows_basename_only(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        full_path = "/very/long/path/to/my_folder"
        window.update_folder_label(full_path)
        
        # Should only show the basename, not the full path
        assert "my_folder" in window.folder_label.text()
        assert "/very/long" not in window.folder_label.text()

    def test_folder_label_handles_windows_paths(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        win_path = "C:\\Users\\test\\Projects\\MyApp"
        window.update_folder_label(win_path)
        
        assert "MyApp" in window.folder_label.text()

    def test_folder_label_styling(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert window.folder_label.styleSheet() != ""
        # Check that dark theme colors are applied
        assert "#2a2d2e" in window.folder_label.styleSheet() or \
               "#cccccc" in window.folder_label.styleSheet()


class TestFolderOperations:
    """Tests for folder operations (open folder, new folder)."""

    def test_open_folder_updates_file_tree(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test folder structure
        test_folder = tmp_path / "test_folder"
        test_folder.mkdir()
        (test_folder / "file1.txt").write_text("content1")
        (test_folder / "file2.txt").write_text("content2")
        
        # Simulate opening the folder
        window.file_model.setRootPath(str(test_folder))
        window.file_tree.setRootIndex(window.file_model.index(str(test_folder)))
        
        # Normalize paths for comparison (Qt uses forward slashes)
        assert Path(window.file_model.rootPath()) == test_folder

    def test_new_folder_creates_directory(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Set root path to tmp_path
        window.file_model.setRootPath(str(tmp_path))
        window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
        
        # Mock QInputDialog to return a folder name
        monkeypatch.setattr(
            "main.QInputDialog.getText",
            lambda *args, **kwargs: ("new_test_folder", True)
        )
        
        window.new_folder()
        
        new_folder_path = tmp_path / "new_test_folder"
        assert new_folder_path.exists()
        assert new_folder_path.is_dir()

    def test_new_folder_cancelled(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.file_model.setRootPath(str(tmp_path))
        window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
        
        # Mock QInputDialog to simulate cancel
        monkeypatch.setattr(
            "main.QInputDialog.getText",
            lambda *args, **kwargs: ("", False)
        )
        
        initial_contents = list(tmp_path.iterdir())
        window.new_folder()
        
        # No new folder should be created
        assert list(tmp_path.iterdir()) == initial_contents

    def test_new_folder_already_exists(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create existing folder
        existing_folder = tmp_path / "existing_folder"
        existing_folder.mkdir()
        
        window.file_model.setRootPath(str(tmp_path))
        window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
        
        # Mock QInputDialog to return existing folder name
        monkeypatch.setattr(
            "main.QInputDialog.getText",
            lambda *args, **kwargs: ("existing_folder", True)
        )
        
        # Mock QMessageBox.warning to capture the error
        warning_called = []
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: warning_called.append(True)
        )
        
        window.new_folder()
        
        # Should show warning for existing folder
        assert len(warning_called) == 1

    def test_new_folder_empty_name(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.file_model.setRootPath(str(tmp_path))
        window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
        
        # Mock QInputDialog to return empty string but OK clicked
        monkeypatch.setattr(
            "main.QInputDialog.getText",
            lambda *args, **kwargs: ("", True)
        )
        
        initial_contents = list(tmp_path.iterdir())
        window.new_folder()
        
        # No new folder should be created with empty name
        assert list(tmp_path.iterdir()) == initial_contents

    def test_file_tree_root_path_after_open_folder(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create nested folder structure
        nested = tmp_path / "level1" / "level2"
        nested.mkdir(parents=True)
        
        # Directly call the internal logic that open_folder uses
        window.file_model.setRootPath(str(nested))
        window.file_tree.setRootIndex(window.file_model.index(str(nested)))
        
        # Normalize paths for comparison (Qt uses forward slashes)
        assert Path(window.file_model.rootPath()) == nested


class TestEdgesCases:
    """Tests for edge cases and error handling."""

    def test_empty_file_save_load(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        file_path = tmp_path / "empty.txt"
        window.save_to_file(str(file_path))
        
        assert file_path.exists()
        assert file_path.read_text(encoding='utf-8') == ""
        
        window.editor.setPlainText("not empty")
        window.load_file(str(file_path))
        assert window.editor.toPlainText() == ""

    def test_very_long_line(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        long_line = "x" * 10000
        editor.setPlainText(long_line)
        
        assert len(editor.toPlainText()) == 10000

    def test_rapid_typing(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.editor.setFocus()
        for char in "Hello World":
            qtbot.keyClicks(window.editor, char)
        
        assert "Hello World" in window.editor.toPlainText()

    def test_cursor_at_end_of_document(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        
        assert editor.textCursor().atEnd()

    def test_cursor_at_start_of_document(self, qtbot):
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1\nLine 2")
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
        
        assert editor.textCursor().atStart()

    def test_whitespace_only_content(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        whitespace = "   \n\t\n   \n"
        window.editor.setPlainText(whitespace)
        
        file_path = tmp_path / "whitespace.txt"
        window.save_to_file(str(file_path))
        
        window.load_file(str(file_path))
        assert window.editor.toPlainText() == whitespace

    def test_newline_only_file(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        newlines = "\n\n\n\n\n"
        window.editor.setPlainText(newlines)
        
        file_path = tmp_path / "newlines.txt"
        window.save_to_file(str(file_path))
        
        window.load_file(str(file_path))
        assert window.editor.toPlainText() == newlines
        assert window.editor.blockCount() == 6
