#!/usr/bin/env python3
"""
Quick test script to visually verify the text alignment fix.
Run this and open a file to see if text is properly aligned (not cut off).
"""
import sys
from main import TextEditor
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.setWindowTitle("Text Alignment Test - Open a file to verify text is not cut off")
    editor.show()
    sys.exit(app.exec())
