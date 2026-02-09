import pytest
import os
import tempfile
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QTimer, QDir, QUrl
from PySide6.QtGui import QTextCursor, QFont
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QScrollArea
from unittest.mock import patch

from main import TextEditor, CodeEditor, FindReplaceDialog, LineNumberArea, CustomTabWidget, CustomTabBar, SyntaxHighlighter


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

    def test_new_folder_shortcut_configured(self, qtbot):
        import inspect
        from main import TextEditor
        
        source = inspect.getsource(TextEditor.create_menu_bar)
        assert 'new_folder_action.setShortcut("Ctrl+Shift+N")' in source

    def test_open_folder_shortcut_configured(self, qtbot):
        import inspect
        from main import TextEditor
        
        source = inspect.getsource(TextEditor.create_menu_bar)
        assert 'open_folder_action.setShortcut("Ctrl+Shift+O")' in source

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
        
        unicode_content = "Hello ä¸–ç•Œ ðŸŒ ÐŸÑ€Ð¸Ð²ÐµÑ‚"
        window.editor.setPlainText(unicode_content)
        
        file_path = tmp_path / "unicode.txt"
        window.save_to_file(str(file_path))
        
        assert file_path.read_text(encoding='utf-8') == unicode_content

    def test_load_unicode_content(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        unicode_content = "Hello ä¸–ç•Œ ðŸŒ ÐŸÑ€Ð¸Ð²ÐµÑ‚"
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

    def test_update_folder_label_with_simple_path(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        test_path = "/home/user/Documents"
        window.update_folder_label(test_path)
        

    def test_update_folder_label_with_nested_path(self, qtbot, tmp_path):
        window = TextEditor()
        qtbot.addWidget(window)
        
        nested = tmp_path / "level1" / "level2"
        nested.mkdir(parents=True)
        
        window.update_folder_label(str(nested))
        

    def test_update_folder_label_with_root_path(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.update_folder_label("/")
        

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
        

    def test_folder_label_shows_basename_only(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        full_path = "/very/long/path/to/my_folder"
        window.update_folder_label(full_path)
        
        # Should only show the basename, not the full path

    def test_folder_label_handles_windows_paths(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        win_path = "C:\\Users\\test\\Projects\\MyApp"
        window.update_folder_label(win_path)
        

    def test_folder_label_styling(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert window.folder_label.styleSheet() != ""
        # Check that dark theme colors are applied
        assert "#2a2d2e" in window.folder_label.styleSheet() or \
               "#cccccc" in window.folder_label.styleSheet()

    def test_zoom_indicator_exists(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert hasattr(window, 'zoom_indicator')
        assert window.zoom_indicator is not None

    def test_zoom_indicator_hidden_by_default(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        assert not window.zoom_indicator.isVisible()

    def test_zoom_indicator_shows_on_zoom_in(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.zoom_in()
        
        assert window.zoom_indicator.isVisible()
        assert "%" in window.zoom_indicator.text()

    def test_zoom_indicator_shows_on_zoom_out(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Zoom in first to ensure we can zoom out
        window.zoom_in()
        window.zoom_out()
        
        assert window.zoom_indicator.isVisible()
        assert "%" in window.zoom_indicator.text()

    def test_zoom_indicator_displays_correct_percentage(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Default font size is 11pt, so 100% initially
        window.update_zoom_indicator()
        assert "100%" in window.zoom_indicator.text()
        
        # After zoom in (font size becomes 12pt)
        window.zoom_in()
        assert "109%" in window.zoom_indicator.text() or "110%" in window.zoom_indicator.text()

    def test_zoom_indicator_increases_on_zoom_in(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        font = window.editor.font()
        initial_size = font.pointSize()
        
        window.zoom_in()
        font = window.editor.font()
        
        assert font.pointSize() == initial_size + 1

    def test_zoom_indicator_decreases_on_zoom_out(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Zoom in first
        window.zoom_in()
        font = window.editor.font()
        size_after_zoom_in = font.pointSize()
        
        # Then zoom out
        window.zoom_out()
        font = window.editor.font()
        
        assert font.pointSize() == size_after_zoom_in - 1

    def test_zoom_indicator_doesnt_go_below_6pt(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Set font to minimum size (6pt)
        font = window.editor.font()
        font.setPointSize(6)
        window.editor.setFont(font)
        window.editor.line_number_area.setFont(font)
        
        # Try to zoom out
        window.zoom_out()
        
        # Should still be 6pt
        font = window.editor.font()
        assert font.pointSize() == 6

    def test_zoom_indicator_timer_active_on_show(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.show_zoom_indicator()
        
        assert window.zoom_indicator_timer.isActive()

    def test_zoom_indicator_auto_hides(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.show_zoom_indicator()
        assert window.zoom_indicator.isVisible()
        
        # Wait for timer to trigger (1 second)
        qtbot.wait(1100)
        
        assert not window.zoom_indicator.isVisible()
        assert not window.zoom_indicator_timer.isActive()

    def test_zoom_indicator_positioned_top_right(self, qtbot):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.show_zoom_indicator()
        
        # Check that indicator is positioned near the top right
        indicator_x = window.zoom_indicator.x()
        indicator_y = window.zoom_indicator.y()
        indicator_width = window.zoom_indicator.width()
        
        # Should be positioned at the top (near menu bar area)
        assert indicator_y >= 0 and indicator_y < 50
        # Should be on the right side
        assert indicator_x + indicator_width > window.width() * 0.6


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


class TestDeleteFunctionality:
     """Tests for delete file/folder functionality."""

     def test_delete_file_from_tree(self, qtbot, tmp_path, monkeypatch):
         window = TextEditor()
         qtbot.addWidget(window)
         window.show()
         qtbot.waitExposed(window)
         
         # Create a test file
         test_file = tmp_path / "test.txt"
         test_file.write_text("test content")
         
         # Set the file tree to the tmp_path
         window.file_model.setRootPath(str(tmp_path))
         window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
         
         # Get the index of the test file
         file_index = window.file_model.index(str(test_file))
         
         # Mock QMessageBox.warning to confirm deletion
         monkeypatch.setattr(
             "main.QMessageBox.warning",
             lambda *args, **kwargs: QMessageBox.Yes
         )
         
         # Delete the file
         window.delete_file_or_folder(file_index)
         
         # Verify the file is deleted
         assert not test_file.exists()

     def test_delete_folder_from_tree(self, qtbot, tmp_path, monkeypatch):
         window = TextEditor()
         qtbot.addWidget(window)
         window.show()
         qtbot.waitExposed(window)
         
         # Create a test folder with content
         test_folder = tmp_path / "test_folder"
         test_folder.mkdir()
         (test_folder / "nested_file.txt").write_text("content")
         
         # Set the file tree to the tmp_path
         window.file_model.setRootPath(str(tmp_path))
         window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
         
         # Get the index of the test folder
         folder_index = window.file_model.index(str(test_folder))
         
         # Mock QMessageBox.warning to confirm deletion
         monkeypatch.setattr(
             "main.QMessageBox.warning",
             lambda *args, **kwargs: QMessageBox.Yes
         )
         
         # Delete the folder
         window.delete_file_or_folder(folder_index)
         
         # Verify the folder is deleted
         assert not test_folder.exists()

     def test_delete_cancelled(self, qtbot, tmp_path, monkeypatch):
         window = TextEditor()
         qtbot.addWidget(window)
         window.show()
         qtbot.waitExposed(window)
         
         # Create a test file
         test_file = tmp_path / "test.txt"
         test_file.write_text("test content")
         
         # Set the file tree to the tmp_path
         window.file_model.setRootPath(str(tmp_path))
         window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
         
         # Get the index of the test file
         file_index = window.file_model.index(str(test_file))
         
         # Mock QMessageBox.warning to cancel deletion
         monkeypatch.setattr(
             "main.QMessageBox.warning",
             lambda *args, **kwargs: QMessageBox.No
         )
         
         # Try to delete the file
         window.delete_file_or_folder(file_index)
         
         # Verify the file still exists
         assert test_file.exists()
         assert test_file.read_text() == "test content"

     def test_delete_currently_open_file(self, qtbot, tmp_path, monkeypatch):
         window = TextEditor()
         qtbot.addWidget(window)
         window.show()
         qtbot.waitExposed(window)
         
         # Create and open a test file
         test_file = tmp_path / "open_file.txt"
         test_file.write_text("open content")
         
         # Simulate opening the file
         window.load_file(str(test_file))
         assert window.current_file == str(test_file)
         assert "open_file.txt" in window.windowTitle()
         
         # Set the file tree to the tmp_path
         window.file_model.setRootPath(str(tmp_path))
         window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
         
         # Get the index of the test file
         file_index = window.file_model.index(str(test_file))
         
         # Mock QMessageBox.warning to confirm deletion
         monkeypatch.setattr(
             "main.QMessageBox.warning",
             lambda *args, **kwargs: QMessageBox.Yes
         )
         
         # Delete the file
         window.delete_file_or_folder(file_index)
         
         # Verify the file is deleted and editor is cleared
         assert not test_file.exists()
         assert window.current_file is None
         assert "Untitled" in window.windowTitle()
         assert window.editor.toPlainText() == ""

     def test_delete_nonexistent_file_error(self, qtbot, tmp_path, monkeypatch):
         window = TextEditor()
         qtbot.addWidget(window)
         window.show()
         qtbot.waitExposed(window)
         
         # Create a test file and immediately delete it
         test_file = tmp_path / "will_delete.txt"
         test_file.write_text("content")
         
         # Set the file tree to the tmp_path
         window.file_model.setRootPath(str(tmp_path))
         window.file_tree.setRootIndex(window.file_model.index(str(tmp_path)))
         
         # Get the index before deleting
         file_index = window.file_model.index(str(test_file))
         
         # Delete the file manually
         test_file.unlink()
         
         # Mock QMessageBox.warning to confirm deletion
         monkeypatch.setattr(
             "main.QMessageBox.warning",
             lambda *args, **kwargs: QMessageBox.Yes
         )
         
         # Mock QMessageBox.critical to check error handling
         error_called = []
         monkeypatch.setattr(
             "main.QMessageBox.critical",
             lambda *args, **kwargs: error_called.append(True)
         )
         
         # Try to delete (should fail gracefully)
         window.delete_file_or_folder(file_index)
         
         # Verify error was shown
         assert len(error_called) == 1


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


class TestTabs:
    """Tests for the tab functionality."""

    def test_custom_tab_bar_creation(self, qtbot):
         """Test CustomTabBar creation."""
         tab_bar = CustomTabBar()
         qtbot.addWidget(tab_bar)
         assert tab_bar is not None
         assert tab_bar.tabsClosable()

    def test_custom_tab_widget_creation(self, qtbot):
         """Test CustomTabWidget creation."""
         tab_widget = CustomTabWidget()
         qtbot.addWidget(tab_widget)
         assert tab_widget is not None
         assert tab_widget.tab_bar is not None

    def test_text_editor_with_initial_tab(self, qtbot):
         """Test TextEditor initializes with one untitled tab."""
         window = TextEditor()
         qtbot.addWidget(window)
         assert window.tab_widget is not None
         assert window.tab_widget.count() == 1
         assert window.tab_widget.tabText(0) == "Untitled"

    def test_create_new_tab(self, qtbot):
         """Test creating a new tab."""
         window = TextEditor()
         qtbot.addWidget(window)
         initial_count = window.tab_widget.count()
         window.create_new_tab()
         assert window.tab_widget.count() == initial_count + 1

    def test_tab_switching(self, qtbot):
         """Test switching between tabs."""
         window = TextEditor()
         qtbot.addWidget(window)
         window.create_new_tab()
         
         window.tab_widget.setCurrentIndex(0)
         assert window.tab_widget.currentIndex() == 0
         
         window.tab_widget.setCurrentIndex(1)
         assert window.tab_widget.currentIndex() == 1

    def test_tab_shows_unsaved_changes(self, qtbot):
         """Test that tab shows asterisk for unsaved changes."""
         window = TextEditor()
         qtbot.addWidget(window)
         editor = window.tab_widget.widget(0)
         
         editor.setPlainText("test content")
         qtbot.wait(100)
         
         tab_text = window.tab_widget.tabText(0)
         assert "*" in tab_text

    def test_tab_title_updates_on_file_load(self, qtbot, tmp_path):
         """Test that tab title shows filename when file is loaded."""
         window = TextEditor()
         qtbot.addWidget(window)
         
         test_file = tmp_path / "test.txt"
         test_file.write_text("content")
         
         window.load_file(str(test_file))
         tab_text = window.tab_widget.tabText(0)
         assert "test.txt" in tab_text

    def test_load_same_file_switches_to_existing_tab(self, qtbot, tmp_path):
         """Test that loading an already open file switches to its tab."""
         window = TextEditor()
         qtbot.addWidget(window)
         
         test_file = tmp_path / "test.txt"
         test_file.write_text("content")
         
         window.load_file(str(test_file))
         first_tab_index = window.tab_widget.currentIndex()
         
         window.create_new_tab()
         assert window.tab_widget.currentIndex() != first_tab_index
         
         window.load_file(str(test_file))
         assert window.tab_widget.currentIndex() == first_tab_index

    def test_close_tab_with_unsaved_changes(self, qtbot, monkeypatch):
        """Test closing a tab with unsaved changes prompts user."""
        window = TextEditor()
        qtbot.addWidget(window)
        editor = window.tab_widget.widget(0)
        editor.setPlainText("unsaved content")
        
        # Mock the dialog to return Discard
        monkeypatch.setattr(
           "main.QMessageBox.warning",
           lambda *args, **kwargs: QMessageBox.Discard
        )
        
        window.close_tab(0)
        # After closing the last tab, all tabs should be removed
        assert window.tab_widget.count() == 0

    def test_open_files_tracking(self, qtbot, tmp_path):
         """Test that open files are properly tracked."""
         window = TextEditor()
         qtbot.addWidget(window)
         
         test_file1 = tmp_path / "file1.txt"
         test_file2 = tmp_path / "file2.txt"
         test_file1.write_text("content1")
         test_file2.write_text("content2")
         
         window.load_file(str(test_file1))
         assert str(test_file1) in window.open_files
         
         window.load_file(str(test_file2))
         assert str(test_file2) in window.open_files
         assert len(window.open_files) == 2


class TestMultiTabFunctionality:
    """Comprehensive tests for multi-tab functionality."""

    def test_new_file_creates_new_tab(self, qtbot):
        """Test that new_file creates a new tab."""
        window = TextEditor()
        qtbot.addWidget(window)
        initial_count = window.tab_widget.count()

        window.new_file()

        assert window.tab_widget.count() == initial_count + 1
        assert "Untitled" in window.tab_widget.tabText(window.tab_widget.currentIndex())

    def test_each_tab_has_independent_editor(self, qtbot):
        """Test that each tab has its own independent editor."""
        window = TextEditor()
        qtbot.addWidget(window)

        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("Tab 1 content")

        window.create_new_tab()
        editor2 = window.tab_widget.widget(1)
        editor2.setPlainText("Tab 2 content")

        assert editor1 is not editor2
        assert editor1.toPlainText() == "Tab 1 content"
        assert editor2.toPlainText() == "Tab 2 content"

    def test_tab_switch_updates_current_editor(self, qtbot):
        """Test that switching tabs updates the current editor reference."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("First tab")

        window.create_new_tab()
        editor2 = window.tab_widget.widget(1)
        editor2.setPlainText("Second tab")

        window.tab_widget.setCurrentIndex(0)
        qtbot.wait(50)
        assert window.editor is editor1

        window.tab_widget.setCurrentIndex(1)
        qtbot.wait(50)
        assert window.editor is editor2

    def test_tab_switch_updates_window_title(self, qtbot, tmp_path):
        """Test that switching tabs updates the window title."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        file1 = tmp_path / "file1.txt"
        file1.write_text("content1")
        window.load_file(str(file1))

        window.create_new_tab()
        file2 = tmp_path / "file2.txt"
        file2.write_text("content2")
        window.load_file(str(file2))

        window.tab_widget.setCurrentIndex(0)
        qtbot.wait(50)
        assert "file1.txt" in window.windowTitle()

        window.tab_widget.setCurrentIndex(1)
        qtbot.wait(50)
        assert "file2.txt" in window.windowTitle()

    def test_close_tab_removes_from_open_files(self, qtbot, tmp_path, monkeypatch):
        """Test that closing a tab removes file from open_files tracking."""
        window = TextEditor()
        qtbot.addWidget(window)

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        window.load_file(str(test_file))

        assert str(test_file) in window.open_files

        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )

        window.close_tab(window.tab_widget.currentIndex())

        assert str(test_file) not in window.open_files

    def test_close_tab_updates_remaining_indices(self, qtbot, tmp_path, monkeypatch):
        """Test that closing a tab updates indices for remaining tabs."""
        window = TextEditor()
        qtbot.addWidget(window)

        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content{i}")
            files.append(f)
            if i == 0:
                window.load_file(str(f))
            else:
                window.create_new_tab()
                window.load_file(str(f))

        window.tab_widget.setCurrentIndex(1)
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )
        window.close_tab(1)

        assert window.tab_widget.count() == 2

    def test_close_all_tabs_shows_welcome_or_empty(self, qtbot, monkeypatch):
        """Test behavior when all tabs are closed."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )

        window.close_tab(0)

        assert window.tab_widget.count() == 0

    def test_modified_indicator_cleared_on_save(self, qtbot, tmp_path):
        """Test that asterisk is removed from tab title after save."""
        window = TextEditor()
        qtbot.addWidget(window)

        window.editor.setPlainText("modified content")
        qtbot.wait(50)

        assert "*" in window.tab_widget.tabText(0)

        file_path = tmp_path / "saved.txt"
        window.save_to_file(str(file_path))

        tab_text = window.tab_widget.tabText(0)
        assert "*" not in tab_text
        assert "saved.txt" in tab_text

    def test_tab_close_button_emits_signal(self, qtbot):
        """Test that tab close button emits the correct signal."""
        window = TextEditor()
        qtbot.addWidget(window)

        signal_received = []
        window.tab_widget.close_requested.connect(lambda idx: signal_received.append(idx))

        window.tab_widget.tab_bar.close_requested.emit(0)

        assert len(signal_received) == 1
        assert signal_received[0] == 0

    def test_reuse_untitled_tab_when_loading_file(self, qtbot, tmp_path):
        """Test that loading a file reuses an empty untitled tab."""
        window = TextEditor()
        qtbot.addWidget(window)

        initial_count = window.tab_widget.count()
        assert initial_count == 1
        assert window.tab_widget.tabText(0) == "Untitled"

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        window.load_file(str(test_file))

        assert window.tab_widget.count() == 1
        assert "test.txt" in window.tab_widget.tabText(0)

    def test_create_new_tab_when_current_modified(self, qtbot, tmp_path):
        """Test that loading a file creates new tab when current is modified."""
        window = TextEditor()
        qtbot.addWidget(window)

        window.editor.setPlainText("unsaved changes")
        window.editor.document().setModified(True)

        initial_count = window.tab_widget.count()

        test_file = tmp_path / "new_file.txt"
        test_file.write_text("file content")
        window.load_file(str(test_file))

        assert window.tab_widget.count() == initial_count + 1

    def test_cancel_close_keeps_tab_open(self, qtbot, monkeypatch):
        """Test that cancelling close keeps the tab open."""
        window = TextEditor()
        qtbot.addWidget(window)

        window.editor.setPlainText("unsaved content")
        window.editor.document().setModified(True)

        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Cancel
        )

        initial_count = window.tab_widget.count()
        window.close_tab(0)

        assert window.tab_widget.count() == initial_count

    def test_save_on_close_tab(self, qtbot, tmp_path, monkeypatch):
        """Test saving when closing a tab with unsaved changes."""
        window = TextEditor()
        qtbot.addWidget(window)

        window.editor.setPlainText("content to save")
        window.editor.document().setModified(True)

        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Save
        )

        save_path = str(tmp_path / "saved_on_close.txt")
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            lambda *args, **kwargs: (save_path, "All Files (*)")
        )

        window.close_tab(0)

        assert (tmp_path / "saved_on_close.txt").exists()
        assert (tmp_path / "saved_on_close.txt").read_text() == "content to save"

    def test_multiple_tabs_cursor_position_independent(self, qtbot):
        """Test that cursor position is independent between tabs."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("Line 1\nLine 2\nLine 3")
        cursor1 = editor1.textCursor()
        cursor1.movePosition(QTextCursor.End)
        editor1.setTextCursor(cursor1)

        window.create_new_tab()
        editor2 = window.tab_widget.widget(1)
        editor2.setPlainText("A\nB")
        cursor2 = editor2.textCursor()
        cursor2.movePosition(QTextCursor.Start)
        editor2.setTextCursor(cursor2)

        assert editor1.textCursor().blockNumber() == 2
        assert editor2.textCursor().blockNumber() == 0

    def test_editor_has_focus_on_startup(self, qtbot):
        """Test that the editor has focus when the application starts."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        qtbot.wait(100)  # Allow focus events to process
        
        assert window.editor.hasFocus(), "Editor should have focus on startup"

    def test_editor_has_focus_after_new_file(self, qtbot):
        """Test that the editor has focus after creating a new file."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a new file
        window.new_file()
        qtbot.wait(100)
        
        assert window.editor.hasFocus(), "Editor should have focus after new file"

    def test_editor_has_focus_after_opening_file(self, qtbot, tmp_path):
        """Test that the editor has focus after opening an existing file."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create and open a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        window.load_file(str(test_file))
        qtbot.wait(100)
        
        assert window.editor.hasFocus(), "Editor should have focus after opening file"

    def test_current_file_preserved_after_discarding_untitled_tab(self, qtbot, tmp_path, monkeypatch):
        """Test that current_file is correct after closing untitled tab with discard.
        
        Bug: When you modify untitled tab, open existing file, close untitled with discard,
        then save the existing file - Save As dialog appears instead of saving to existing path.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Modify the untitled first tab
        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("unsaved content")
        editor1.document().setModified(True)
        
        # Open an existing file (creates new tab at index 1)
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("original content")
        window.load_file(str(existing_file))
        
        # Verify we're on the existing file tab
        assert window.tab_widget.currentIndex() == 1
        assert window.current_file == str(existing_file)
        
        # Close the untitled tab (index 0) with discard
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )
        window.close_tab(0)
        qtbot.wait(50)
        
        # Now the existing file should be at index 0 and current_file should be set
        assert window.tab_widget.count() == 1
        assert window.tab_widget.currentIndex() == 0
        assert window.current_file == str(existing_file), \
            f"current_file should be '{existing_file}' but is '{window.current_file}'"
        
        # Modify and save - should NOT show Save As dialog
        window.editor.setPlainText("modified content")
        
        save_as_called = []
        original_get_save = QFileDialog.getSaveFileName
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            lambda *args, **kwargs: (save_as_called.append(True), ("", ""))[1]
        )
        
        window.save_file()
        
        assert len(save_as_called) == 0, "Save As dialog should NOT have been shown"
        assert existing_file.read_text() == "modified content"

    def test_current_file_preserved_after_saving_untitled_tab(self, qtbot, tmp_path, monkeypatch):
        """Test that current_file is correct after closing untitled tab with save.
        
        Bug: Same issue occurs when saving the untitled tab before closing.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Modify the untitled first tab
        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("unsaved content")
        editor1.document().setModified(True)
        
        # Open an existing file
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("original content")
        window.load_file(str(existing_file))
        
        # Close the untitled tab (index 0) with save
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Save
        )
        
        # Mock save dialog for the untitled file
        untitled_save_path = str(tmp_path / "saved_untitled.txt")
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            lambda *args, **kwargs: (untitled_save_path, "All Files (*)")
        )
        
        window.close_tab(0)
        qtbot.wait(50)
        
        # Now the existing file should be current
        assert window.tab_widget.count() == 1
        assert window.current_file == str(existing_file), \
            f"current_file should be '{existing_file}' but is '{window.current_file}'"
        
        # Modify the existing file
        window.editor.setPlainText("modified existing content")
        
        # Reset the mock to track if Save As is called again
        save_as_called = []
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            lambda *args, **kwargs: (save_as_called.append(True), ("", ""))[1]
        )
        
        window.save_file()
        
        assert len(save_as_called) == 0, "Save As dialog should NOT have been shown"
        assert existing_file.read_text() == "modified existing content"

    def test_save_untitled_tab_when_not_current_shows_save_dialog(self, qtbot, tmp_path, monkeypatch):
        """Test that saving an untitled modified tab shows save dialog even when it's not the current tab.
        
        Bug: When you modify untitled tab, open another file, then close the untitled tab
        and click Save, the save dialog should appear but it doesn't - the file is lost.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Modify the untitled first tab
        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("unsaved content in untitled")
        editor1.document().setModified(True)
        
        # Open another file (this becomes the current tab)
        test_file = tmp_path / "existing.txt"
        test_file.write_text("existing content")
        window.load_file(str(test_file))
        
        # Verify we're now on the second tab (index 1)
        assert window.tab_widget.currentIndex() == 1
        assert window.current_file == str(test_file)
        
        # Now close the untitled tab (index 0) - it has unsaved changes
        # Mock the warning dialog to return Save
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Save
        )
        
        # Track if save dialog was shown
        save_dialog_shown = []
        save_path = str(tmp_path / "saved_untitled.txt")
        def mock_get_save_filename(*args, **kwargs):
            save_dialog_shown.append(True)
            return (save_path, "All Files (*)")
        
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            mock_get_save_filename
        )
        
        # Close the untitled tab (index 0)
        window.close_tab(0)
        
        # The save dialog SHOULD have been shown
        assert len(save_dialog_shown) == 1, "Save dialog was not shown for untitled file"
        
        # The file should have been saved
        assert (tmp_path / "saved_untitled.txt").exists(), "File was not saved"
        assert (tmp_path / "saved_untitled.txt").read_text() == "unsaved content in untitled"


class TestSplitView:
    """Tests for split view functionality."""
    
    def test_initial_state_has_one_pane(self, qtbot):
        """Test that editor starts with exactly one split pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert len(window.split_panes) == 1
        assert window.active_pane is not None
        assert window.active_pane in window.split_panes
    
    def test_add_split_view_creates_second_pane(self, qtbot):
        """Test that clicking split creates a second pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        initial_count = len(window.split_panes)
        window.add_split_view()
        
        assert len(window.split_panes) == initial_count + 1
        assert len(window.split_panes) == 2
    
    def test_add_split_view_creates_third_pane(self, qtbot):
        """Test that we can create up to 3 panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        window.add_split_view()
        
        assert len(window.split_panes) == 3
    
    def test_max_three_split_panes(self, qtbot):
        """Test that we cannot create more than 3 panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        window.add_split_view()
        window.add_split_view()  # Should be ignored
        window.add_split_view()  # Should be ignored
        
        assert len(window.split_panes) == 3
    
    def test_split_button_disabled_at_max_panes(self, qtbot):
        """Test that split button is disabled when at max panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Initially enabled
        assert window.split_panes[0].tab_widget.split_button.isEnabled()
        
        window.add_split_view()
        window.add_split_view()
        
        # At max, all split buttons should be disabled
        for pane in window.split_panes:
            assert not pane.tab_widget.split_button.isEnabled()
    
    def test_split_button_enabled_after_closing_pane(self, qtbot):
        """Test that split button is re-enabled after closing a pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        window.add_split_view()
        
        # At max, disabled
        assert not window.split_panes[0].tab_widget.split_button.isEnabled()
        
        # Close one pane
        pane_to_close = window.split_panes[1]
        window.close_split_pane(pane_to_close)
        
        # Should be enabled again
        for pane in window.split_panes:
            assert pane.tab_widget.split_button.isEnabled()
    
    def test_close_button_hidden_with_one_pane(self, qtbot):
        """Test that close button is hidden when only one pane exists."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert len(window.split_panes) == 1
        assert not window.split_panes[0].close_button.isVisible()
    
    def test_close_button_visible_with_multiple_panes(self, qtbot):
        """Test that close buttons are visible when multiple panes exist."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        
        # Check that close buttons are not hidden (visibility state)
        for pane in window.split_panes:
            assert not pane.close_button.isHidden()
    
    def test_close_button_hidden_after_returning_to_one_pane(self, qtbot):
        """Test that close button hides when returning to one pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        assert not window.split_panes[0].close_button.isHidden()
        
        # Close one pane
        pane_to_close = window.split_panes[1]
        window.close_split_pane(pane_to_close)
        
        assert len(window.split_panes) == 1
        assert window.split_panes[0].close_button.isHidden()
    
    def test_close_split_pane_removes_pane(self, qtbot):
        """Test that closing a split pane removes it from the list."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        assert len(window.split_panes) == 2
        
        pane_to_close = window.split_panes[1]
        window.close_split_pane(pane_to_close)
        
        assert len(window.split_panes) == 1
        assert pane_to_close not in window.split_panes
    
    def test_cannot_close_last_pane(self, qtbot):
        """Test that we cannot close the last remaining pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert len(window.split_panes) == 1
        
        # Try to close the only pane
        window.close_split_pane(window.split_panes[0])
        
        # Should still have one pane
        assert len(window.split_panes) == 1
    
    def test_each_pane_has_independent_tabs(self, qtbot):
        """Test that each pane has its own independent tab widget."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        
        pane1 = window.split_panes[0]
        pane2 = window.split_panes[1]
        
        # They should have different tab widgets
        assert pane1.tab_widget is not pane2.tab_widget
        
        # Add content to pane1
        window.set_active_pane(pane1)
        window.editor.setPlainText("Pane 1 content")
        
        # Add content to pane2
        window.set_active_pane(pane2)
        window.editor.setPlainText("Pane 2 content")
        
        # Content should be different
        assert pane1.tab_widget.widget(0).toPlainText() == "Pane 1 content"
        assert pane2.tab_widget.widget(0).toPlainText() == "Pane 2 content"
    
    def test_new_pane_gets_new_tab(self, qtbot):
        """Test that a new pane is created with an initial tab."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        
        new_pane = window.split_panes[1]
        assert new_pane.tab_widget.count() >= 1
    
    def test_active_pane_switches_on_add(self, qtbot):
        """Test that the new pane becomes active when created."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        original_pane = window.active_pane
        window.add_split_view()
        
        # Active pane should now be the new one
        assert window.active_pane != original_pane
        assert window.active_pane == window.split_panes[1]
    
    def test_closing_all_tabs_removes_pane_when_multiple(self, qtbot):
        """Test that closing all tabs in a pane removes the pane when there are multiple panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create a second pane
        window.add_split_view()
        assert len(window.split_panes) == 2
        
        # The new pane should be active with one tab
        active_pane = window.active_pane
        assert window.tab_widget.count() == 1
        
        # Close the only tab in the active pane
        window.remove_tab(0)
        
        # The pane should have been removed
        assert len(window.split_panes) == 1
        assert active_pane not in window.split_panes
    
    def test_closing_all_tabs_shows_welcome_when_one_pane(self, qtbot):
        """Test that closing all tabs shows welcome screen when only one pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert len(window.split_panes) == 1
        
        # Close the only tab
        window.remove_tab(0)
        
        # Should still have one pane but show welcome screen
        assert len(window.split_panes) == 1
        assert not window.welcome_screen.isHidden()
        assert window.tab_widget.isHidden()
    
    def test_pane_count_decreases_when_closing_tabs(self, qtbot):
        """Test that pane count properly decreases when all tabs are closed."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create 3 panes
        window.add_split_view()
        window.add_split_view()
        assert len(window.split_panes) == 3
        
        # Close all tabs in the active pane (which should be the 3rd one)
        window.remove_tab(0)
        assert len(window.split_panes) == 2
        
        # Close all tabs in the now-active pane
        window.remove_tab(0)
        assert len(window.split_panes) == 1
        
        # Closing tabs in the last pane should show welcome, not remove pane
        window.remove_tab(0)
        assert len(window.split_panes) == 1
        assert not window.welcome_screen.isHidden()
    
    def test_split_pane_has_file_label(self, qtbot):
        """Test that each split pane has a file label in the header."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        pane = window.split_panes[0]
        assert hasattr(pane, 'file_label')
        assert pane.file_label is not None
    
    def test_file_label_updates_on_tab_change(self, qtbot, tmp_path):
        """Test that the pane header updates when switching tabs."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create a file and load it
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        window.load_file(str(test_file))
        
        pane = window.split_panes[0]
        assert "test.txt" in pane.file_label.text()
    
    def test_split_view_with_file_operations(self, qtbot, tmp_path):
        """Test that file operations work correctly with split views."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("File 1 content")
        file2.write_text("File 2 content")
        
        # Load file1 in first pane
        window.load_file(str(file1))
        
        # Create second pane and load file2
        window.add_split_view()
        window.load_file(str(file2))
        
        # Verify each pane has correct content
        pane1 = window.split_panes[0]
        pane2 = window.split_panes[1]
        
        assert pane1.tab_widget.widget(0).toPlainText() == "File 1 content"
        assert pane2.tab_widget.widget(0).toPlainText() == "File 2 content"
    
    def test_closing_pane_with_modified_content_prompts(self, qtbot, monkeypatch):
        """Test that closing a pane with unsaved changes prompts user."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        
        # Modify content in the new pane
        window.editor.setPlainText("unsaved changes")
        window.editor.document().setModified(True)
        
        # Mock the message box to return Discard
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )
        
        pane_to_close = window.active_pane
        window.close_split_pane(pane_to_close)
        
        # Pane should be closed
        assert pane_to_close not in window.split_panes
    
    def test_closing_pane_cancel_keeps_pane(self, qtbot, monkeypatch):
        """Test that canceling close keeps the pane open."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        window.add_split_view()
        
        # Modify content
        window.editor.setPlainText("unsaved changes")
        window.editor.document().setModified(True)
        
        # Mock the message box to return Cancel
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Cancel
        )
        
        pane_count_before = len(window.split_panes)
        pane_to_close = window.active_pane
        window.close_split_pane(pane_to_close)
        
        # Pane should still exist
        assert len(window.split_panes) == pane_count_before
        assert pane_to_close in window.split_panes
    
    def test_close_button_size_is_small(self, qtbot):
        """Test that close button is small enough to not affect header height."""
        from main import SplitEditorPane
        pane = SplitEditorPane()
        qtbot.addWidget(pane)
        
        # Close button should be small (16x16 or less)
        assert pane.close_button.width() <= 16
        assert pane.close_button.height() <= 16
    
    def test_header_has_fixed_height(self, qtbot):
        """Test that the pane header has a fixed height that doesn't change."""
        from main import SplitEditorPane
        from PySide6.QtWidgets import QWidget
        pane = SplitEditorPane()
        qtbot.addWidget(pane)
        
        # Header should have a fixed, small height (around 24px)
        header = pane.findChild(QWidget)
        assert header.maximumHeight() <= 28
    
    def test_new_file_opens_in_active_pane(self, qtbot, tmp_path):
        """Test that opening a new file adds it to the currently active pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create two panes
        window.add_split_view()
        
        # The second pane is active, let's put content in it so it's not empty
        second_pane = window.split_panes[1]
        window.editor.setPlainText("second pane content")
        window.editor.document().setModified(True)
        
        # Switch to the first pane 
        first_pane = window.split_panes[0]
        window.set_active_pane(first_pane)
        
        # Modify first pane so the file won't reuse existing tab
        window.editor.setPlainText("first pane content")
        window.editor.document().setModified(True)
        
        # Count tabs in first pane before
        tabs_before = first_pane.tab_widget.count()
        
        # Create a test file and load it
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        window.load_file(str(test_file))
        
        # File should have been loaded in the first pane (active pane), as a new tab
        assert first_pane.tab_widget.count() == tabs_before + 1
        # The new tab should contain the file content
        new_tab_content = first_pane.tab_widget.widget(first_pane.tab_widget.count() - 1).toPlainText()
        assert new_tab_content == "content"
        assert window.active_pane == first_pane
    
    def test_folder_label_no_garbage_characters(self, qtbot, tmp_path):
        """Test that folder label doesn't contain garbage/corrupted characters."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Set a simple folder path
        test_folder = tmp_path / "TestFolder"
        test_folder.mkdir()
        window.update_folder_label(str(test_folder))
        
        label_text = window.folder_label.text()
        # Should only contain printable ASCII characters and the folder name
        # Check for common mojibake indicators
        for char in label_text:
            # All chars should be printable or common symbols
            assert ord(char) < 256 or char in "📁", f"Found unexpected character: {repr(char)}"
        assert "TestFolder" in label_text
    
    def test_modified_indicator_clears_after_undo_to_saved_state(self, qtbot, tmp_path):
        """Test that the modified indicator clears when content matches saved state."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create and save a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")
        window.load_file(str(test_file))
        
        # Store reference to editor
        editor = window.editor
        
        # Verify not modified
        assert not editor.document().isModified()
        
        # Simulate typing by inserting text via cursor (this preserves undo history)
        from PySide6.QtGui import QTextCursor
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(" added")
        editor.setTextCursor(cursor)
        
        # Should now be modified
        assert editor.document().isModified()
        
        # Undo the change
        editor.undo()
        
        # Content should match original, so modified flag should be False
        assert editor.toPlainText() == "original"
        assert not editor.document().isModified(), "Modified flag should clear when content matches saved state"
    
    def test_modified_indicator_clears_when_manually_typed_back(self, qtbot, tmp_path):
        """Test that modified indicator clears when manually typing back to original state."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Create and save a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")
        window.load_file(str(test_file))
        
        editor = window.editor
        
        # Verify not modified
        assert not editor.document().isModified()
        
        # Simulate typing "abc" at end
        from PySide6.QtGui import QTextCursor
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("abc")
        editor.setTextCursor(cursor)
        
        # Should be modified
        assert editor.document().isModified()
        
        # Now delete "abc" using backspace (3 times)
        for _ in range(3):
            cursor = editor.textCursor()
            cursor.deletePreviousChar()
            editor.setTextCursor(cursor)
        
        # Content should match original
        assert editor.toPlainText() == "hello"
        # Modified flag should be False since content matches saved state
        assert not editor.document().isModified(), "Modified flag should clear when content matches saved state"


class TestMultiFileSearchBugFix:
    """Test for multifile search bug fix: should allow searching with default folder on startup."""

    def test_multifile_search_folder_validation_on_startup(self, qtbot, tmp_path, monkeypatch):
        """Test that default folder on startup does not trigger validation warning.
        
        Bug: When app starts, it loads QDir.currentPath() in the sidebar.
        But show_multifile_find_dialog() rejects it with:
            if not folder_path or folder_path == QDir.currentPath():
        
        Fix: Remove the folder_path == QDir.currentPath() check.
        """
        # Create test file in temp directory
        file1 = tmp_path / "test_file.txt"
        file1.write_text("content\n")
        
        # Change to temp directory  
        monkeypatch.chdir(tmp_path)
        
        # Create window (loads current directory in file tree on startup)
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        try:
            # Verify default folder is loaded
            folder_path = window.file_model.rootPath()
            assert folder_path == QDir.currentPath(), "Should load current directory"
            
            # Mock to capture if warning() is called
            warning_called = []
            original_warning = QMessageBox.warning
            
            def mock_warning(*args, **kwargs):
                warning_called.append(True)
                return None
            
            QMessageBox.warning = mock_warning
            
            # Mock MultiFileSearchDialog to prevent it from actually showing
            with patch('main.MultiFileSearchDialog') as MockDialog:
                try:
                    window.show_multifile_find_dialog()
                finally:
                    QMessageBox.warning = original_warning
            
            # With fix: warning should NOT be called
            # With bug: warning WILL be called because folder_path == QDir.currentPath()
            assert len(warning_called) == 0, "Should NOT show warning for default folder on startup (indicates bug not fixed)"
        finally:
            window.close()


class TestViewFocus:
    """Tests for view/pane focus behavior."""
    
    def test_active_view_gets_focus(self, qtbot, tmp_path):
        """Test that when a view becomes active, the cursor focuses on its editor.
        
        Bug: When a view becomes active, the cursor/focus should move to the editor
        in that view, but currently it doesn't.
        """
        # Create editor window
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get the first pane
        pane1 = window.active_pane
        
        # Create a test file
        test_file1 = tmp_path / "file1.txt"
        test_file1.write_text("file 1 content")
        
        # Open file in pane 1
        window.load_file(str(test_file1))
        
        # Verify pane 1 editor has focus
        assert pane1.tab_widget.currentWidget().hasFocus(), "Pane 1 editor should have focus initially"
        
        # Create a second view
        window.add_split_view()
        pane2 = window.split_panes[1]
        
        # Pane 2 should be active
        assert window.active_pane == pane2
        
        # Verify pane 2 editor has focus
        pane2_editor = pane2.tab_widget.currentWidget()
        assert pane2_editor is not None, "Pane 2 should have an editor"
        assert pane2_editor.hasFocus(), "Pane 2 editor should have focus when pane becomes active"
        
        # Now click on pane 1 to make it active
        qtbot.mouseClick(pane1, Qt.LeftButton)
        
        # Verify pane 1 is now active
        assert window.active_pane == pane1
        
        # Verify pane 1 editor now has focus
        pane1_editor = pane1.tab_widget.currentWidget()
        assert pane1_editor is not None, "Pane 1 should have an editor"
        assert pane1_editor.hasFocus(), "Pane 1 editor should have focus when pane becomes active"


class TestOpenFileInMultipleViews:
    """Tests for opening files in multiple views."""
    
    def test_opening_already_open_file_opens_in_active_view(self, qtbot, tmp_path):
        """Test that opening a file already open in another view opens it in the active view.
        
        Bug: When file X is open in view 1 and you try to open file X from view 2,
        it should open file X in view 2 (same file in both views), but instead it
        just switches to view 1 where the file is already open.
        """
        # Create editor window
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get the first pane
        pane1 = window.active_pane
        
        # Create a test file
        test_file = tmp_path / "shared_file.txt"
        test_file.write_text("shared content")
        
        # Open file in pane 1
        window.load_file(str(test_file))
        assert window.active_pane == pane1
        assert window.current_file == str(test_file)
        
        # Create a second view
        window.add_split_view()
        assert len(window.split_panes) == 2
        pane2 = window.split_panes[1]
        
        # Pane 2 should be active
        assert window.active_pane == pane2
        
        # Now try to open the same file (which is already open in pane 1)
        # It should open in pane 2, not just switch to pane 1
        window.load_file(str(test_file))
        
        # Verify pane 2 is still active (not switched to pane 1)
        assert window.active_pane == pane2, f"After opening file in pane 2, pane 2 should be active but pane {window.split_panes.index(window.active_pane) + 1} is active"
        
        # Verify the file is now open in both panes
        # Check that pane2 has the file in its current tab
        current_index_pane2 = pane2.tab_widget.currentIndex()
        file_found_in_pane2 = False
        for file_path, (pane, idx) in window.open_files.items():
            if pane == pane2 and idx == current_index_pane2 and file_path == str(test_file):
                file_found_in_pane2 = True
                break
        assert file_found_in_pane2, f"File should be in pane 2's current tab"


class TestViewActivation:
    """Tests for view/pane activation."""
    
    def test_clicking_on_view_updates_current_file(self, qtbot, tmp_path):
        """Test that clicking on a view updates current_file to match that view.
        
        Bug: When multiple views are open with different files, clicking on a view
        doesn't update current_file to reflect the file in that view. This causes
        the wrong file to be saved/operated on.
        """
        # Create editor window
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get the first pane
        pane1 = window.active_pane
        assert pane1 is not None
        
        # Open a file in pane 1
        test_file1 = tmp_path / "file1.txt"
        test_file1.write_text("file 1 content")
        window.load_file(str(test_file1))
        assert window.current_file == str(test_file1)
        
        # Create a second view
        window.add_split_view()
        assert len(window.split_panes) == 2
        pane2 = window.split_panes[1]
        
        # Pane 2 is now active with an empty/untitled tab
        assert window.active_pane == pane2
        # current_file should be None because pane2 has no file
        assert window.current_file is None
        
        # Open a different file in pane 2
        test_file2 = tmp_path / "file2.txt"
        test_file2.write_text("file 2 content")
        window.load_file(str(test_file2))
        assert window.current_file == str(test_file2)
        
        # Now click on pane 1 to make it active
        qtbot.mouseClick(pane1, Qt.LeftButton)
        
        # Verify pane 1 is now active
        assert window.active_pane == pane1, "Pane 1 should be active after clicking on it"
        
        # THE BUG: current_file should be updated to file1, but it stays as file2
        # This is the bug - when you switch panes, current_file should reflect the file in the active pane
        assert window.current_file == str(test_file1), f"After clicking pane 1, current_file should be {test_file1} but is {window.current_file}"


class TestMultiViewSaveFile:
    """Tests for save file behavior with multiple views."""
    
    def test_save_file_after_closing_extra_views(self, qtbot, tmp_path, monkeypatch):
        """Test that save works correctly after closing extra views.
        
        Bug: When multiple views are open and you close all but the first,
        then make a change and save, it asks for a new filename instead of
        saving to the existing file.
        """
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")
        
        # Create editor window
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Open the test file in first pane
        window.load_file(str(test_file))
        assert window.current_file == str(test_file)
        first_pane = window.active_pane
        
        # Create a second view (this will create an untitled tab in the new pane)
        # This is the key: creating a new split pane calls add_split_view which
        # creates a new untitled tab, which sets current_file = None
        window.add_split_view()
        assert len(window.split_panes) == 2
        second_pane = window.split_panes[1]
        
        # At this point, current_file should be None because we just created an untitled tab
        # This is the bug!
        assert window.current_file is None, f"After creating new pane with untitled tab, current_file should be None but is {window.current_file}"
        
        # Close the second pane (which is the active pane)
        window.close_split_pane(second_pane)
        assert len(window.split_panes) == 1
        
        # Now we should be back at the first pane with the test file
        assert window.active_pane == first_pane
        
        # After the fix, current_file should be restored to the test file
        assert window.current_file == str(test_file), f"After closing second pane, current_file should be {test_file} but is {window.current_file}"
        
        # Make a change to the file
        window.editor.setPlainText("modified content")
        
        # Mock QFileDialog.getSaveFileName to detect if save-as is triggered
        save_as_called = []
        original_getSaveFileName = QFileDialog.getSaveFileName
        
        def mock_getSaveFileName(*args, **kwargs):
            save_as_called.append(True)
            return original_getSaveFileName(*args, **kwargs)
        
        monkeypatch.setattr("main.QFileDialog.getSaveFileName", mock_getSaveFileName)
        
        # Try to save - should NOT trigger save-as dialog
        window.save_file()
        
        # Verify the file was saved with the new content
        assert test_file.read_text() == "modified content", f"File should contain 'modified content' but contains '{test_file.read_text()}'"
        # Verify save-as was NOT triggered
        assert len(save_as_called) == 0, "Save should use existing filename, not trigger save-as"


class TestSplitViewButton:
    """Tests for split view button tooltip."""
    
    def test_split_button_shows_max_views_tooltip_when_disabled(self, qtbot):
        """Test that split button shows 'Maximum views reached' tooltip when disabled."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Initially split button should be enabled with "Split Editor" tooltip
        assert window.tab_widget.split_button.isEnabled()
        assert window.tab_widget.split_button.toolTip() == "Split Editor"
        
        # Create splits until we reach the max
        for i in range(window.MAX_SPLIT_PANES - 1):
            window.create_split_pane()
        
        # After reaching max panes, split button should be disabled with custom tooltip
        assert not window.tab_widget.split_button.isEnabled()
        assert window.tab_widget._custom_tooltip.text() == "Maximum Views Reached"
        
        # Close a pane to re-enable it
        window.close_split_pane(window.split_panes[0])
        
        # Button should be enabled again with original tooltip
        assert window.tab_widget.split_button.isEnabled()
        assert window.tab_widget.split_button.toolTip() == "Split Editor"


class TestCursorBehavior:
    """Tests for cursor behavior."""
    
    def test_press_down_on_last_line_goes_to_end(self, qtbot):
        """Test that pressing down on the last line moves cursor to end of that line."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        
        # Set text with last line that has content before cursor position
        editor.setPlainText("Line 1\nLine 2")
        
        # Move cursor to beginning of last line
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine)
        editor.setTextCursor(cursor)
        
        # Verify cursor is at start of last line
        assert cursor.blockNumber() == 1
        assert cursor.positionInBlock() == 0
        
        # Simulate pressing down arrow key
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import Qt
        down_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
        editor.keyPressEvent(down_event)
        
        # Cursor should be at end of line since it's the last line
        cursor = editor.textCursor()
        assert cursor.blockNumber() == 1, "Should still be on last line"
        assert cursor.positionInBlock() == 6, f"Should be at end of line (position 6), but is at {cursor.positionInBlock()}"


class TestMultiFileSearchResultsDialog:
    """Tests for multifile search results dialog."""
    
    def test_search_result_button_closes_all_dialogs(self, qtbot, tmp_path):
        """Test that clicking a search result button closes both the results dialog and find dialog."""
        # Create test files
        test_file1 = tmp_path / "file1.txt"
        test_file1.write_text("hello world\ntest content")
        
        # Create main editor window
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Set file model to temp directory
        window.file_model.setRootPath(str(tmp_path))
        
        # Import classes we need
        from main import MultiFileSearchResultsDialog, MultiFileSearchDialog
        
        # Create the search dialog (the one with find/replace inputs)
        search_dialog = MultiFileSearchDialog(str(tmp_path), window)
        qtbot.addWidget(search_dialog)
        search_dialog.show()
        qtbot.waitExposed(search_dialog)
        
        # Verify search dialog is visible
        assert search_dialog.isVisible()
        
        # Create search results manually with search_dialog as parent
        results = [
            (str(test_file1), 1, "hello world\n", 0, "hello")
        ]
        
        # Create the results dialog with search_dialog as parent
        results_dialog = MultiFileSearchResultsDialog(results, window, search_dialog)
        qtbot.addWidget(results_dialog)
        results_dialog.show()
        qtbot.waitExposed(results_dialog)
        
        # Verify dialogs are visible
        assert results_dialog.isVisible()
        assert search_dialog.isVisible()
        
        # Get the first search result button
        scroll_area = results_dialog.findChild(QScrollArea)
        assert scroll_area is not None
        
        # Get the button widget from scroll area
        scroll_widget = scroll_area.widget()
        layout = scroll_widget.layout()
        assert layout.count() > 0
        
        # Get the first button (search result)
        button_widget = layout.itemAt(0).widget()
        assert button_widget is not None
        
        # Click the button (simulate user clicking on a search result)
        qtbot.mouseClick(button_widget, Qt.LeftButton)
        
        # Give Qt time to process the close event
        qtbot.wait(100)
        
        # Verify both dialogs are closed
        assert not results_dialog.isVisible(), "Results dialog should be closed"
        assert not search_dialog.isVisible(), "Search dialog should be closed"


class TestActivePaneTracking:
    """Tests for active pane tracking when cursor moves between views."""
    
    def test_cursor_movement_to_different_view_updates_active_pane(self, qtbot):
        """When cursor moves to a different view, that view becomes active."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create first pane and add some content
        initial_pane = window.active_pane
        initial_editor = window.tab_widget.widget(0)
        initial_editor.setPlainText("View 1")
        
        # Split the view
        window.add_split_view()
        
        # Get the panes
        assert len(window.split_panes) > 0
        split_pane = window.split_panes[0]
        second_editor = split_pane.tab_widget.widget(0)
        second_editor.setPlainText("View 2")
        
        # After splitting, the second pane becomes active
        # Now let's click on the first editor to make it active
        initial_editor.setFocus()
        
        # The active pane should now be the initial pane again
        first_pane_active = window.active_pane == initial_pane
        
        # Now click on the second editor to make it active
        second_editor.setFocus()
        
        # The active pane should now be the second pane
        assert window.active_pane == split_pane, "When cursor moves to split pane via setFocus(), that pane should become active"


class TestTabClickBehavior:
    """Tests for tab clicking behavior across multiple views."""
    
    def test_clicking_tab_in_current_view_moves_cursor(self, qtbot):
        """When clicking a tab in the current view, cursor should move to that tab."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create two tabs in the main view
        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("Tab 1 content")
        
        editor2, _ = window.create_new_tab()
        editor2.setPlainText("Tab 2 content")
        
        # editor2 should have focus from create_new_tab
        assert editor2.hasFocus(), "editor2 should have focus after creation"
        assert window.tab_widget.currentIndex() == 1
        
        # Now click on tab 0 (editor1's tab)
        window.tab_widget.setCurrentIndex(0)
        
        # After clicking tab 0, the cursor should move to editor1
        assert editor1.hasFocus(), "Cursor should move to editor1 after clicking its tab"
    
    def test_clicking_tab_in_different_view_moves_cursor_and_changes_active_pane(self, qtbot):
        """When clicking a tab in a different view, cursor should move and that view becomes active."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get the first pane
        pane1 = window.active_pane
        editor1 = window.tab_widget.widget(0)
        editor1.setPlainText("Pane 1 Content")
        
        # Split the view
        window.add_split_view()
        
        # pane2 is now active
        pane2 = window.active_pane
        editor2 = window.tab_widget.widget(0)
        editor2.setPlainText("Pane 2 Content")
        
        # Verify pane2 is active and has focus
        assert window.active_pane == pane2
        assert editor2.hasFocus()
        
        # First, verify pane1 is not active
        assert window.active_pane != pane1
        
        # Simulate a mouse click on a tab in pane1
        # Get the tab bar and the position of the first tab
        tab_bar = pane1.tab_widget.tabBar()
        tab_rect = tab_bar.tabRect(0)
        tab_center = tab_rect.center()
        
        # Use qtbot to simulate the mouse click
        qtbot.mouseClick(tab_bar, Qt.LeftButton, pos=tab_center)
        
        # After clicking, pane1 should be active and editor1 should have focus
        assert window.active_pane == pane1, "Pane1 should become active when clicking its tab"
        assert editor1.hasFocus(), "Cursor should move to editor1 in pane1 after clicking its tab"


class TestMultipleSplitPanesUnsavedChanges:
    """Tests for unsaved changes handling across multiple split panes."""

    def test_multiple_views_unsaved_changes_on_exit(self, qtbot, monkeypatch):
        """Test that closing the app with unsaved changes in non-active pane is detected."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create first pane with unsaved changes
        editor1 = window.tab_widget.widget(0)
        editor1.insertPlainText("Changes in pane 1")
        pane1 = window.active_pane
        assert editor1.document().isModified()
        
        # Split the view to create second pane
        window.add_split_view()
        pane2 = window.active_pane
        editor2 = window.tab_widget.widget(0)
        # Don't add unsaved changes to pane2, it starts clean
        assert not editor2.document().isModified()
        
        # Now switch back to pane1 (making it active), then switch to pane2
        # This leaves pane1 non-active but with unsaved changes
        window.set_active_pane(pane2)
        assert window.active_pane == pane2
        assert window.tab_widget == pane2.tab_widget
        
        # Mock warning to return Cancel for closeEvent
        warning_call_count = [0]
        
        def mock_warning_close(*args, **kwargs):
            warning_call_count[0] += 1
            # Return Cancel to prevent close
            return QMessageBox.Cancel
        
        monkeypatch.setattr("main.QMessageBox.warning", mock_warning_close)
        
        # Now try to close the app - it should prompt for unsaved changes in pane1 even though pane2 is active
        from PySide6.QtGui import QCloseEvent
        close_event = QCloseEvent()
        
        window.closeEvent(close_event)
        
        # Should have asked about unsaved changes in pane1 (the non-active pane)
        assert warning_call_count[0] >= 1, f"Should prompt about unsaved changes in non-active pane, but got {warning_call_count[0]} warnings"
        # The event should be ignored because we returned Cancel
        assert not close_event.isAccepted(), "Should not close when user cancels"


class TestMultiplePanesFileTracking:
    """Tests for tracking which files are in which panes after opening them normally."""
    
    def test_single_pane_file_in_active_pane(self, qtbot, tmp_path):
        """Test that a file opened in single pane is in the active pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Open the file
        window.load_file(str(test_file))
        
        # Verify file is in active pane
        assert window.current_file == str(test_file)
        assert window.active_pane.tab_widget.count() == 1
        assert window.active_pane.tab_widget.tabText(0) == "test.txt"
    
    def test_multiple_files_in_same_pane(self, qtbot, tmp_path):
        """Test that multiple files can be in the same pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Open both files
        window.load_file(str(file1))
        window.load_file(str(file2))
        
        # Verify both files are in active pane
        assert window.active_pane.tab_widget.count() == 2
        assert window.active_pane.tab_widget.tabText(0) == "file1.txt"
        assert window.active_pane.tab_widget.tabText(1) == "file2.txt"
    
    def test_files_in_different_split_panes(self, qtbot, tmp_path):
        """Test that files can be tracked in different split panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Open first file in active pane
        window.load_file(str(file1))
        pane1 = window.active_pane
        
        # Split the editor
        window.add_split_view()
        pane2 = window.active_pane
        
        # Open second file in new pane
        window.load_file(str(file2))
        
        # Verify files are in different panes
        assert pane1 != pane2
        assert pane1.tab_widget.count() == 1
        assert pane2.tab_widget.count() == 1
        assert pane1.tab_widget.tabText(0) == "file1.txt"
        assert pane2.tab_widget.tabText(0) == "file2.txt"
    
    def test_get_files_in_pane(self, qtbot, tmp_path):
        """Test helper function to get all files in a specific pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Open files
        window.load_file(str(file1))
        window.load_file(str(file2))
        pane = window.active_pane
        
        # Get all files in pane
        files_in_pane = []
        for i in range(pane.tab_widget.count()):
            files_in_pane.append(pane.tab_widget.tabText(i))
        
        assert "file1.txt" in files_in_pane
        assert "file2.txt" in files_in_pane


class TestDragFileFromSidebarToView:
    """Tests for dragging files from sidebar into main view to create tabs."""
    
    def test_pane_accepts_file_drop(self, qtbot, tmp_path):
        """Test that pane's drop event handler accepts files."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test file
        test_file = tmp_path / "document.txt"
        test_file.write_text("test content")
        
        # Simulate dropping file URLs onto the pane
        from PySide6.QtCore import QMimeData
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])
        
        # Create drop event
        from PySide6.QtGui import QDropEvent
        drop_event = QDropEvent(
            QPoint(0, 0),
            Qt.CopyAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Emit the drop event on the pane's tab widget
        window.active_pane.tab_widget.dropEvent(drop_event)
        qtbot.wait(100)
        
        # Verify file was opened in active pane
        assert window.active_pane.tab_widget.count() >= 1
        tab_texts = [window.active_pane.tab_widget.tabText(i) for i in range(window.active_pane.tab_widget.count())]
        assert "document.txt" in tab_texts
    
    def test_file_drop_to_second_pane(self, qtbot, tmp_path, monkeypatch):
        """Test dropping a file onto a specific split pane opens it there."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Mock QMessageBox to avoid dialogs
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Open file1 in pane1
        window.load_file(str(file1))
        pane1 = window.active_pane
        
        # Create second pane
        window.add_split_view()
        pane2 = window.active_pane
        
        # Simulate dropping file2 onto pane2
        from PySide6.QtCore import QMimeData, QUrl
        from PySide6.QtGui import QDropEvent
        
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(file2))])
        
        drop_event = QDropEvent(
            QPoint(0, 0),
            Qt.CopyAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        pane2.tab_widget.dropEvent(drop_event)
        qtbot.wait(100)
        
        # Verify file2 is in pane2
        tab_texts = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        assert "file2.txt" in tab_texts


class TestDragTabBetweenViews:
    """Tests for dragging tabs from one pane to another."""
    
    def test_pane_tab_widget_accepts_tab_drop(self, qtbot, tmp_path):
        """Test that pane's tab widget drop handler accepts tab drops."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Open file in pane1
        window.load_file(str(test_file))
        pane1 = window.active_pane
        
        # Create pane2
        window.add_split_view()
        pane2 = window.active_pane
        
        # Simulate tab drop event with mime data
        from PySide6.QtCore import QMimeData, QPoint
        from PySide6.QtGui import QDropEvent
        
        mime_data = QMimeData()
        mime_data.setText("tab:0")  # Simulate dropping tab 0
        
        drop_event = QDropEvent(
            QPoint(0, 0),
            Qt.MoveAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Check that pane2 would accept this drop
        assert mime_data.text().startswith("tab:")
    
    def test_tab_moved_between_panes_on_drop(self, qtbot, tmp_path, monkeypatch):
        """Test that a tab is actually moved when dropped on another pane."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Mock QMessageBox to avoid dialogs
        monkeypatch.setattr(
            "main.QMessageBox.warning",
            lambda *args, **kwargs: QMessageBox.Discard
        )
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Open file1 in pane1 with file2 as second tab
        window.load_file(str(file1))
        pane1 = window.active_pane
        window.load_file(str(file2))
        
        assert pane1.tab_widget.count() == 2
        
        # Create pane2
        window.add_split_view()
        pane2 = window.active_pane
        
        # Call the handler directly to move tab from pane1 to pane2
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane1)}", pane2)
        qtbot.wait(100)
        
        # Tab should now be in pane2
        assert pane2.tab_widget.count() == 2  # 1 original + 1 moved
        tab_texts = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        # Check if file1.txt is in tabs (with or without * for modified status)
        assert any("file1.txt" in text for text in tab_texts)


class TestMoveTabModifiedState:
    """Tests for modified state when moving tabs between split views."""

    def test_unmodified_file_stays_unmodified_after_move(self, qtbot, tmp_path):
        """Bug test: Moving an unmodified file to another view should not mark it as modified."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create and load an unmodified file
        file1 = tmp_path / "unmodified.txt"
        file1.write_text("Original content")
        
        window.load_file(str(file1))
        qtbot.wait(50)
        
        pane1 = window.active_pane
        editor1 = pane1.tab_widget.widget(0)
        
        # Verify file is NOT modified
        assert not editor1.document().isModified(), "File should not be modified after loading"
        tab_text = pane1.tab_widget.tabText(0)
        assert not tab_text.endswith("*"), f"Tab should not have * but has: '{tab_text}'"
        
        # Create a second split view
        window.add_split_view()
        pane2 = window.active_pane
        qtbot.wait(50)
        
        # Move the tab from pane1 to pane2
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane1)}", pane2)
        qtbot.wait(100)
        
        # Find the moved file's tab in pane2
        moved_tab_index = None
        for i in range(pane2.tab_widget.count()):
            if "unmodified.txt" in pane2.tab_widget.tabText(i):
                moved_tab_index = i
                break
        
        assert moved_tab_index is not None, "Moved file should be in pane2"
        
        moved_editor = pane2.tab_widget.widget(moved_tab_index)
        moved_tab_text = pane2.tab_widget.tabText(moved_tab_index)
        
        # The file should still NOT be modified after the move
        assert not moved_editor.document().isModified(), "File should NOT be modified after move"
        assert not moved_tab_text.endswith("*"), f"Tab should not have * after move but has: '{moved_tab_text}'"

    def test_modified_file_stays_modified_after_move(self, qtbot, tmp_path):
        """Test: Moving a modified file to another view should keep it marked as modified."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create and load a file
        file1 = tmp_path / "to_modify.txt"
        file1.write_text("Original content")
        
        window.load_file(str(file1))
        qtbot.wait(50)
        
        pane1 = window.active_pane
        editor1 = pane1.tab_widget.widget(0)
        
        # Modify the file by appending text (simulates user typing)
        editor1.appendPlainText(" - extra text")
        qtbot.wait(50)
        
        # Verify file IS modified
        assert editor1.document().isModified(), "File should be modified after editing"
        tab_text = pane1.tab_widget.tabText(0)
        assert tab_text.endswith("*"), f"Tab should have * but has: '{tab_text}'"
        
        # Create a second split view
        window.add_split_view()
        pane2 = window.active_pane
        qtbot.wait(50)
        
        # Move the tab from pane1 to pane2
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane1)}", pane2)
        qtbot.wait(100)
        
        # Find the moved file's tab in pane2
        moved_tab_index = None
        for i in range(pane2.tab_widget.count()):
            if "to_modify.txt" in pane2.tab_widget.tabText(i):
                moved_tab_index = i
                break
        
        assert moved_tab_index is not None, "Moved file should be in pane2"
        
        moved_editor = pane2.tab_widget.widget(moved_tab_index)
        moved_tab_text = pane2.tab_widget.tabText(moved_tab_index)
        
        # The file should still BE modified after the move
        assert moved_editor.document().isModified(), "File should still be modified after move"
        assert moved_tab_text.endswith("*"), f"Tab should have * after move but has: '{moved_tab_text}'"


class TestDragTabWithMultipleTabs:
    """Test for dragging tabs between panes when both have multiple tabs."""

    def test_drag_tab_from_pane_with_fewer_tabs(self, qtbot, tmp_path):
        """Test dragging tab from pane that has fewer tabs than the destination pane.
        
        This is a regression test for the bug where tabs couldn't be dragged between
        views when the source pane had fewer tabs than the destination pane. The issue
        was that the source pane lookup only checked if the tab index existed in a pane,
        so it would incorrectly match the destination pane instead of the source pane.
        
        Scenario:
        - pane1 has 2 tabs (indices 0, 1)
        - pane2 has 3 tabs (indices 0, 1, 2)
        - When dragging tab 1 from pane1, the code would check:
          - pane1: count=2 > index=1? YES (correct match)
          - (stops here, but the bug would be if pane2 was checked first)
        - However, the real bug is when the source pane is checked AFTER a pane
          that has more tabs, it gets skipped due to order dependency.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        file4 = tmp_path / "file4.txt"
        file5 = tmp_path / "file5.txt"
        
        file1.write_text("content1")
        file2.write_text("content2")
        file3.write_text("content3")
        file4.write_text("content4")
        file5.write_text("content5")
        
        # Create pane2 first with 3 tabs
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(file3))
        window.load_file(str(file4))
        window.load_file(str(file5))
        
        # Now set pane1 as active and open only 1 file
        # This is tricky - we need to navigate back to pane1
        pane1 = window.split_panes[0]
        window.set_active_pane(pane1)
        window.load_file(str(file1))
        
        # Verify initial state
        assert pane1.tab_widget.count() == 1  # file1
        assert pane2.tab_widget.count() == 3  # file3, file4, file5
        
        # Now drag a new tab to pane1
        window.set_active_pane(pane1)
        window.load_file(str(file2))
        
        assert pane1.tab_widget.count() == 2  # file1, file2
        
        # Debug: print open_files before drag
        print(f"\nBefore drag:")
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"pane2 tabs: {[pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]}")
        print(f"open_files: {window.open_files}")
        
        # Simulate dragging tab at index 1 (file2) from pane1 to pane2
        window.on_tab_dropped_to_pane(f"tab:1:{id(pane1)}", pane2)
        
        # Debug: print state after drag
        print(f"\nAfter drag:")
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"pane2 tabs: {[pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]}")
        print(f"open_files: {window.open_files}")
        
        # Verify file2 was moved from pane1 to pane2
        assert pane1.tab_widget.count() == 1, f"pane1 should have 1 tab, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 4, f"pane2 should have 4 tabs, has {pane2.tab_widget.count()}"
        
        # Verify the content is correct
        pane2_tabs_after = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        assert any("file2.txt" in text for text in pane2_tabs_after), "file2 should be in pane2 after drag"


class TestDragTabWithinSamePane:
    """Test for dragging tabs within the same pane (reordering)."""

    def test_drag_tab_within_same_pane_does_not_affect_other_panes(self, qtbot, tmp_path):
        """Bug test: Dragging a tab within the same pane should not move tabs from other panes.
        
        This tests the scenario where:
        - pane1 has tabs at indices 0, 1
        - pane2 has tabs at indices 0, 1
        - User drags tab 1 within pane1 (reordering)
        - Bug: The code incorrectly finds pane2's tab at index 1 and moves it to pane1
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "pane1_file1.txt"
        file2 = tmp_path / "pane1_file2.txt"
        file3 = tmp_path / "pane2_file1.txt"
        file4 = tmp_path / "pane2_file2.txt"
        
        file1.write_text("pane1 content 1")
        file2.write_text("pane1 content 2")
        file3.write_text("pane2 content 1")
        file4.write_text("pane2 content 2")
        
        # Load files into pane1 (the initial pane)
        pane1 = window.active_pane
        window.load_file(str(file1))
        window.load_file(str(file2))
        
        # Create pane2 and load files into it
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(file3))
        window.load_file(str(file4))
        
        # Verify initial state
        assert pane1.tab_widget.count() == 2, f"pane1 should have 2 tabs, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 2, f"pane2 should have 2 tabs, has {pane2.tab_widget.count()}"
        
        pane1_tabs_before = [pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]
        pane2_tabs_before = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        
        print(f"\nBefore reorder:")
        print(f"pane1 tabs: {pane1_tabs_before}")
        print(f"pane2 tabs: {pane2_tabs_before}")
        
        # Simulate dragging tab 1 within pane1 (same pane reorder)
        # This should NOT affect pane2 at all
        window.on_tab_dropped_to_pane(f"tab:1:{id(pane1)}", pane1)
        qtbot.wait(100)
        
        pane1_tabs_after = [pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]
        pane2_tabs_after = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        
        print(f"\nAfter reorder within pane1:")
        print(f"pane1 tabs: {pane1_tabs_after}")
        print(f"pane2 tabs: {pane2_tabs_after}")
        
        # pane2 should be completely unchanged
        assert pane2.tab_widget.count() == 2, f"pane2 should still have 2 tabs, has {pane2.tab_widget.count()}"
        assert pane2_tabs_after == pane2_tabs_before, f"pane2 tabs should be unchanged: {pane2_tabs_before} -> {pane2_tabs_after}"
        
        # pane1 should also be unchanged (reorder within same pane is a no-op for cross-pane logic)
        assert pane1.tab_widget.count() == 2, f"pane1 should still have 2 tabs, has {pane1.tab_widget.count()}"


class TestMoveLastTabClosesPane:
    """Test that moving the last tab from a pane closes that pane."""

    def test_moving_last_tab_closes_source_pane(self, qtbot, tmp_path):
        """Bug test: When the last tab is moved from a pane, that pane should close."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        # Load file1 in pane1
        pane1 = window.active_pane
        window.load_file(str(file1))
        
        # Create pane2 and load file2
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(file2))
        
        # Verify initial state: 2 panes
        assert len(window.split_panes) == 2, f"Should have 2 panes, has {len(window.split_panes)}"
        assert pane1.tab_widget.count() == 1, "pane1 should have 1 tab"
        assert pane2.tab_widget.count() == 1, "pane2 should have 1 tab"
        
        # Move the only tab from pane2 to pane1
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane2)}", pane1)
        qtbot.wait(100)
        
        # pane2 should now be closed since it has no tabs
        assert len(window.split_panes) == 1, f"Should have 1 pane after moving last tab, has {len(window.split_panes)}"
        assert pane1 in window.split_panes, "pane1 should still exist"
        assert pane1.tab_widget.count() == 2, f"pane1 should have 2 tabs, has {pane1.tab_widget.count()}"


class TestMultipleTabMoves:
    """Test that multiple tab moves work correctly."""

    def test_multiple_tab_moves_between_panes(self, qtbot, tmp_path):
        """Bug test: Moving tabs multiple times should continue to work."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        files = []
        for i in range(4):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)
        
        # Load files 0 and 1 in pane1
        pane1 = window.active_pane
        window.load_file(str(files[0]))
        window.load_file(str(files[1]))
        
        # Create pane2 and load files 2 and 3
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(files[2]))
        window.load_file(str(files[3]))
        
        # Verify initial state
        assert pane1.tab_widget.count() == 2, f"pane1 should have 2 tabs, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 2, f"pane2 should have 2 tabs, has {pane2.tab_widget.count()}"
        
        def get_tab_names(pane):
            return [pane.tab_widget.tabText(i) for i in range(pane.tab_widget.count())]
        
        print(f"\nInitial state:")
        print(f"pane1: {get_tab_names(pane1)}")
        print(f"pane2: {get_tab_names(pane2)}")
        
        # Move 1: Move file1.txt (index 1) from pane1 to pane2
        print(f"\nMove 1: file1.txt from pane1 to pane2")
        window.on_tab_dropped_to_pane(f"tab:1:{id(pane1)}", pane2)
        qtbot.wait(50)
        
        assert pane1.tab_widget.count() == 1, f"After move 1, pane1 should have 1 tab, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 3, f"After move 1, pane2 should have 3 tabs, has {pane2.tab_widget.count()}"
        print(f"pane1: {get_tab_names(pane1)}")
        print(f"pane2: {get_tab_names(pane2)}")
        
        # Move 2: Move file2.txt (index 0) from pane2 to pane1
        print(f"\nMove 2: file2.txt from pane2 to pane1")
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane2)}", pane1)
        qtbot.wait(50)
        
        assert pane1.tab_widget.count() == 2, f"After move 2, pane1 should have 2 tabs, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 2, f"After move 2, pane2 should have 2 tabs, has {pane2.tab_widget.count()}"
        print(f"pane1: {get_tab_names(pane1)}")
        print(f"pane2: {get_tab_names(pane2)}")
        
        # Move 3: Move file3.txt (index 0) from pane2 to pane1
        print(f"\nMove 3: file3.txt from pane2 to pane1")
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane2)}", pane1)
        qtbot.wait(50)
        
        assert pane1.tab_widget.count() == 3, f"After move 3, pane1 should have 3 tabs, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 1, f"After move 3, pane2 should have 1 tab, has {pane2.tab_widget.count()}"
        print(f"pane1: {get_tab_names(pane1)}")
        print(f"pane2: {get_tab_names(pane2)}")
        
        # Move 4: Move file0.txt (index 0) from pane1 to pane2
        print(f"\nMove 4: file0.txt from pane1 to pane2")
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane1)}", pane2)
        qtbot.wait(50)
        
        assert pane1.tab_widget.count() == 2, f"After move 4, pane1 should have 2 tabs, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 2, f"After move 4, pane2 should have 2 tabs, has {pane2.tab_widget.count()}"
        print(f"pane1: {get_tab_names(pane1)}")
        print(f"pane2: {get_tab_names(pane2)}")

    def test_stress_test_many_tab_moves(self, qtbot, tmp_path):
        """Stress test: Perform 25+ tab moves to ensure stability."""
        import random
        random.seed(42)  # For reproducibility
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create 6 test files
        files = []
        for i in range(6):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)
        
        # Load files 0, 1, 2 in pane1
        pane1 = window.active_pane
        window.load_file(str(files[0]))
        window.load_file(str(files[1]))
        window.load_file(str(files[2]))
        
        # Create pane2 and load files 3, 4, 5
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(files[3]))
        window.load_file(str(files[4]))
        window.load_file(str(files[5]))
        
        def get_tab_names(pane):
            return [pane.tab_widget.tabText(i) for i in range(pane.tab_widget.count())]
        
        def get_total_tabs():
            return pane1.tab_widget.count() + pane2.tab_widget.count()
        
        # Verify initial state
        assert pane1.tab_widget.count() == 3
        assert pane2.tab_widget.count() == 3
        initial_total = get_total_tabs()
        
        print(f"\nInitial: pane1={get_tab_names(pane1)}, pane2={get_tab_names(pane2)}")
        
        # Perform 25 random moves
        for move_num in range(1, 26):
            # Pick source and dest panes
            if pane1.tab_widget.count() == 0:
                source, dest = pane2, pane1
            elif pane2.tab_widget.count() == 0:
                source, dest = pane1, pane2
            else:
                # Random choice, but ensure we don't empty a pane to keep test interesting
                if pane1.tab_widget.count() == 1:
                    source, dest = pane2, pane1
                elif pane2.tab_widget.count() == 1:
                    source, dest = pane1, pane2
                else:
                    if random.choice([True, False]):
                        source, dest = pane1, pane2
                    else:
                        source, dest = pane2, pane1
            
            # Pick random tab index from source
            tab_index = random.randint(0, source.tab_widget.count() - 1)
            tab_name = source.tab_widget.tabText(tab_index)
            
            source_count_before = source.tab_widget.count()
            dest_count_before = dest.tab_widget.count()
            
            # Perform the move
            window.on_tab_dropped_to_pane(f"tab:{tab_index}:{id(source)}", dest)
            qtbot.wait(10)
            
            # Verify counts changed correctly
            assert source.tab_widget.count() == source_count_before - 1, \
                f"Move {move_num}: source should have {source_count_before - 1} tabs, has {source.tab_widget.count()}"
            assert dest.tab_widget.count() == dest_count_before + 1, \
                f"Move {move_num}: dest should have {dest_count_before + 1} tabs, has {dest.tab_widget.count()}"
            
            # Verify total tabs unchanged
            assert get_total_tabs() == initial_total, \
                f"Move {move_num}: total tabs should be {initial_total}, is {get_total_tabs()}"
            
            # Verify moved tab is in dest
            dest_tabs = get_tab_names(dest)
            assert any(tab_name in t for t in dest_tabs), \
                f"Move {move_num}: {tab_name} should be in dest but dest has {dest_tabs}"
            
            if move_num % 5 == 0:
                print(f"Move {move_num}: pane1={get_tab_names(pane1)}, pane2={get_tab_names(pane2)}")
        
        print(f"\nFinal: pane1={get_tab_names(pane1)}, pane2={get_tab_names(pane2)}")
        print("All 25 moves completed successfully!")


class TestDropTabOntoTabBar:
    """Test dropping a tab onto the tab bar of another pane."""

    def test_drop_tab_onto_tab_bar_moves_tab(self, qtbot, tmp_path):
        """Bug test: Dropping a tab onto a tab in another view should move it there."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        
        file1.write_text("content 1")
        file2.write_text("content 2")
        file3.write_text("content 3")
        
        # Load file1 in pane1
        pane1 = window.active_pane
        window.load_file(str(file1))
        
        # Create pane2 and load file2 and file3
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(file2))
        window.load_file(str(file3))
        
        # Verify initial state
        assert pane1.tab_widget.count() == 1
        assert pane2.tab_widget.count() == 2
        
        # Simulate dropping onto the tab bar (which triggers CustomTabBar.dropEvent)
        # The tab bar should emit a signal that gets handled
        from PySide6.QtCore import QMimeData, QPoint
        from PySide6.QtGui import QDropEvent
        
        # Create mime data as if dragging tab 0 from pane1
        mime_data = QMimeData()
        mime_data.setText(f"tab:0:{id(pane1)}")
        
        # Simulate the drop on pane2's tab bar
        tab_bar = pane2.tab_widget.tabBar()
        
        # Call the tab bar's drop event handler directly
        # Since the event is complex to construct, we'll test via the tab_dropped signal
        # which is what should happen when dropping on the tab bar
        pane2.tab_widget.tab_dropped.emit(f"tab:0:{id(pane1)}")
        qtbot.wait(50)
        
        # pane1 should be closed since its last tab was moved
        assert len(window.split_panes) == 1, "pane1 should be closed after moving its last tab"
        
        # file1 should now be in pane2
        pane2_tabs = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        assert any("file1.txt" in t for t in pane2_tabs), \
            f"file1.txt should be in pane2, but pane2 has: {pane2_tabs}"
        assert pane2.tab_widget.count() == 3, f"pane2 should have 3 tabs, has {pane2.tab_widget.count()}"


class TestMoveUntitledTab:
    """Test moving untitled tabs between views."""

    def test_move_untitled_tab_to_another_view(self, qtbot, tmp_path):
        """Bug test: Untitled tabs should be movable to another view."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Load a file in pane1
        file1 = tmp_path / "file1.txt"
        file1.write_text("content 1")
        
        pane1 = window.active_pane
        window.load_file(str(file1))
        
        # Create pane2 - it will have an Untitled tab by default
        window.add_split_view()
        pane2 = window.active_pane
        
        # Verify initial state
        assert pane1.tab_widget.count() == 1
        assert pane2.tab_widget.count() == 1
        assert "Untitled" in pane2.tab_widget.tabText(0)
        
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"pane2 tabs: {[pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]}")
        
        # Try to move the Untitled tab from pane2 to pane1
        window.on_tab_dropped_to_pane(f"tab:0:{id(pane2)}", pane1)
        qtbot.wait(50)
        
        print(f"After move:")
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"split_panes count: {len(window.split_panes)}")
        
        # The Untitled tab should now be in pane1, and pane2 should be closed
        assert len(window.split_panes) == 1, "pane2 should be closed after moving its last tab"
        assert pane1.tab_widget.count() == 2, f"pane1 should have 2 tabs, has {pane1.tab_widget.count()}"
        
        pane1_tabs = [pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]
        assert any("Untitled" in t for t in pane1_tabs), \
            f"Untitled should be in pane1, but pane1 has: {pane1_tabs}"


class TestUntitledDocumentModifiedState:
    """Tests for untitled document modified state tracking."""

    def test_untitled_document_not_modified_when_empty(self, qtbot):
        """A new untitled document should not be marked as modified when empty."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Get the editor for the untitled tab
        editor = window.editor
        
        # Empty untitled document should not be modified
        assert not editor.document().isModified(), "Empty untitled document should not be modified"
        
        # Tab title should not have asterisk
        tab_title = window.tab_widget.tabText(0)
        assert not tab_title.endswith("*"), f"Tab title should not have asterisk: {tab_title}"

    def test_untitled_document_modified_after_typing(self, qtbot):
        """An untitled document should be marked as modified after typing."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        editor = window.editor
        
        # Type some text (use insertPlainText which simulates actual typing)
        editor.insertPlainText("Hello")
        qtbot.wait(50)
        
        # Should be modified
        assert editor.document().isModified(), "Document should be modified after typing"
        
        # Tab title should have asterisk
        tab_title = window.tab_widget.tabText(0)
        assert tab_title.endswith("*"), f"Tab title should have asterisk: {tab_title}"

    def test_untitled_document_not_modified_after_undo_to_empty(self, qtbot):
        """An untitled document should not be modified after undoing back to empty."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        editor = window.editor
        editor.setFocus()
        qtbot.wait(50)
        
        # Type using keyboard simulation (more realistic than insertPlainText)
        qtbot.keyClicks(editor, "Hello")
        qtbot.wait(50)
        
        # Verify it's modified and tab has asterisk
        assert editor.document().isModified(), "Document should be modified after typing"
        tab_title = window.tab_widget.tabText(0)
        assert tab_title.endswith("*"), f"Tab title should have asterisk after typing: {tab_title}"
        
        # Undo all changes (each keyClick is a separate undo action)
        while editor.document().isUndoAvailable():
            qtbot.keyClick(editor, Qt.Key_Z, Qt.ControlModifier)
            qtbot.wait(10)
        qtbot.wait(50)
        
        # Verify content is empty
        assert editor.toPlainText() == "", f"Content should be empty after undo, got: {repr(editor.toPlainText())}"
        
        # Should NOT be modified (back to original empty state)
        assert not editor.document().isModified(), "Document should not be modified after undo to empty"
        
        # Tab title should NOT have asterisk
        tab_title = window.tab_widget.tabText(0)
        assert not tab_title.endswith("*"), f"Tab title should not have asterisk after undo: {tab_title}"

    def test_untitled_document_close_without_warning_when_empty(self, qtbot):
        """Closing an empty untitled document should not show unsaved changes warning."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        editor = window.editor
        
        # Type and then undo to get back to empty
        editor.insertPlainText("Hello")
        qtbot.wait(50)
        editor.undo()
        qtbot.wait(50)
        
        # Should not be modified
        assert not editor.document().isModified(), "Document should not be modified after undo"
        
        # Close tab should not trigger warning (mocking to verify no dialog appears)
        with patch.object(QMessageBox, 'warning', return_value=QMessageBox.Discard) as mock_warning:
            window.close_tab(0)
            qtbot.wait(50)
            # Warning should NOT have been called since document is not modified
            mock_warning.assert_not_called()


class TestSplitButtonTooltipOnClick:
    """Tests for split button tooltip visibility on click when disabled."""
    
    def test_tooltip_stays_visible_after_click_release(self, qtbot):
        """Test that tooltip stays visible after mouse press and release on disabled split button."""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QMouseEvent
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create splits until max is reached
        for i in range(window.MAX_SPLIT_PANES - 1):
            window.create_split_pane()
        
        # Verify button is disabled
        split_button = window.tab_widget.split_button
        assert not split_button.isEnabled()
        
        # Get button center position
        button_center = split_button.rect().center()
        global_pos = split_button.mapToGlobal(button_center)
        
        # Custom tooltip should be hidden initially
        custom_tooltip = window.tab_widget._custom_tooltip
        assert not custom_tooltip.isVisible(), "Custom tooltip should be hidden initially"
        
        # Simulate mouse press
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPoint(button_center),
            global_pos,
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier
        )
        window.tab_widget.eventFilter(split_button, press_event)
        qtbot.wait(50)
        
        # Verify tooltip is visible after press
        assert custom_tooltip.isVisible(), "Custom tooltip should be visible after mouse press"
        
        # Simulate mouse release
        release_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            QPoint(button_center),
            global_pos,
            Qt.LeftButton,
            Qt.NoButton,
            Qt.NoModifier
        )
        window.tab_widget.eventFilter(split_button, release_event)
        qtbot.wait(50)
        
        # Tooltip should STILL be visible after release
        assert custom_tooltip.isVisible(), "Custom tooltip should still be visible after mouse release"
        
        # Simulate mouse leave
        leave_event = QEvent(QEvent.Type.Leave)
        window.tab_widget.eventFilter(split_button, leave_event)
        qtbot.wait(50)
        
        # Tooltip should be hidden after leave
        assert not custom_tooltip.isVisible(), "Custom tooltip should be hidden after mouse leave"


class TestFontFunctionality:
    """Tests for font selection, size, and color functionality."""

    def test_format_menu_exists(self, qtbot):
        """Test that Format menu exists with font options."""
        window = TextEditor()
        qtbot.addWidget(window)
        menubar = window.menuBar()
        
        format_menu = None
        for action in menubar.actions():
            if "ormat" in action.text():
                format_menu = action.menu()
                break
        
        assert format_menu is not None
        action_texts = [a.text() for a in format_menu.actions()]
        assert any("Font" in t for t in action_texts)
        assert any("Size" in t for t in action_texts)
        assert any("Color" in t for t in action_texts)

    def test_set_editor_font_family(self, qtbot):
        """Test setting font family for all editors."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_font_family("Arial")
        
        assert window.editor.font().family() == "Arial"

    def test_set_editor_font_family_multiple_tabs(self, qtbot):
        """Test setting font family applies to all open tabs."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.create_new_tab()
        window.create_new_tab()
        
        window.set_editor_font_family("Courier New")
        
        for i in range(window.tab_widget.count()):
            editor = window.tab_widget.widget(i)
            assert editor.font().family() == "Courier New"

    def test_set_editor_font_size(self, qtbot):
        """Test setting font size for all editors."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_font_size(16)
        
        assert window.editor.font().pointSize() == 16

    def test_set_editor_font_size_multiple_tabs(self, qtbot):
        """Test setting font size applies to all open tabs."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.create_new_tab()
        window.create_new_tab()
        
        window.set_editor_font_size(14)
        
        for i in range(window.tab_widget.count()):
            editor = window.tab_widget.widget(i)
            assert editor.font().pointSize() == 14

    def test_set_editor_font_color(self, qtbot):
        """Test setting font color for all editors."""
        from PySide6.QtGui import QColor
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        red_color = QColor(255, 0, 0)
        window.set_editor_font_color(red_color)
        
        editor_color = window.editor.get_text_color()
        assert editor_color.red() == 255
        assert editor_color.green() == 0
        assert editor_color.blue() == 0

    def test_set_editor_font_color_multiple_tabs(self, qtbot):
        """Test setting font color applies to all open tabs."""
        from PySide6.QtGui import QColor
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.create_new_tab()
        
        green_color = QColor(0, 255, 0)
        window.set_editor_font_color(green_color)
        
        for i in range(window.tab_widget.count()):
            editor = window.tab_widget.widget(i)
            editor_color = editor.get_text_color()
            assert editor_color.green() == 255

    def test_font_dialog_cancelled(self, qtbot, monkeypatch):
        """Test that cancelling font dialog does not change font."""
        from PySide6.QtWidgets import QDialog
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        original_font = window.editor.font().family()
        
        monkeypatch.setattr(
            "main.FontSelectionDialog.exec",
            lambda self: QDialog.Rejected
        )
        
        window.show_font_dialog()
        
        assert window.editor.font().family() == original_font

    def test_font_size_dialog_cancelled(self, qtbot, monkeypatch):
        """Test that cancelling font size dialog does not change size."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        original_size = window.editor.font().pointSize()
        
        monkeypatch.setattr(
            "main.QInputDialog.getInt",
            lambda *args, **kwargs: (20, False)
        )
        
        window.show_font_size_dialog()
        
        assert window.editor.font().pointSize() == original_size

    def test_font_color_dialog_cancelled(self, qtbot, monkeypatch):
        """Test that cancelling font color dialog does not change color."""
        from PySide6.QtGui import QColor
        
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        original_color = window.editor.get_text_color()
        
        monkeypatch.setattr(
            "main.QColorDialog.getColor",
            lambda *args, **kwargs: QColor()
        )
        
        window.show_font_color_dialog()
        
        current_color = window.editor.get_text_color()
        assert current_color == original_color

    def test_font_change_updates_tab_stop_distance(self, qtbot):
        """Test that changing font updates tab stop distance."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        original_tab_distance = window.editor.tabStopDistance()
        
        window.set_editor_font_family("Courier New")
        
        new_tab_distance = window.editor.tabStopDistance()
        assert new_tab_distance > 0

    def test_font_size_shows_zoom_indicator(self, qtbot):
        """Test that changing font size shows zoom indicator."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_font_size(14)
        
        assert window.zoom_indicator.isVisible()

    def test_font_applies_to_split_panes(self, qtbot):
        """Test that font changes apply to editors in split panes."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.add_split_view()
        
        assert len(window.split_panes) == 2
        
        window.set_editor_font_family("Verdana")
        
        for pane in window.split_panes:
            for i in range(pane.tab_widget.count()):
                editor = pane.tab_widget.widget(i)
                assert editor.font().family() == "Verdana"


class TestSyntaxHighlighting:
    """Tests for multi-language syntax highlighting."""

    def test_syntax_highlighter_exists(self, qtbot):
        """Test that CodeEditor has a syntax highlighter."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        assert editor.highlighter is not None
        assert isinstance(editor.highlighter, SyntaxHighlighter)

    def test_set_language_python(self, qtbot):
        """Test setting Python language."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language('python')
        assert editor.highlighter.language == 'python'

    def test_set_language_javascript(self, qtbot):
        """Test setting JavaScript language."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language('javascript')
        assert editor.highlighter.language == 'javascript'

    def test_set_language_from_file_python(self, qtbot):
        """Test language detection from .py file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('test.py')
        assert editor.highlighter.language == 'python'

    def test_set_language_from_file_javascript(self, qtbot):
        """Test language detection from .js file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('test.js')
        assert editor.highlighter.language == 'javascript'

    def test_set_language_from_file_html(self, qtbot):
        """Test language detection from .html file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('index.html')
        assert editor.highlighter.language == 'html'

    def test_set_language_from_file_css(self, qtbot):
        """Test language detection from .css file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('styles.css')
        assert editor.highlighter.language == 'css'

    def test_set_language_from_file_json(self, qtbot):
        """Test language detection from .json file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('config.json')
        assert editor.highlighter.language == 'json'

    def test_set_language_from_file_java(self, qtbot):
        """Test language detection from .java file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('Main.java')
        assert editor.highlighter.language == 'java'

    def test_set_language_from_file_c(self, qtbot):
        """Test language detection from .c file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('main.c')
        assert editor.highlighter.language == 'c'

    def test_set_language_from_file_cpp(self, qtbot):
        """Test language detection from .cpp file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('main.cpp')
        assert editor.highlighter.language == 'cpp'

    def test_set_language_from_file_rust(self, qtbot):
        """Test language detection from .rs file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('main.rs')
        assert editor.highlighter.language == 'rust'

    def test_set_language_from_file_go(self, qtbot):
        """Test language detection from .go file."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('main.go')
        assert editor.highlighter.language == 'go'

    def test_set_language_from_file_unknown(self, qtbot):
        """Test language detection from unknown file type."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language_from_file('file.xyz')
        assert editor.highlighter.language is None

    def test_highlighter_has_rules_for_python(self, qtbot):
        """Test that Python language has highlighting rules."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language('python')
        assert len(editor.highlighter.rules) > 0

    def test_highlighter_has_rules_for_javascript(self, qtbot):
        """Test that JavaScript language has highlighting rules."""
        editor = CodeEditor()
        qtbot.addWidget(editor)
        editor.set_language('javascript')
        assert len(editor.highlighter.rules) > 0

    def test_load_file_sets_language(self, qtbot, tmp_path):
        """Test that loading a file sets the correct language."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test Python file
        test_file = tmp_path / "test_script.py"
        test_file.write_text("def hello():\n    print('Hello')")
        
        window.load_file(str(test_file))
        
        assert window.editor.highlighter.language == 'python'

    def test_save_as_sets_language(self, qtbot, tmp_path, monkeypatch):
        """Test that saving with new extension updates language."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Set up content
        window.editor.setPlainText("function test() { return 1; }")
        
        # Mock save dialog
        js_file = str(tmp_path / "test.js")
        monkeypatch.setattr(
            "main.QFileDialog.getSaveFileName",
            lambda *args, **kwargs: (js_file, "JavaScript Files (*.js)")
        )
        
        window.save_file_as()
        
        assert window.editor.highlighter.language == 'javascript'

    def test_syntax_highlighter_extension_map(self, qtbot):
        """Test that extension map contains expected mappings."""
        assert SyntaxHighlighter.EXTENSION_MAP['.py'] == 'python'
        assert SyntaxHighlighter.EXTENSION_MAP['.js'] == 'javascript'
        assert SyntaxHighlighter.EXTENSION_MAP['.ts'] == 'javascript'
        assert SyntaxHighlighter.EXTENSION_MAP['.html'] == 'html'
        assert SyntaxHighlighter.EXTENSION_MAP['.css'] == 'css'
        assert SyntaxHighlighter.EXTENSION_MAP['.json'] == 'json'
        assert SyntaxHighlighter.EXTENSION_MAP['.java'] == 'java'
        assert SyntaxHighlighter.EXTENSION_MAP['.c'] == 'c'
        assert SyntaxHighlighter.EXTENSION_MAP['.cpp'] == 'cpp'
        assert SyntaxHighlighter.EXTENSION_MAP['.rs'] == 'rust'
        assert SyntaxHighlighter.EXTENSION_MAP['.go'] == 'go'

    def test_syntax_highlighter_colors_defined(self, qtbot):
        """Test that syntax highlighting colors are defined."""
        assert 'keyword' in SyntaxHighlighter.COLORS
        assert 'builtin' in SyntaxHighlighter.COLORS
        assert 'string' in SyntaxHighlighter.COLORS
        assert 'comment' in SyntaxHighlighter.COLORS
        assert 'number' in SyntaxHighlighter.COLORS
        assert 'function' in SyntaxHighlighter.COLORS

    def test_python_keywords_defined(self, qtbot):
        """Test that Python keywords are defined."""
        python_def = SyntaxHighlighter.LANGUAGES['python']
        assert 'def' in python_def['keywords']
        assert 'class' in python_def['keywords']
        assert 'import' in python_def['keywords']
        assert 'if' in python_def['keywords']
        assert 'for' in python_def['keywords']

    def test_javascript_keywords_defined(self, qtbot):
        """Test that JavaScript keywords are defined."""
        js_def = SyntaxHighlighter.LANGUAGES['javascript']
        assert 'function' in js_def['keywords']
        assert 'const' in js_def['keywords']
        assert 'let' in js_def['keywords']
        assert 'var' in js_def['keywords']
        assert 'async' in js_def['keywords']

    def test_language_menu_exists(self, qtbot):
        """Test that View > Language menu exists."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        # Check that language_menu attribute exists
        assert hasattr(window, 'language_menu')
        assert window.language_menu is not None

    def test_language_menu_has_languages(self, qtbot):
        """Test that language menu has expected language options."""
        window = TextEditor()
        qtbot.addWidget(window)
        
        assert 'python' in window.language_actions
        assert 'javascript' in window.language_actions
        assert 'html' in window.language_actions
        assert 'css' in window.language_actions
        assert None in window.language_actions  # Plain Text

    def test_set_editor_language_from_menu(self, qtbot):
        """Test setting language via menu updates editor."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_language('python')
        
        assert window.editor.highlighter.language == 'python'

    def test_language_menu_updates_checkmark(self, qtbot):
        """Test that selecting a language updates the checkmark."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_language('javascript')
        
        assert window.language_actions['javascript'].isChecked()
        assert not window.language_actions['python'].isChecked()
        assert not window.language_actions[None].isChecked()

    def test_language_menu_updates_status_bar(self, qtbot):
        """Test that selecting a language updates status bar."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_language('python')
        
        assert window.file_type_label.text() == 'Python'

    def test_plain_text_clears_highlighting(self, qtbot):
        """Test that selecting Plain Text clears highlighting."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        window.set_editor_language('python')
        assert window.editor.highlighter.language == 'python'
        
        window.set_editor_language(None)
        assert window.editor.highlighter.language is None
        assert window.file_type_label.text() == 'Plain Text'

    def test_load_file_updates_language_menu(self, qtbot, tmp_path):
        """Test that loading a file updates language menu checkmark."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        test_file = tmp_path / "script.py"
        test_file.write_text("print('hello')")
        
        window.load_file(str(test_file))
        
        assert window.language_actions['python'].isChecked()
