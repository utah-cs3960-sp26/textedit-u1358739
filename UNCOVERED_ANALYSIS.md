# Code Coverage Analysis - Uncovered Lines

**Overall Coverage: 94% (1681 total statements, 99 uncovered)**

## Uncovered Lines Summary

### 1. **Lines 2078-2084** - Close Pane Unsaved Changes Handling
```python
old_tab_widget = self.tab_widget
self.tab_widget = tab_widget
self.tab_widget.setCurrentIndex(i)
if not self.save_file():
    self.tab_widget = old_tab_widget
    return
self.tab_widget = old_tab_widget
```

**Why uncovered:** This is the error recovery path when saving a file fails during the "close split pane" operation. It's extremely difficult to test because it requires:
- Creating a split pane with modified files
- Closing that pane
- Intentionally failing the file write operation (would need file system permission errors or I/O mocking)
- The save_file() must return False while prompting for save

**Testing challenge:** Requires mocking file I/O at the OS level or triggering permission errors, which is fragile.

---

### 2. **Lines 2239-2241** - Legacy Format Tab Index Mapping
```python
elif pane_info == index:
    new_current_file = file_path
    break
```

**Why uncovered:** This handles legacy tab index format (when `pane_info` is just an integer rather than a tuple). The codebase moved to tuple format `(pane, tab_index)`, making this legacy code path effectively dead.

**Testing challenge:** The codebase only creates tuple format, so this old format never occurs during normal execution.

---

### 3. **Lines 2294-2296** - Legacy Format File Save
```python
elif pane_info == index:
    file_path = path
    break
```

**Why uncovered:** Same as above - legacy code path for old tab index format that's no longer created by the application.

**Testing challenge:** Legacy format is never generated, only the tuple format is used.

---

### 4. **Lines 2302-2304** - Legacy Format Tab Text Update
```python
else:
    # Legacy format (just tab index)
    if pane_info < self.tab_widget.count():
        file_name = os.path.basename(new_file_path)
        self.tab_widget.setTabText(pane_info, file_name)
```

**Why uncovered:** Same legacy code path issue.

**Testing challenge:** Legacy format never created by current code.

---

### 5. **Lines 2339-2343** - Legacy Format Remove Tab
```python
elif pane_info == index:
    del self.open_files[file_path]
    if file_path in self.file_modified_state:
        del self.file_modified_state[file_path]
    break
```

**Why uncovered:** Legacy format handling in remove_tab().

**Testing challenge:** Legacy format never generated.

---

### 6. **Lines 2352-2353** - Legacy Format Index Update
```python
elif pane_info > index:
    self.open_files[file_path] = pane_info - 1
```

**Why uncovered:** Legacy format index update during tab removal.

**Testing challenge:** Legacy format never generated.

---

### 7. **Lines 2402-2407** - File Open with Encoding Error
```python
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    QMessageBox.critical(self, "Error", f"Could not load file:\n{e}")
```

**Why uncovered:** The exception handler in `load_file()` is tested in isolation, but this specific location isn't hit by any test.

**Testing challenge:** Requires file I/O errors during test execution - mocking `open()` at the right spot is needed.

---

### 8. **Lines 2425-2446** - File Open with Unsupported Encoding
```python
except UnicodeDecodeError as e:
    QMessageBox.critical(self, "Error", f"Could not load file: {e}")
```

**Why uncovered:** Exception handler for files with invalid UTF-8 encoding.

**Testing challenge:** Would require creating a test file with invalid UTF-8 bytes and ensuring it's read by load_file(). Complex to set up reliably.

---

### 9. **Lines 2484-2485** - Save File Path Normalization Edge Case
```python
if os.path.normpath(source_path) == os.path.normpath(dest_path):
    continue
```

**Why uncovered:** Prevents moving a file to itself in the file tree.

**Testing challenge:** This edge case is difficult to trigger without low-level file system manipulation or careful mock setup.

---

### 10. **Lines 2501-2509** - Directory Merge During File Move
```python
if os.path.isdir(dest_file_path) and os.path.isdir(source_path):
    # Move contents into existing directory
    for item in os.listdir(source_path):
        src = os.path.join(source_path, item)
        dst = os.path.join(dest_file_path, item)
        ...
```

**Why uncovered:** Complex file system logic for merging directories during drag-drop operations.

**Testing challenge:** Requires actual file system operations with nested directories and careful cleanup. Hard to test in isolation.

---

### 11. **Lines 2518-2544** - File Move Exception Handling
```python
except Exception as e:
    pass  # Silent failure in drag-drop
```

**Why uncovered:** Generic exception handler that silently catches file operation errors during drag-drop.

**Testing challenge:** Requires triggering file operation failures (permissions, locked files, etc.) at precisely the right moment.

---

### 12. **Lines 2604-2606** - Update File Label for Legacy Format
```python
if pane_info < self.tab_widget.count():
    file_name = os.path.basename(new_file_path)
    self.tab_widget.setTabText(pane_info, file_name)
```

**Why uncovered:** Legacy format handling in `update_moved_file_paths()`.

**Testing challenge:** Legacy format never created.

---

### 13. **Lines 2651** - New Tab Creation Edge Case
```python
editor, _ = self.create_new_tab(file_path)
```

**Why uncovered:** Creates new tab for file already open in different pane.

**Testing challenge:** Tests might not specifically exercise this exact code path where file is in different pane.

---

### 14. **Lines 2736-2747** - Close Event Unsaved Changes
```python
if self.editor.document().isModified():
    # ... prompt user to save
    if ret == QMessageBox.Save:
        return self.save_current_file()
```

**Why uncovered:** Main window close event unsaved changes check.

**Testing challenge:** Window close events are difficult to test reliably in automated tests without proper event simulation.

---

### 15. **Lines 2798** - Editor Focus Early Return
```python
if self.active_pane and self.active_pane.tab_widget == self.tab_widget:
    return  # Already in active pane
```

**Why uncovered:** Early return when editor focus is received in already-active pane.

**Testing challenge:** Requires setting focus to editor that's already in active pane - tests may not specifically test this no-op case.

---

### 16. **Lines 2828-2829** - Find Dialog Exception
```python
except Exception as e:
    QMessageBox.critical(self, "Error", f"No files found: {e}")
```

**Why uncovered:** Exception handler in find operation.

**Testing challenge:** Need to trigger exception in find logic, hard to arrange without complex setup.

---

### 17. **Lines 3032-3034** - Close Event Save Failure
```python
if ret == QMessageBox.Save:
    if not self.save_current_file():
        event.ignore()
        return
```

**Why uncovered:** When user chooses to save but save fails during close event.

**Testing challenge:** Requires closing window with file modified AND causing save to fail - very difficult to set up.

---

### 18. **Lines 3042-3046** - Main Function Entry Point
```python
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TextEdit")
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())
```

**Why uncovered:** Entry point function never called during tests (tests create QApplication and TextEditor directly).

**Testing challenge:** Tests bypass main() and set up their own QApplication instance.

---

## Summary by Category

### **Legacy Code (Lines that can be safely removed)**
- Lines 2239-2241, 2294-2296, 2302-2304, 2339-2343, 2352-2353, 2604-2606
- **Impact:** These handle old tab index format that's no longer generated
- **Recommendation:** Remove or refactor to eliminate legacy code paths

### **File I/O Error Handling (Hard to test)**
- Lines 2402-2407, 2425-2446, 2484-2485, 2501-2509, 2518-2544, 2828-2829
- **Impact:** Exception handlers for file operations
- **Recommendation:** Consider refactoring to testable error handling patterns

### **GUI Event Handling (Difficult to simulate)**
- Lines 2736-2747, 2798, 3032-3034, 3042-3046
- **Impact:** Window close events, focus handling, entry point
- **Recommendation:** Accept as non-testable or use specialized GUI testing frameworks

### **Edge Cases**
- Lines 2651, 2736-2747
- **Impact:** Uncommon code paths that rarely execute
- **Recommendation:** Can be tested with additional integration tests if needed

## Overall Assessment

**Total uncovered: 99 statements (6% of codebase)**

Most uncovered lines fall into these categories:
1. **Legacy code** - Old format handling that should be removed (7 locations)
2. **Exception handlers** - File I/O and parsing errors (6 locations)
3. **GUI events** - Window close, focus, dialog events (3 locations)
4. **Entry point** - main() function (1 location)

The 94% coverage is solid for a GUI application. The remaining gaps are mostly in:
- Dead/legacy code that could be removed
- Exception paths that are difficult to trigger
- GUI event handlers that are hard to test automatically

## Recommendations

1. **Remove legacy code**: Lines with old tab index format handling should be deleted
2. **Add integration tests**: For complex file operations (drag-drop, file moves)
3. **Use file system mocking**: For exception handlers in file I/O operations
4. **Accept GUI limitations**: Some GUI event handlers may not be worth testing
5. **Consider pytest fixtures**: For complex setup scenarios with files and permissions
