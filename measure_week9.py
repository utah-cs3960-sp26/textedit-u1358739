"""
Week 9 Timing Measurements Script
Measures frame times for file opening, scrolling, and find-replace operations.
"""
import sys
import os
import time
import psutil
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QEvent, Qt
from PySide6.QtGui import QWheelEvent
from main import TextEditor


class TimingMeasurement:
    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
    
    def get_memory_usage(self):
        """Get physical memory usage in GB."""
        return self.process.memory_info().rss / (1024 * 1024 * 1024)
    
    def measure_open_file(self, editor, file_path):
        """Measure frame time for opening a file."""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        # Reset frame timer
        frame_timer = editor.frame_timer_widget
        frame_timer.start_timing()
        
        # Clear any existing editor content
        editor.editor.setPlainText("")
        editor.editor.document().setModified(False)
        
        # Open the file
        print(f"Opening {file_path}...")
        start_time = time.time()
        editor.load_file(file_path)
        
        # Wait for file to load (process events)
        timeout = time.time() + 60  # 60 second timeout
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            
            # Check if loading is done (text is present and not pending)
            if (hasattr(editor.editor, '_pending_file_load') and 
                editor.editor._pending_file_load is None and
                not hasattr(editor.editor, '_load_chunks')):
                break
        
        elapsed = time.time() - start_time
        
        # Get frame timer results
        max_frame = frame_timer.max_frame_time
        avg_frame = frame_timer.avg_frame_time if frame_timer.frame_times else 0
        
        print(f"  Elapsed: {elapsed:.2f}s, Max Frame: {max_frame:.1f}ms, Avg Frame: {avg_frame:.1f}ms")
        
        return {
            'elapsed_ms': elapsed * 1000,
            'max_frame_ms': max_frame,
            'avg_frame_ms': avg_frame,
            'total_lines': editor.editor.blockCount()
        }
    
    def measure_find_replace(self, editor, find_text, replace_text):
        """Measure frame time for find and replace."""
        frame_timer = editor.frame_timer_widget
        frame_timer.start_timing()
        
        print(f"Replacing '{find_text}' with '{replace_text}'...")
        start_time = time.time()
        
        # Open find/replace dialog
        editor.open_find_replace()
        find_dialog = None
        
        # Find the dialog
        for widget in QApplication.topLevelWidgets():
            if 'FindReplace' in widget.__class__.__name__:
                find_dialog = widget
                break
        
        if find_dialog:
            # Set find and replace text
            find_dialog.find_input.setText(find_text)
            find_dialog.replace_input.setText(replace_text)
            
            # Wait a frame for UI to update
            QApplication.processEvents()
            time.sleep(0.016)
            
            # Perform replace all
            frame_timer.start_timing()
            start_time = time.time()
            find_dialog.replace_all()
            
            # Wait for replacement to complete
            timeout = time.time() + 120  # 120 second timeout
            while time.time() < timeout:
                QApplication.processEvents()
                time.sleep(0.001)
                
                # Check if replacement is done
                if not hasattr(find_dialog, '_replace_state'):
                    break
            
            elapsed = time.time() - start_time
            
            # Get frame timer results
            max_frame = frame_timer.max_frame_time
            avg_frame = frame_timer.avg_frame_time if frame_timer.frame_times else 0
            
            print(f"  Elapsed: {elapsed:.2f}s, Max Frame: {max_frame:.1f}ms, Avg Frame: {avg_frame:.1f}ms")
            
            # Close dialog
            find_dialog.close()
            QApplication.processEvents()
            
            return {
                'elapsed_ms': elapsed * 1000,
                'max_frame_ms': max_frame,
                'avg_frame_ms': avg_frame
            }
        
        return None
    
    def measure_scroll(self, editor):
        """Measure frame time for scrolling."""
        frame_timer = editor.frame_timer_widget
        frame_timer.start_timing()
        
        print("Scrolling through document...")
        start_time = time.time()
        
        # Simulate scrolling with Page Down
        for _ in range(50):
            editor.editor.keyPressEvent(QEvent(QEvent.KeyPress))
            editor.editor.moveCursor(editor.editor.textCursor().Down)
            QApplication.processEvents()
            time.sleep(0.001)
        
        elapsed = time.time() - start_time
        max_frame = frame_timer.max_frame_time
        avg_frame = frame_timer.avg_frame_time if frame_timer.frame_times else 0
        
        print(f"  Elapsed: {elapsed:.2f}s, Max Frame: {max_frame:.1f}ms, Avg Frame: {avg_frame:.1f}ms")
        
        return {
            'elapsed_ms': elapsed * 1000,
            'max_frame_ms': max_frame,
            'avg_frame_ms': avg_frame
        }
    
    def run_measurements(self):
        """Run all measurements."""
        app = QApplication.instance() or QApplication(sys.argv)
        editor = TextEditor()
        editor.show()
        
        files = ['small.txt', 'medium.txt', 'large.txt']
        
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"Skipping {file_path} (not found)")
                continue
            
            print(f"\n=== Testing {file_path} ===")
            
            # Measure file opening
            open_result = self.measure_open_file(editor, file_path)
            if open_result:
                self.results.setdefault(file_path, {})['open'] = open_result
            
            # Only test scroll and find-replace for accessible files
            if open_result and open_result['elapsed_ms'] < 60000:  # < 1 minute
                # Measure scrolling
                scroll_result = self.measure_scroll(editor)
                self.results.setdefault(file_path, {})['scroll'] = scroll_result
                
                # Measure find-replace (only on small files to save time)
                if file_path == 'small.txt':
                    replace_result = self.measure_find_replace(editor, 'while', 'for')
                    self.results.setdefault(file_path, {})['replace'] = replace_result
        
        # Record memory usage
        print(f"\nMemory usage: {self.get_memory_usage():.2f} GB")
        
        editor.close()
        
        # Print summary
        print("\n=== Summary ===")
        for file_name, measurements in self.results.items():
            print(f"\n{file_name}:")
            for op, result in measurements.items():
                if result:
                    print(f"  {op}: Max={result['max_frame_ms']:.1f}ms, Avg={result['avg_frame_ms']:.1f}ms")


if __name__ == '__main__':
    measurement = TimingMeasurement()
    measurement.run_measurements()
