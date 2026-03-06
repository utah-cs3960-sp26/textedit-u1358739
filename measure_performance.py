#!/usr/bin/env python3
"""
Measure Week 9 performance with deferred loading enabled.
Run this to get actual frame time measurements for large files.
"""
import os
import sys

# Enable deferred loading for measurements
os.environ['ENABLE_DEFERRED_LOAD'] = 'true'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QElapsedTimer
from main import TextEditor
import time

class PerformanceMeasure:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.editor_window = None
        self.measurements = {}
    
    def measure_file_open(self, file_path, timeout_seconds=120):
        """Measure frame time for opening a file."""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        print(f"\nMeasuring: Opening {file_path}")
        print(f"File size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
        
        # Create new editor window
        editor = TextEditor()
        editor.show()
        self.app.processEvents()
        
        # Start frame timer
        frame_timer = editor.frame_timer_widget
        frame_timer.start_timing()
        
        # Measure loading
        start_time = time.time()
        wall_start = start_time
        
        editor.load_file(file_path)
        
        # Wait for loading to complete
        timeout_time = time.time() + timeout_seconds
        max_wall_time = 0
        while time.time() < timeout_time:
            self.app.processEvents()
            time.sleep(0.001)
            
            # Check if deferred loading is complete
            if not hasattr(editor.editor, '_load_chunks') and \
               (not hasattr(editor.editor, '_pending_file_load') or editor.editor._pending_file_load is None):
                break
            
            max_wall_time = time.time() - wall_start
        
        wall_time = time.time() - start_time
        
        # Get frame statistics
        max_frame = frame_timer.max_frame_time if frame_timer.frame_times else 0
        avg_frame = frame_timer.avg_frame_time if frame_timer.frame_times else 0
        
        result = {
            'wall_time_ms': wall_time * 1000,
            'max_frame_ms': max_frame,
            'avg_frame_ms': avg_frame,
            'frame_count': len(frame_timer.frame_times),
            'lines': editor.editor.blockCount() if editor.editor.document() else 0
        }
        
        print(f"  Wall time: {result['wall_time_ms']:.0f}ms")
        print(f"  Max frame: {result['max_frame_ms']:.1f}ms")
        print(f"  Avg frame: {result['avg_frame_ms']:.1f}ms")
        print(f"  Frames: {result['frame_count']}")
        print(f"  Lines: {result['lines']}")
        
        editor.close()
        return result
    
    def run(self):
        """Run all measurements."""
        files = ['small.txt', 'medium.txt', 'large.txt']
        
        print("="*60)
        print("Week 9 Performance Measurements")
        print(f"System time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"\nSkipping {file_path} (not found)")
                continue
            
            result = self.measure_file_open(file_path)
            if result:
                self.measurements[file_path] = result
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        for file_name, measurements in self.measurements.items():
            print(f"\n{file_name}:")
            print(f"  Wall Time: {measurements['wall_time_ms']:.0f} ms")
            print(f"  Max Frame: {measurements['max_frame_ms']:.1f} ms")
            print(f"  Avg Frame: {measurements['avg_frame_ms']:.1f} ms")

if __name__ == '__main__':
    measure = PerformanceMeasure()
    measure.run()
