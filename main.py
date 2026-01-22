import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QStatusBar, QMenuBar,
    QToolBar, QLabel, QLineEdit, QDialog, QPushButton, QSplitter,
    QTreeView, QFileSystemModel, QFrame, QTextEdit, QInputDialog, QMenu
)
from PySide6.QtGui import (
    QAction, QKeySequence, QFont, QColor, QPainter, QTextFormat,
    QTextCursor, QFontMetrics, QPalette, QShortcut, QTextCharFormat
)
from PySide6.QtCore import Qt, QRect, QSize, QDir, Signal, QTimer


class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Text editor with line numbers and syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Set font
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Set tab width
        metrics = QFontMetrics(font)
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))
    
    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d30")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, self.line_number_area.width() - 10,
                               self.fontMetrics().height(),
                               Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1


class FindReplaceDialog(QDialog):
    """Find and Replace dialog."""
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find and Replace")
        self.setFixedSize(400, 150)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Find row
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        self.find_btn = QPushButton("Find Next")
        self.find_btn.clicked.connect(self.find_next)
        find_layout.addWidget(self.find_btn)
        layout.addLayout(find_layout)
        
        # Replace row
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self.replace)
        replace_layout.addWidget(self.replace_btn)
        layout.addLayout(replace_layout)
        
        # Replace all button
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.clicked.connect(self.replace_all)
        layout.addWidget(self.replace_all_btn)
    
    def find_next(self):
        text = self.find_input.text()
        if text:
            found = self.editor.find(text)
            if not found:
                cursor = self.editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.editor.setTextCursor(cursor)
                self.editor.find(text)
    
    def replace(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()
    
    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if find_text:
            import re
            content = self.editor.toPlainText()
            new_content = re.sub(re.escape(find_text), replace_text, content, flags=re.IGNORECASE)
            if new_content != content:
                cursor = self.editor.textCursor()
                cursor.beginEditBlock()
                cursor.select(QTextCursor.Document)
                cursor.insertText(new_content)
                cursor.endEditBlock()


class TextEditor(QMainWindow):
    """Main text editor window."""
    
    def __init__(self):
         super().__init__()
         self.current_file = None
         self.zoom_indicator_timer = QTimer()
         self.zoom_indicator_timer.timeout.connect(self.hide_zoom_indicator)
         self.init_ui()
         self.apply_dark_theme()
    
    def init_ui(self):
        self.setWindowTitle("TextEdit - Untitled")
        
        # Set window size to fit within available screen space
        screen = QApplication.primaryScreen().availableGeometry()
        width = min(1200, screen.width() - 100)
        height = min(800, screen.height() - 100)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter for sidebar and editor
        splitter = QSplitter(Qt.Horizontal)
        
        # File explorer sidebar with header
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Folder name header
        self.folder_label = QLabel()
        self.folder_label.setStyleSheet("""
            background-color: #2a2d2e;
            color: #cccccc;
            padding: 8px;
            font-weight: bold;
            border-bottom: 1px solid #3e3e42;
        """)
        sidebar_layout.addWidget(self.folder_label)
        
        # File explorer sidebar
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.file_tree.setColumnHidden(1, True)
        self.file_tree.setColumnHidden(2, True)
        self.file_tree.setColumnHidden(3, True)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setMaximumWidth(300)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_file_tree_context_menu)
        sidebar_layout.addWidget(self.file_tree)
        
        self.update_folder_label(QDir.currentPath())
        
        # Editor
        self.editor = CodeEditor()
        self.editor.textChanged.connect(self.on_text_changed)
        
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(self.editor)
        splitter.setSizes([200, 1000])
        
        main_layout.addWidget(splitter)
        
        # Create menus and toolbars
        self.create_menu_bar()
        self.create_status_bar()
        
        # Connect cursor position to status bar
        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        new_folder_action = QAction("New &Folder...", self)
        new_folder_action.setShortcut("Ctrl+Shift+N")
        new_folder_action.triggered.connect(self.new_folder)
        file_menu.addAction(new_folder_action)
        
        file_menu.addSeparator()
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("Open Fol&der...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find and Replace...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        self.toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        self.toggle_sidebar_action.setShortcut("Ctrl+B")
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
         self.status_bar = QStatusBar()
         self.setStatusBar(self.status_bar)
         
         self.cursor_label = QLabel("Ln 1, Col 1")
         self.encoding_label = QLabel("UTF-8")
         self.file_type_label = QLabel("Plain Text")
         
         self.status_bar.addPermanentWidget(self.cursor_label)
         self.status_bar.addPermanentWidget(QLabel("  |  "))
         self.status_bar.addPermanentWidget(self.encoding_label)
         self.status_bar.addPermanentWidget(QLabel("  |  "))
         self.status_bar.addPermanentWidget(self.file_type_label)
         
         # Create zoom indicator (hidden by default)
         self.zoom_indicator = QLabel()
         self.zoom_indicator.setStyleSheet("""
             background-color: #333333;
             color: #cccccc;
             padding: 5px 10px;
             border: 1px solid #555555;
             border-radius: 3px;
             font-size: 12px;
         """)
         self.zoom_indicator.hide()
         self.zoom_indicator.setParent(self)
         self.update_zoom_indicator()
    
    def apply_dark_theme(self):
        dark_style = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #cccccc;
                border-bottom: 1px solid #454545;
            }
            QMenuBar::item:selected {
                background-color: #505050;
            }
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #454545;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                selection-background-color: #264f78;
            }
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QStatusBar QLabel {
                color: white;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 14px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #787878;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:horizontal {
                background-color: #1e1e1e;
                height: 14px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background-color: #5a5a5a;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #787878;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
            }
            QDialog {
                background-color: #252526;
                color: #cccccc;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #454545;
                padding: 5px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QLabel {
                color: #cccccc;
            }
        """
        self.setStyleSheet(dark_style)
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("TextEdit - Untitled")
    
    def new_folder(self):
        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Folder name:"
        )
        if ok and folder_name:
            current_path = self.file_model.rootPath()
            new_folder_path = os.path.join(current_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=False)
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"Folder '{folder_name}' already exists.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder:\n{e}")
    
    def open_file(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
            )
            if file_path:
                self.load_file(file_path)
    
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Open Folder", self.file_model.rootPath()
        )
        if folder_path:
            self.file_model.setRootPath(folder_path)
            self.file_tree.setRootIndex(self.file_model.index(folder_path))
            self.update_folder_label(folder_path)
    
    def open_file_from_tree(self, index):
        file_path = self.file_model.filePath(index)
        if not self.file_model.isDir(index):
            if self.maybe_save():
                self.load_file(file_path)
    
    def show_file_tree_context_menu(self, position):
        """Display context menu for file tree items."""
        index = self.file_tree.indexAt(position)
        
        if not index.isValid():
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.file_tree.mapToGlobal(position))
        
        if action == delete_action:
            self.delete_file_or_folder(index)
    
    def delete_file_or_folder(self, index):
        """Delete the selected file or folder."""
        file_path = self.file_model.filePath(index)
        is_dir = self.file_model.isDir(index)
        
        item_type = "folder" if is_dir else "file"
        item_name = os.path.basename(file_path)
        
        ret = QMessageBox.warning(
            self, "Delete",
            f"Are you sure you want to delete this {item_type}?\n\n{item_name}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if ret == QMessageBox.Yes:
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                
                # If we deleted the currently open file, close it
                # Normalize paths for comparison (handle forward/back slashes)
                if self.current_file and os.path.normpath(self.current_file) == os.path.normpath(file_path):
                    self.editor.clear()
                    self.current_file = None
                    self.setWindowTitle("TextEdit - Untitled")
                
                # Refresh file model to stop watching the deleted path
                root_path = self.file_model.rootPath()
                self.file_model.setRootPath(root_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete:\n{e}")
    
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"TextEdit - {file_path}")
            self.update_file_type(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
    
    def save_file(self):
        if self.current_file:
            return self.save_to_file(self.current_file)
        return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if file_path:
            return self.save_to_file(file_path)
        return False
    
    def save_to_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = file_path
            self.setWindowTitle(f"TextEdit - {file_path}")
            self.editor.document().setModified(False)
            self.update_file_type(file_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False
    
    def maybe_save(self):
        if self.editor.document().isModified():
            ret = QMessageBox.warning(
                self, "TextEdit",
                "The document has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if ret == QMessageBox.Save:
                return self.save_file()
            elif ret == QMessageBox.Cancel:
                return False
        return True
    
    def on_text_changed(self):
        title = self.windowTitle()
        if not title.endswith("*") and self.editor.document().isModified():
            self.setWindowTitle(title + " *")
    
    def update_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Ln {line}, Col {col}")
    
    def update_folder_label(self, folder_path):
        folder_name = os.path.basename(folder_path) or folder_path
        self.folder_label.setText(f"📁 {folder_name}")
    
    def update_file_type(self, file_path):
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        file_types = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'html': 'HTML',
            'css': 'CSS',
            'json': 'JSON',
            'md': 'Markdown',
            'txt': 'Plain Text',
        }
        self.file_type_label.setText(file_types.get(ext, 'Plain Text'))
    
    def show_find_dialog(self):
        dialog = FindReplaceDialog(self.editor, self)
        dialog.exec()
    
    def toggle_sidebar(self):
        self.file_tree.setVisible(not self.file_tree.isVisible())
    
    def zoom_in(self):
        font = self.editor.font()
        font.setPointSize(font.pointSize() + 1)
        self.editor.setFont(font)
        self.editor.line_number_area.setFont(font)
        self.show_zoom_indicator()
    
    def zoom_out(self):
        font = self.editor.font()
        if font.pointSize() > 6:
            font.setPointSize(font.pointSize() - 1)
            self.editor.setFont(font)
            self.editor.line_number_area.setFont(font)
        self.show_zoom_indicator()
    
    def show_zoom_indicator(self):
        """Display the zoom indicator popup near the menu bar."""
        self.update_zoom_indicator()
        self.zoom_indicator.adjustSize()
        self.zoom_indicator.show()
        
        # Position the indicator at top right, aligned with menu bar
        menubar = self.menuBar()
        x = self.width() - self.zoom_indicator.width() - 10 - int(self.width() * 0.08)
        y = menubar.height() - 31
        self.zoom_indicator.move(x, y)
        
        # Auto-hide after 1 second
        self.zoom_indicator_timer.stop()
        self.zoom_indicator_timer.start(1000)
    
    def hide_zoom_indicator(self):
        """Hide the zoom indicator."""
        self.zoom_indicator.hide()
        self.zoom_indicator_timer.stop()
    
    def update_zoom_indicator(self):
        """Update the zoom indicator text with current zoom percentage."""
        font = self.editor.font()
        # Default font size is 11pt
        zoom_percent = int((font.pointSize() / 11) * 100)
        self.zoom_indicator.setText(f"{zoom_percent}%")
    
    def show_about(self):
        QMessageBox.about(
            self, "About TextEdit",
            "TextEdit - A VS Code-like Text Editor\n\n"
            "Built with Python and PySide6\n\n"
            "Features:\n"
            "• Syntax highlighting line numbers\n"
            "• File explorer sidebar\n"
            "• Find and replace\n"
            "• Dark theme"
        )
    
    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TextEdit")
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
