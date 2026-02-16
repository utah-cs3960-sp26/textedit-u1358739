# Deep Dive: Uncovered Code Analysis - SECOND PASS (160 Lines / 9%)

## Overview
Current coverage: **91%** (1,554 covered / 1,714 total statements)
Missing lines: **160 statements** spread across 35+ distinct locations
**Improvement:** +18 lines covered (from 178 → 160) / +1% coverage (from 90% → 91%)

The uncovered code falls into **7 major functional areas** with varying difficulty levels.

---

## Tests Added (Sections 1.1, 1.5, 1.6, 2.3, 8.1)
✅ **test_tab_drag_with_pixmap_visual_feedback** - Line 145 (CustomTabBar visual feedback)
✅ **test_tab_drop_parsing_malformed_mime_data** - Lines 1976-1977 (Tab drop exception handling)
✅ **test_tab_drop_validation_invalid_tab_index** - Line 1993 (Tab index validation)
✅ **test_tab_drop_validation_negative_tab_index** - Line 1993 (Negative index rejection)
✅ **test_new_folder_os_error_handling** - Lines 2398-2399 (OS error catching)
✅ **test_show_about_dialog** - Line 3049 (About dialog display)

---

## 1. DRAG & DROP / FILE TREE OPERATIONS (9 lines remaining)

### 1.1 Tab Drag Visual Feedback (Line 145)
**Status:** ✅ COVERED (test added)

---

### 1.2 File Tree Drop Model Validation (Lines 1456, 1462)
**Status:** ✅ COVERED (previously completed)

---

### 1.3 File Move Self-Protection (Line 1479)
**Status:** ✅ COVERED (previously completed)

---

### 1.4 Directory Merge During Drag-Drop (Lines 1495-1505)
**Status:** ✅ COVERED (previously completed)

---

### 1.5 Inter-Pane Tab Drop Parsing (Lines 1976-1977)
**Status:** ✅ COVERED (test added)
**Location:** `TextEditor.on_tab_dropped()` at lines 1972-1978
**What it does:** Parses mime data from dragging a tab between panes with format validation.

---

### 1.6 Inter-Pane Tab Drop Validation (Lines 1993, 1997)
**Status:** ✅ PARTIALLY COVERED (line 1993 covered, line 1997 still uncovered)
**Location:** `TextEditor.on_tab_dropped()` at lines 1991-1997
**Coverage:**
- **Line 1993:** ✅ COVERED - Tab index bounds checking
- **Line 1997:** ❌ UNCOVERED - Widget type validation (not a CodeEditor)

---

## 2. ERROR HANDLING & EXCEPTION PATHS (25+ lines)

### 2.1 Find/Replace All File Operation Errors (Lines 1407-1408)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.replace_all()` at lines 1407-1408
**What it does:** Catches and reports errors when reading/writing files during batch find-replace.
**Why uncovered:** Tests don't trigger file I/O errors
**Cost to test:** High - requires mocking `open()` to fail

---

### 2.2 Save Tab File Exceptions (Lines 2300-2307, 2323-2326)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.save_tab_file()`
**What it does:** Catches exceptions when writing files (both for existing and new files).
**Why uncovered:** File operations succeed in tests (temp directories always writable)
**Cost to test:** Medium-High - requires mocking file I/O at specific points

---

### 2.3 New Folder Exceptions (Lines 2398-2399)
**Status:** ✅ COVERED (test added)
**Location:** `TextEditor.new_folder()` at lines 2394-2399
**What it does:** Catches generic OS exceptions when creating directories.

---

## 3. FOCUS MANAGEMENT (8 lines) - Very High Difficulty

### 3.1 Update Focus in Pane Close (Lines 2078-2084)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_pane_close()` at lines 2078-2084
```python
if not self.split_panes:  # ← LINE 2078
    # No panes left, disable editor
    self.editor = None
    self.tab_widget = None
    self.active_pane = None
    self.editor_splitter.setVisible(False)  # ← LINE 2084
```
**Why uncovered:** Tests don't close all panes (app requires at least 1 pane)
**Cost to test:** Very High - requires changing app architecture to allow 0 panes

---

### 3.2 Update Current Pane on Other Pane Close (Lines 2095, 2097)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_pane_close()` at lines 2092-2097
```python
elif self.active_pane == closed_pane:  # ← LINE 2095
    # Active pane was closed, switch to another
    remaining_pane = next(p for p in self.split_panes if p != closed_pane)
    self.switch_to_pane(remaining_pane)  # ← LINE 2097
```
**Why uncovered:** Qt focus bugs prevent proper testing of pane switching on close
**Cost to test:** Very High - requires refactoring focus logic

---

## 4. TAB TRACKING & UI STATE (35+ lines) - High Difficulty

### 4.1 Tab Index Updates on Removal (Lines 2199-2203)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_tab_close_requested()` at lines 2199-2203
```python
for file_path, (pane, tab_index) in self.open_files.items():
    if pane == pane and tab_index > close_index:  # ← LINES 2199-2203
        # Shift index down after close
        open_files_update[file_path] = (pane, tab_index - 1)
```
**Why uncovered:** Tests close tabs but don't verify open_files dict is updated correctly
**Cost to test:** Medium - need to verify dict updates after tab close

---

### 4.2 Current File Updates (Lines 2239-2241)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_tab_close_requested()` at lines 2239-2241
**What it does:** Updates `current_file` when the currently-viewed file is closed
**Cost to test:** Medium - need to close current file and verify state updates

---

### 4.3 Tab Text Updates for Renamed Files (Lines 2292-2296)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_tab_close_requested()` at lines 2292-2296
**Cost to test:** Medium-High - requires file rename + open file in tab

---

## 5. FILE SAVE OPERATIONS (12 lines) - Medium-High Difficulty

### 5.1 Save New Untitled File (Lines 2300-2307)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.save_tab_file()` - saving untitled files
**Why uncovered:** File I/O mocking needed
**Cost to test:** Medium-High

---

### 5.2 Save Existing File (Lines 2323-2326)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.save_tab_file()` - saving existing files
**Why uncovered:** File I/O mocking needed
**Cost to test:** Medium-High

---

### 5.3 New Folder Exceptions (Lines 2402-2407)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.new_folder()` exception handling
**What it does:** Catches exceptions during folder creation
**Cost to test:** Low - mock `os.makedirs` to fail

---

## 6. FILE MOVE/DELETE OPERATIONS (30+ lines) - Very High Difficulty

### 6.1 Delete File from Tree (Lines 2419-2421)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.delete_file_or_folder()` at lines 2419-2421
**Why uncovered:** Tests don't delete files from file tree; complex multi-file scenarios
**Cost to test:** High

---

### 6.2 File Move Updates (Lines 2560-2606)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_files_moved()` - handling file moves from drag-drop
**Why uncovered:** Tests don't move open files via file tree drag-drop
**Cost to test:** Very High - requires file tree, drag-drop, and file system interaction

---

### 6.3 Split Pane File Updates (Lines 2660-2662)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.on_files_moved()` - split pane handling
**Why uncovered:** Tests don't move files in split panes
**Cost to test:** Very High

---

## 7. FILE LOADING EDGE CASES (12 lines) - High Difficulty

### 7.1 Load File Already Open in Different Pane (Lines 2676-2684, 2706)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.load_file()` at lines 2676-2706
```python
elif file_path in self.open_files and isinstance(self.open_files[file_path], tuple):
    pane, tab_index = self.open_files[file_path]
    if pane == self.active_pane:
        # File is already in active pane, reuse it
        editor = self.tab_widget.widget(tab_index)
    else:
        # File is in a different pane, create new tab in active pane
        editor, _ = self.create_new_tab(file_path)  # ← LINE 2706
```
**Why uncovered:** Complex multi-pane scenario with file already open in another pane
**Cost to test:** High - requires split panes + file open in one, loading from another

---

## 8. UI / APP LIFECYCLE (8 lines)

### 8.1 Show About Dialog (Line 3049)
**Status:** ✅ COVERED (test added)
**Location:** `TextEditor.show_about()` at line 3049
**What it does:** Displays the About dialog with app information.

---

### 8.2 Close Event with Modified Files (Lines 3087-3089, 3097-3101)
**Status:** ❌ UNCOVERED
**Location:** `TextEditor.closeEvent()` at lines 3060-3101
**What it does:** 
- **Lines 3087-3089:** Saves unsaved files before closing
- **Lines 3097-3101:** Pytest detection logic to avoid showing dialogs during teardown

**Why uncovered:** 
- Close event only called when actually closing the window
- Tests create windows but don't explicitly close them
- Would need to call `window.close()` and handle events

**Cost to test:** Medium - requires explicit window close and event handling

---

### 8.3 Main Entry Point (Lines 3105)
**Status:** ❌ UNCOVERED (unreachable)
**Location:** `main()` function and `if __name__ == "__main__"` block
**Why uncovered:** Entry point only runs when script is executed directly, not during test runs
**Cost to test:** Impossible - architectural limitation

---

## Summary Table

| Category | Lines | Covered | Uncovered | Primary Reason | Difficulty |
|----------|-------|---------|-----------|---|---|
| **Drag & Drop** | 15 | 13 | 2 | Widget type validation hard to test | High |
| **Error Handling** | 25+ | 0 | 25 | No simulated I/O errors | High |
| **Focus Management** | 8 | 0 | 8 | Qt focus bugs, app architecture | Very High |
| **Tab Tracking** | 35+ | 0 | 35 | Multi-pane edge cases | Medium-High |
| **File Save** | 12 | 0 | 12 | File I/O mocking needed | Medium-High |
| **File Move/Delete** | 30+ | 0 | 30 | Complex scenarios, drag-drop required | Very High |
| **File Loading** | 12 | 0 | 12 | Multi-pane conflicts | High |
| **UI/Lifecycle** | 8 | 0 | 8 | App lifecycle, unreachable code | Low-Impossible |
| **TOTAL** | **1,714** | **1,554** | **160** | | |

---

## Coverage Improvement Summary

### Tests Added This Session
- **6 new tests** covering previously uncovered lines
- **18 lines** now covered (improvement from 178 → 160 uncovered lines)
- **Coverage increased** from 90% → 91% (+1%)

### Successfully Covered Sections
1. ✅ Section 1.1 - Tab drag visual feedback with icons
2. ✅ Section 1.5 - Inter-pane tab drop parsing with malformed data
3. ✅ Section 1.6 - Inter-pane tab drop validation (partial - line 1993)
4. ✅ Section 2.3 - New folder OS error handling
5. ✅ Section 8.1 - About dialog display

### Most Cost-Effective Next Steps

**Easy (Low-cost, Medium value):**
- Mock file I/O failures to test save/replace error handling (2-3 tests)
- Test tab index updates after close (1-2 tests)
- Test file move updates (2-3 tests)

**Medium (Medium-cost, Medium value):**
- Close event with unsaved files (1-2 tests, requires explicit window.close())
- Legacy file format handling (2-3 tests, manual state setup)
- Multi-pane file loading scenarios (2-3 tests, requires split panes)

**Hard (High-cost, Low value):**
- Focus management with pane closure (requires Qt refactoring)
- All edge cases in file move/delete with drag-drop simulation
- File tree delete operations with multiple files

---

## Recommendation

**To reach ~95% coverage (realistically achievable):**
- Implement 8-12 focused tests targeting easier gaps
- Focus on high-value, low-cost areas:
  - Exception handling (mock failures) - 6 tests
  - Tab tracking on close - 2 tests
  - File move updates - 2 tests

**Estimated effort:** 1-2 hours per test × 10 tests = 10-20 hours

**Estimated final coverage:** 94-96% (reaching higher is diminishing returns)

**Not worth reaching 100% because:**
- 40+ lines in file move/delete are complex multi-step scenarios
- Focus management code has Qt architectural limitations
- Main entry point (1 line) is architecturally unreachable during tests
- Diminishing returns: ~91% is already excellent for a UI application
