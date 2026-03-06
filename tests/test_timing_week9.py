"""
Test and measure frame times for Week 9 optimizations.
Runs timing tests without blocking on frame timer display.
"""
import sys
import os
import time
from PySide6.QtWidgets import QApplication
from main import TextEditor

def measure_file_open(text_editor, file_path, frame_timer):
    """Measure frame time for opening a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    # Start frame timer
    frame_timer.start_timing()
    
    # Record starting time
    start_time = time.time()
    
    # Open the file
    text_editor.load_file(file_path)
    
    # Process events to allow loading to happen
    QApplication.processEvents()
    
    # Wait for loading to complete (for deferred loading)
    while frame_timer.frame_times and len(frame_timer.frame_times) < 5:
        QApplication.processEvents()
        time.sleep(0.016)  # Let a few frames pass
    
    elapsed = time.time() - start_time
    max_frame = frame_timer.max_frame_time if frame_timer.frame_times else 0
    avg_frame = frame_timer.avg_frame_time if frame_timer.frame_times else 0
    
    return {
        'elapsed_ms': elapsed * 1000,
        'max_frame_ms': max_frame,
        'avg_frame_ms': avg_frame
    }

def test_small_file():
    """Test opening small.txt"""
    app = QApplication.instance() or QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    
    timing = measure_file_open(editor, "small.txt", editor.frame_timer_widget)
    if timing:
        print(f"small.txt: {timing}")
    
    editor.close()

if __name__ == '__main__':
    test_small_file()
