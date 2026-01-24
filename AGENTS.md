# AGENTS.md

## Build/Test Commands

```bash
# Run all tests
pytest test_editor.py -v

# Run single test
pytest test_editor.py::TestClassName::test_method_name -v

# Run tests with coverage
pytest test_editor.py --cov=main

# Run the application
python main.py
```

## Architecture & Structure

Single-file application (`main.py`) implementing a VS Code-like text editor using PySide6 (Qt for Python).

**Core Classes:**
- `TextEditor` - Main window managing tabs, splits, file operations
- `CodeEditor` - Rich text editor with line numbers, syntax highlighting
- `SplitEditorPane` - Container for split views with custom headers
- `CustomTabWidget` - Tab management with close buttons and split functionality
- `FindReplaceDialog` - Find/replace functionality with case sensitivity options
- `LineNumberArea` - Line number gutter renderer

**Key Features:** Multi-tab editing, split views, file tree sidebar, find/replace, save/open, undo/redo, syntax highlighting, zoom, dark theme.

## Code Style Guidelines

- **Language:** Python 3 with PySide6 (Qt)
- **Formatting:** Follow PEP 8; imports organized (stdlib, Qt, local)
- **Classes:** CamelCase for all classes
- **Methods/Functions:** snake_case
- **Constants:** UPPER_CASE
- **Comments:** Use docstrings for classes/methods; inline comments for complex logic
- **Error Handling:** Use try/except with meaningful error messages via QMessageBox
- **File Operations:** Always normalize paths with `os.path.normpath()` for cross-platform compatibility
- **Signals:** Use Qt Signals for inter-component communication (prefer over direct calls)
- **Types:** No type hints currently used; maintain consistency with existing code

## Bug Fixing Process

When a task requires fixing a bug, follow this process:

1. **Write a failing test** - Create a test that verifies the desired functionality
2. **Verify the test fails** - Run the test and confirm it fails with the current code
3. **Fix the bug** - Implement the fix in the code
4. **Verify the test passes** - Run the test and confirm it now passes
5. **Reverify if needed** - If you modify the test during implementation, re-verify that the original code fails that test

This ensures the fix is correct and the test properly validates the behavior.
