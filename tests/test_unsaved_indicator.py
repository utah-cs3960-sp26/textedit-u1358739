"""
Test for unsaved changes indicator bug when opening files.

When opening a file, the unsaved changes indicator should NOT appear
since no actual changes have been made by the user.
"""
import os
import sys
import time
from pathlib import Path

# Add parent directory to path so we can find main.py
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)  # Change to project root so file paths work

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Enable deferred loading for this test module
os.environ['ENABLE_DEFERRED_LOAD'] = 'true'


class TestUnsavedIndicator:
    """Tests for unsaved changes indicator behavior."""
    
    def setup_method(self):
        """Setup for each test."""
        self.editor = None
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.editor:
            self.editor.close()
    
    def test_file_does_not_show_unsaved_on_open(self, qtbot):
        """
        Opening a file should NOT show unsaved changes indicator.
        
        This is a regression test for a bug where opening a file
        would show the unsaved changes asterisk even though no changes
        were actually made.
        """
        from main import TextEditor
        
        # Create and show editor
        self.editor = TextEditor()
        qtbot.addWidget(self.editor)
        self.editor.show()
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Load small.txt (deferred loading is disabled in tests, so use small file)
        self.editor.load_file("small.txt")
        
        # Wait briefly for UI to settle
        timeout = time.time() + 5
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
        
        # Extra process events to ensure UI is settled
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.01)
        
        # VERIFICATION: After opening file, document should NOT be modified
        is_modified = self.editor.editor.document().isModified()
        assert not is_modified, \
            "Document should not be marked as modified after opening a file"
        
        # VERIFICATION: Tab title should not have asterisk
        tab_index = self.editor.tab_widget.currentIndex()
        tab_title = self.editor.tab_widget.tabText(tab_index)
        assert not tab_title.endswith("*"), \
            f"Tab title should not show unsaved indicator, but got: '{tab_title}'"
        
        # VERIFICATION: Window title should not have asterisk
        window_title = self.editor.windowTitle()
        assert not window_title.endswith("*"), \
            f"Window title should not show unsaved indicator, but got: '{window_title}'"
    
    def test_large_file_with_deferred_load(self, qtbot):
        """
        Opening a large file with deferred loading enabled should NOT show unsaved indicator.
        
        This tests the case where deferred loading is enabled (production mode).
        The chunks are loaded progressively, but the document should only be marked
        as modified AFTER the entire file is loaded, and then immediately marked as unmodified.
        """
        if not os.path.exists("large.txt"):
            # Skip if large.txt doesn't exist
            return
        
        from main import TextEditor
        
        # Create and show editor
        self.editor = TextEditor()
        qtbot.addWidget(self.editor)
        self.editor.show()
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Load large.txt
        self.editor.load_file("large.txt")
        
        # Wait for file to load completely with deferred loading
        timeout = time.time() + 120
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            
            # Check if loading is complete
            if not hasattr(self.editor.editor, '_load_content') and \
               (not hasattr(self.editor.editor, '_pending_file_load') or 
                self.editor.editor._pending_file_load is None):
                break
        
        # Extra process events to ensure UI is settled
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.01)
        
        # VERIFICATION: After opening file, document should NOT be modified
        is_modified = self.editor.editor.document().isModified()
        assert not is_modified, \
            "Document should not be marked as modified after opening a file"
        
        # VERIFICATION: Tab title should not have asterisk
        tab_index = self.editor.tab_widget.currentIndex()
        tab_title = self.editor.tab_widget.tabText(tab_index)
        assert not tab_title.endswith("*"), \
            f"Tab title should not show unsaved indicator, but got: '{tab_title}'"
        
        # VERIFICATION: Window title should not have asterisk
        window_title = self.editor.windowTitle()
        assert not window_title.endswith("*"), \
            f"Window title should not show unsaved indicator, but got: '{window_title}'"
