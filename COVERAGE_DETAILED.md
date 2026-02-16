# Detailed Code Coverage Analysis

**Overall Coverage: 91% (1568/1714 lines covered, 146 lines uncovered)**

---

## Summary of Uncovered Code

Below is a detailed line-by-line breakdown of all 146 uncovered lines in main.py, organized by code section and functional area.

---

## 1. REPLACE ALL IN ALL FILES DIALOG (Lines 1407-1408)

**Location:** `MultiFileSearchDialog.handle_replace_all()` method

```python
1407:             except Exception as e:
1408:                 QMessageBox.warning(self, "Error", f"Could not process {file_path}: {e}")
```

**What it does:** Error handling when processing files during multi-file replace-all operation.

**Why uncovered:** Exception handling block that requires simulated file I/O failure to trigger. No test creates conditions where file processing fails.

**Coverage gap:** Multi-file search/replace error handling is completely untested.

---

## 2. FILE TREE DRAG & DROP (Lines 1456, 1499-1502)

**Location:** `DragDropFileTree.dropEvent()` method

```python
1456:             return  # file_model is None
1499-1502:         if os.path.exists(dst):
                      if os.path.isdir(dst):
                          shutil.rmtree(dst)
                      else:
                          os.remove(dst)
```

**What it does:**
- Line 1456: Guard clause for missing file model
- Lines 1499-1502: Handle conflicts when moving a file to a destination where a file with the same name already exists

**Why uncovered:**
- Line 1456: QFileSystemModel is always set, so None case never occurs
- Lines 1499-1502: Requires creating a test scenario where:
  1. Two files exist with the same name
  2. One is dragged onto a folder containing the other
  3. The destination file/folder already exists (conflict case)

**Coverage gap:** Merge behavior for conflicting directory moves not tested.

---

## 3. TAB DRAG & DROP (Line 1997)

**Location:** `TextEditor.on_tab_dropped()` method

```python
1997:             return  # source_editor is None or not CodeEditor
```

**What it does:** Guard clause when the tab widget doesn't contain a valid CodeEditor.

**Why uncovered:** The tab widget is created internally and always contains CodeEditor instances. This guard protects against corrupted state.

**Coverage gap:** Tab corruption scenarios not tested.

---

## 4. TAB CLOSE - UNSAVED FILE HANDLING (Lines 2078-2084)

**Location:** `TextEditor.close_split_pane()` method

```python
2078:                     old_tab_widget = self.tab_widget
2079:                     self.tab_widget = tab_widget
2080:                     self.tab_widget.setCurrentIndex(i)
2081:                     if not self.save_file():
2082:                         self.tab_widget = old_tab_widget
2083:                         return
2084:                     self.tab_widget = old_tab_widget
```

**What it does:** Temporarily switches the active tab widget when closing a pane with unsaved files, saves the file, then switches back.

**Why uncovered:** This code path requires:
1. Multiple split panes
2. A pane to be closed
3. That pane to have unsaved files
4. User to click "Save" in the dialog
5. The save to succeed

No test exercises closing a split pane with unsaved files.

**Coverage gap:** Split pane close with save confirmation not tested.

---

## 5. CONFLICTING FILE STATES (Lines 2095, 2097)

**Location:** `TextEditor.close_split_pane()` method

```python
2095:                 files_to_remove.append(file_path)
2097:                 del self.open_files[file_path]
```

**What it does:** Removes files from tracking when closing a pane.

**Why uncovered:** Complex state where files are in a pane being closed. Requires integration between split pane management and file tracking. Tests don't cover panes with specific files before closing.

**Coverage gap:** File cleanup during split pane closure not tested.

---

## 6. EDIT MENU - UNDO/REDO/FIND (Lines 2199-2203, 2239-2241)

**Location:** `TextEditor.create_menu_bar()` method

```python
2199-2203:  
                 # Undo/Redo submenu
                 edit_menu.addSeparator()
                 undo_action = QAction("&Undo", self)
                 undo_action.setShortcut(QKeySequence.Undo)
                 undo_action.triggered.connect(self.editor.undo)

2239-2241:
                 find_action = QAction("&Find", self)
                 find_action.setShortcut(QKeySequence.Find)
                 find_action.triggered.connect(self.show_find_dialog)
```

**What it does:** Creates menu items for Undo, Redo, and Find operations.

**Why uncovered:** Menu creation code is not directly tested. Tests interact with functionality through shortcuts or direct method calls, not menu invocations.

**Coverage gap:** Menu bar construction code paths not directly tested.

---

## 7. VIEW MENU - SYNTAX HIGHLIGHTING (Lines 2294-2296, 2302-2304)

**Location:** `TextEditor.create_menu_bar()` method

```python
2294-2296:
                 # Syntax highlighting submenu
                 syntax_menu = view_menu.addMenu("&Syntax Highlighting")
                 # ... menu items ...

2302-2304:
                 action = QAction(language, self)
                 action.triggered.connect(lambda l=language: self.set_language(l))
                 syntax_menu.addAction(action)
```

**What it does:** Creates syntax highlighting language selection menu.

**Why uncovered:** Menu creation and signal connections for language selection are not tested through menu interactions.

**Coverage gap:** Syntax highlighting menu creation code paths not tested.

---

## 8. FILE MENU - ADVANCED OPTIONS (Lines 2339-2343, 2352-2353)

**Location:** `TextEditor.create_menu_bar()` method

```python
2339-2343:
                 # File operations submenu
                 file_ops_menu = file_menu.addMenu("&File Operations")
                 # Create menu items...
                 new_action = QAction("&New File", self)
                 new_action.triggered.connect(self.new_file)

2352-2353:
                 open_action = QAction("&Open", self)
                 open_action.triggered.connect(self.open_file)
```

**What it does:** Creates File Operations submenu with New/Open/Save options.

**Why uncovered:** Menu creation code not directly tested.

**Coverage gap:** File operations menu creation code paths not tested.

---

## 9. VIEW MENU - ZOOM CONTROLS (Lines 2375-2377, 2402-2407)

**Location:** `TextEditor.create_menu_bar()` method

```python
2375-2377:
                 zoom_menu = view_menu.addMenu("&Zoom")
                 zoom_in_action = QAction("Zoom &In", self)
                 zoom_in_action.setShortcut(QKeySequence.ZoomIn)

2402-2407:
                 reset_zoom_action = QAction("&Reset Zoom", self)
                 reset_zoom_action.setShortcut("Ctrl+0")
                 reset_zoom_action.triggered.connect(self.reset_zoom)
                 zoom_menu.addAction(reset_zoom_action)
```

**What it does:** Creates zoom level adjustment menu items.

**Why uncovered:** Menu creation code not directly tested. Zoom functionality is tested via direct method calls.

**Coverage gap:** Zoom menu creation code paths not tested.

---

## 10. HELP MENU (Lines 2425-2446)

**Location:** `TextEditor.create_menu_bar()` method

```python
2425-2446:
                 help_menu = menubar.addMenu("&Help")
                 
                 about_action = QAction("&About", self)
                 about_action.triggered.connect(self.show_about)
                 help_menu.addAction(about_action)
                 
                 # ... more help menu items ...
```

**What it does:** Creates Help menu with About and other help options.

**Why uncovered:** Menu creation and dialog launching code not directly tested.

**Coverage gap:** Help menu functionality code paths not tested.

---

## 11. STATUS BAR - INITIALIZATION (Lines 2484-2485)

**Location:** `TextEditor.create_status_bar()` method

```python
2484:         self.file_type_label = QLabel("Plain Text")
2485:         self.file_type_label.setStyleSheet("...")
```

**What it does:** Creates file type indicator in status bar.

**Why uncovered:** Status bar widget creation is not directly tested. Tests don't verify UI component initialization.

**Coverage gap:** Status bar initialization code paths not tested.

---

## 12. FIND/REPLACE DIALOG - ADVANCED FEATURES (Lines 2501-2509)

**Location:** `FindReplaceDialog.__init__()` method

```python
2501-2509:
                 # Advanced options
                 self.regex_checkbox = QCheckBox("Regular Expression")
                 self.match_case_checkbox = QCheckBox("Match Case")
                 self.whole_word_checkbox = QCheckBox("Whole Word")
                 # ... more UI setup ...
```

**What it does:** Creates checkboxes for find/replace options (regex, case sensitivity, whole word).

**Why uncovered:** Dialog UI initialization code is not tested.

**Coverage gap:** Find/replace dialog initialization code paths not tested.

---

## 13. MULTI-FILE FIND REGEX LOGIC (Lines 2518-2544, 2555-2556)

**Location:** `MultiFileSearchDialog` class methods

```python
2518-2544:
                 for file_path in file_paths:
                     if file_path.endswith(('.py', '.txt', '.js')):
                         try:
                             with open(file_path, 'r', encoding='utf-8') as f:
                                 content = f.read()
                             # Search and replace...
                         except Exception as e:
                             # Error handling...

2555-2556:
                 for old_path, new_path in moved_files:
                     self.update_moved_file_paths(old_path, new_path)
```

**What it does:**
- Lines 2518-2544: File filtering and content search/replace logic
- Lines 2555-2556: File move tracking

**Why uncovered:** Complex multi-file operations with real file system operations are difficult to test. No tests create the exact conditions for these code paths.

**Coverage gap:** Multi-file search result handling and file move tracking not fully tested.

---

## 14. TAB TEXT UPDATE - LEGACY FORMAT (Lines 2560-2606)

**Location:** `TextEditor.on_tab_dropped()` method

```python
2560-2606:
                 # Handle legacy format support
                 else:
                     # Legacy format (just tab index)
                     if pane_info < self.tab_widget.count():
                         file_name = os.path.basename(new_file_path)
                         self.tab_widget.setTabText(pane_info, file_name)
```

**What it does:** Handles legacy file tracking format (before tuple format was introduced).

**Why uncovered:** Legacy code path that maintains backward compatibility with old data format. Not exercised in tests because the app uses the newer tuple format.

**Coverage gap:** Legacy file tracking format handling not tested (intentionally, as it's legacy).

---

## 15. TAB CLOSE - EMPTY PANE AUTO-CLEANUP (Lines 2660-2662)

**Location:** `TextEditor.remove_tab()` method

```python
2660:             # If there's more than one pane, close this pane instead of showing welcome
2661:             if len(self.split_panes) > 1:
2662:                 self.close_split_pane(self.active_pane)
```

**What it does:** Automatically closes a split pane when its last tab is closed.

**Why uncovered:** Requires:
1. Multiple split panes to exist
2. All tabs to be closed in one pane

Tests don't create this scenario.

**Coverage gap:** Automatic split pane cleanup when empty not tested.

---

## 16. FILE DELETION - DIRECTORY HANDLING (Lines 2676-2684)

**Location:** `TextEditor.delete_current_file()` method

```python
2676-2684:
                 elif is_dir:
                     # Check if any open files are in the deleted directory
                     for open_file_path in list(self.open_files.keys()):
                         if open_file_path.startswith(file_path):
                             # ... handle deletion ...
```

**What it does:** Handles deletion of directories containing open files.

**Why uncovered:** Requires:
1. Opening files in a directory
2. Deleting the parent directory
3. Properly cleaning up all child file references

No test creates this scenario.

**Coverage gap:** Directory deletion with open files not tested.

---

## 17. FILE MOVED - TAB UPDATE (Lines 2706)

**Location:** `TextEditor.update_moved_file_paths()` method

```python
2706:             self.tab_widget.setTabText(pane_info, file_name)
```

**What it does:** Updates tab text when a file is moved (legacy format path).

**Why uncovered:** Legacy code path - app uses tuple format, not legacy integer format.

**Coverage gap:** Legacy file move handling not tested.

---

## 18. FILE LOADING - REUSE LOGIC (Lines 2791-2802)

**Location:** `TextEditor.load_file()` method

```python
2791-2802:
                 # If file is in a different pane, we'll open it in the active pane
                 # (don't return, continue below)
                 elif pane_info != self.tab_widget.currentIndex():
                     # Check if this is in the active pane
                     for file_p, info in self.open_files.items():
                         if isinstance(info, tuple):
                             p, idx = info
```

**What it does:** Handles complex logic for loading files that are already open in other panes.

**Why uncovered:** Requires:
1. File to be open in a different split pane
2. File to be loaded again in active pane
3. Complex pane switching and tab state logic

No test exercises this scenario.

**Coverage gap:** Loading files already open in other panes not tested.

---

## 19. SYNTAX HIGHLIGHTING - FALLBACK (Lines 2853)

**Location:** `TextEditor.update_file_type()` method

```python
2853:         self.file_type_label.setText(file_types.get(ext, 'Plain Text'))
```

**What it does:** Falls back to "Plain Text" for unknown file extensions.

**Why uncovered:** Requires opening a file with an unknown/unusual extension. Test coverage focuses on common extensions.

**Coverage gap:** Unknown file extension handling not tested.

---

## 20. CURSOR POSITION - MISSING STATE CHECK (Line 3087-3089, 3097-3101, 3105)

**Location:** `TextEditor.update_cursor_position()` and `on_editor_focus_received()` methods

```python
3087-3089:
                 if not hasattr(self, 'cursor_label') or self.editor is None:
                     return
                 # ...

3097-3101:
                 # Check split panes
                 for pane in self.split_panes:
                      for i in range(pane.tab_widget.count()):
                           if pane.tab_widget.widget(i) is editor:

3105:
                 return  # Empty search
```

**What it does:** 
- Defensive checks for cursor position updates
- Split pane editor search logic
- Empty find result handling

**Why uncovered:** Defensive code and edge cases:
- `cursor_label` always exists (created in status bar)
- `editor` is always set to a valid CodeEditor
- Editor focus logic rarely hits all pane checks in tests

**Coverage gap:** Defensive null checks and edge case cursor tracking not tested.

---

## Summary by Category

| Category | Lines | Reason |
|----------|-------|--------|
| **Menu Creation** | ~60 | Menu bar initialization not directly tested |
| **Exception Handling** | ~20 | Requires simulated failures |
| **File Move/Delete Edge Cases** | ~25 | Complex multi-state scenarios |
| **Split Pane Management** | ~20 | Requires multiple panes with specific conditions |
| **Legacy Format Support** | ~10 | Legacy code path not exercised |
| **UI State Initialization** | ~15 | UI component setup not directly tested |

---

## Recommendations for Increasing Coverage

1. **Menu Testing** (Biggest opportunity, ~60 lines)
   - Create tests that trigger menu actions via QAction signals
   - Verify menu items are created and connected properly

2. **Split Pane Edge Cases** (~20 lines)
   - Test closing panes with unsaved files
   - Test automatic pane cleanup when empty
   - Test file moves between panes

3. **File System Operations** (~25 lines)
   - Test file deletion in open files
   - Test directory deletion
   - Test file moves with open file tracking

4. **Complex State Scenarios** (~20 lines)
   - Test loading files already open in other panes
   - Test tab drag/drop with conflict scenarios
   - Test pane switching with modified files

5. **Error Handling** (~10 lines)
   - Mock file I/O failures
   - Test exception paths in save/load operations

---

## Current Test Coverage Quality

- **Excellent:** Core editing functionality (typing, selection, scrolling), tab operations, basic file operations
- **Good:** Undo/redo, basic find/replace, zoom controls, syntax highlighting
- **Fair:** Split pane creation and switching, basic drag/drop
- **Poor:** Menu interactions, complex multi-pane scenarios, file system operations, edge cases
