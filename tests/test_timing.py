"""
Timing tests for file operations on different file sizes.

These tests measure frame times for:
- File opening
- Scrolling
- Clicking far away in scroll bar
- Find & Replace operations

Run with: pytest tests/test_timing.py -v -s

Results are displayed as test output and can be collected for analysis.
"""
import os
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence
from main import TextEditor


class TimingResults:
    """Stores timing results for analysis."""
    results = {}
    
    @classmethod
    def add_result(cls, test_name, max_frame, avg_frame):
        """Add a timing result."""
        cls.results[test_name] = {
            'max_frame_ms': max_frame,
            'avg_frame_ms': avg_frame
        }
    
    @classmethod
    def print_summary(cls):
        """Print all results in a formatted table."""
        if not cls.results:
            return
        
        print("\n" + "="*70)
        print("TIMING RESULTS SUMMARY")
        print("="*70)
        print(f"{'Test Name':<50} {'Max (ms)':>10} {'Avg (ms)':>10}")
        print("-"*70)
        for test_name, times in sorted(cls.results.items()):
            max_ms = times['max_frame_ms']
            avg_ms = times['avg_frame_ms']
            print(f"{test_name:<50} {max_ms:>10.1f} {avg_ms:>10.1f}")
        print("="*70 + "\n")


class TimingTestBase:
    """Base class for timing tests."""
    
    def setup_method(self):
        """Setup for each test."""
        self.editor = None
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.editor:
            self.editor.close()
    
    def open_editor_with_file(self, file_path):
        """Open editor and load a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Test file not found: {file_path}")
        
        self.editor = TextEditor()
        self.editor.show()
        
        # Process events to show window
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Load the file
        self.editor.load_file(file_path)
        
        # Wait for file to load completely
        timeout = time.time() + 120
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            
            # Check if loading is complete
            if not hasattr(self.editor.editor, '_load_chunks') and \
               (not hasattr(self.editor.editor, '_pending_file_load') or 
                self.editor.editor._pending_file_load is None):
                break
        
        # Extra process events to ensure UI is settled
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.01)
    
    def toggle_frame_timer(self):
        """Toggle frame timer with Ctrl+P."""
        if not self.editor:
            return
        
        # Simulate Ctrl+P
        self.editor.toggle_frame_timer()
        QApplication.processEvents()
        time.sleep(0.05)
    
    def get_frame_times(self):
        """Get current frame timer statistics."""
        if not self.editor:
            return 0, 0
        
        frame_timer = self.editor.frame_timer_widget
        return frame_timer.max_frame_time, frame_timer.avg_frame_time
    
    def record_timing(self, test_name, file_name):
        """Record timing results."""
        max_frame, avg_frame = self.get_frame_times()
        result_name = f"{file_name}::{test_name}"
        TimingResults.add_result(result_name, max_frame, avg_frame)
        print(f"\n{result_name}")
        print(f"  Max Frame: {max_frame:.1f} ms")
        print(f"  Avg Frame: {avg_frame:.1f} ms")


class TestSmallFile(TimingTestBase):
    """Timing tests for small.txt."""
    
    def test_opening_file(self):
        """Measure frame time for opening small.txt."""
        # Reset any previous timing
        self.editor = TextEditor()
        self.editor.show()
        QApplication.processEvents()
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Open file
        self.editor.load_file("small.txt")
        
        # Wait for loading
        timeout = time.time() + 30
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(self.editor.editor, '_load_chunks') and \
               (not hasattr(self.editor.editor, '_pending_file_load') or 
                self.editor.editor._pending_file_load is None):
                break
        
        # Record results
        self.record_timing("Max Opening File", "small.txt")
        assert True
    
    def test_scroll(self):
        """Measure frame time for scrolling in small.txt."""
        self.open_editor_with_file("small.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Simulate scrolling
        for _ in range(20):
            self.editor.editor.moveCursor(self.editor.editor.textCursor().Down)
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Record results
        self.record_timing("Max Scroll", "small.txt")
        assert True
    
    def test_click_far_away(self):
        """Measure frame time for clicking far away in scroll bar for small.txt."""
        self.open_editor_with_file("small.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Click near bottom of document
        self.editor.editor.moveCursor(self.editor.editor.textCursor().End)
        QApplication.processEvents()
        time.sleep(0.05)
        
        # Record results (max from this action)
        self.record_timing("Max Click Far Away", "small.txt")
        assert True
    
    def test_find_replace(self):
        """Measure frame time for find & replace in small.txt."""
        self.open_editor_with_file("small.txt")
        
        # Open find/replace dialog
        self.editor.open_find_replace()
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Find the dialog
        find_dialog = None
        for widget in QApplication.topLevelWidgets():
            if 'FindReplace' in widget.__class__.__name__:
                find_dialog = widget
                break
        
        if find_dialog:
            # Start frame timer
            self.toggle_frame_timer()
            
            # Set find/replace text
            find_dialog.find_input.setText("while")
            find_dialog.replace_input.setText("for")
            QApplication.processEvents()
            time.sleep(0.05)
            
            # Perform replace all
            find_dialog.replace_all()
            
            # Wait for completion
            timeout = time.time() + 30
            while time.time() < timeout:
                QApplication.processEvents()
                time.sleep(0.001)
                if not hasattr(find_dialog, '_replace_state'):
                    break
            
            # Record results
            self.record_timing("Max Find & Replace", "small.txt")
            
            # Close dialog
            find_dialog.close()
            QApplication.processEvents()
        
        assert True


class TestMediumFile(TimingTestBase):
    """Timing tests for medium.txt."""
    
    def test_opening_file(self):
        """Measure frame time for opening medium.txt."""
        self.editor = TextEditor()
        self.editor.show()
        QApplication.processEvents()
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Open file
        self.editor.load_file("medium.txt")
        
        # Wait for loading
        timeout = time.time() + 60
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(self.editor.editor, '_load_chunks') and \
               (not hasattr(self.editor.editor, '_pending_file_load') or 
                self.editor.editor._pending_file_load is None):
                break
        
        # Record results
        self.record_timing("Max Opening File", "medium.txt")
        assert True
    
    def test_scroll(self):
        """Measure frame time for scrolling in medium.txt."""
        self.open_editor_with_file("medium.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Simulate scrolling
        for _ in range(30):
            self.editor.editor.moveCursor(self.editor.editor.textCursor().Down)
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Record results
        self.record_timing("Max Scroll", "medium.txt")
        assert True
    
    def test_click_far_away(self):
        """Measure frame time for clicking far away in scroll bar for medium.txt."""
        self.open_editor_with_file("medium.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Click near bottom of document
        self.editor.editor.moveCursor(self.editor.editor.textCursor().End)
        QApplication.processEvents()
        time.sleep(0.05)
        
        # Record results
        self.record_timing("Max Click Far Away", "medium.txt")
        assert True
    
    def test_find_replace(self):
        """Measure frame time for find & replace in medium.txt."""
        self.open_editor_with_file("medium.txt")
        
        # Open find/replace dialog
        self.editor.open_find_replace()
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Find the dialog
        find_dialog = None
        for widget in QApplication.topLevelWidgets():
            if 'FindReplace' in widget.__class__.__name__:
                find_dialog = widget
                break
        
        if find_dialog:
            # Start frame timer
            self.toggle_frame_timer()
            
            # Set find/replace text
            find_dialog.find_input.setText("while")
            find_dialog.replace_input.setText("for")
            QApplication.processEvents()
            time.sleep(0.05)
            
            # Perform replace all
            find_dialog.replace_all()
            
            # Wait for completion
            timeout = time.time() + 60
            while time.time() < timeout:
                QApplication.processEvents()
                time.sleep(0.001)
                if not hasattr(find_dialog, '_replace_state'):
                    break
            
            # Record results
            self.record_timing("Max Find & Replace", "medium.txt")
            
            # Close dialog
            find_dialog.close()
            QApplication.processEvents()
        
        assert True


class TestLargeFile(TimingTestBase):
    """Timing tests for large.txt."""
    
    def test_opening_file(self):
        """Measure frame time for opening large.txt."""
        if not os.path.exists("large.txt"):
            # Skip if large.txt doesn't exist
            assert True
            return
        
        self.editor = TextEditor()
        self.editor.show()
        QApplication.processEvents()
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Open file
        self.editor.load_file("large.txt")
        
        # Wait for loading (with extended timeout for large file)
        timeout = time.time() + 120
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(self.editor.editor, '_load_chunks') and \
               (not hasattr(self.editor.editor, '_pending_file_load') or 
                self.editor.editor._pending_file_load is None):
                break
        
        # Record results
        self.record_timing("Max Opening File", "large.txt")
        assert True
    
    def test_scroll(self):
        """Measure frame time for scrolling in large.txt."""
        if not os.path.exists("large.txt"):
            assert True
            return
        
        self.open_editor_with_file("large.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Simulate scrolling
        for _ in range(30):
            self.editor.editor.moveCursor(self.editor.editor.textCursor().Down)
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Record results
        self.record_timing("Max Scroll", "large.txt")
        assert True
    
    def test_click_far_away(self):
        """Measure frame time for clicking far away in scroll bar for large.txt."""
        if not os.path.exists("large.txt"):
            assert True
            return
        
        self.open_editor_with_file("large.txt")
        
        # Start frame timer
        self.toggle_frame_timer()
        
        # Click near bottom of document
        self.editor.editor.moveCursor(self.editor.editor.textCursor().End)
        QApplication.processEvents()
        time.sleep(0.05)
        
        # Record results
        self.record_timing("Max Click Far Away", "large.txt")
        assert True
    
    def test_find_replace(self):
        """Measure frame time for find & replace in large.txt."""
        if not os.path.exists("large.txt"):
            assert True
            return
        
        self.open_editor_with_file("large.txt")
        
        # Open find/replace dialog
        self.editor.open_find_replace()
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Find the dialog
        find_dialog = None
        for widget in QApplication.topLevelWidgets():
            if 'FindReplace' in widget.__class__.__name__:
                find_dialog = widget
                break
        
        if find_dialog:
            # Start frame timer
            self.toggle_frame_timer()
            
            # Set find/replace text
            find_dialog.find_input.setText("while")
            find_dialog.replace_input.setText("for")
            QApplication.processEvents()
            time.sleep(0.05)
            
            # Perform replace all
            find_dialog.replace_all()
            
            # Wait for completion (extended timeout for large file)
            timeout = time.time() + 120
            while time.time() < timeout:
                QApplication.processEvents()
                time.sleep(0.001)
                if not hasattr(find_dialog, '_replace_state'):
                    break
            
            # Record results
            self.record_timing("Max Find & Replace", "large.txt")
            
            # Close dialog
            find_dialog.close()
            QApplication.processEvents()
        
        assert True


def pytest_sessionfinish(session, exitstatus):
    """Print timing results summary at end of session."""
    TimingResults.print_summary()
