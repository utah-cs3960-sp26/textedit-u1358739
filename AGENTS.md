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

## Common Issues & Solutions

### Windows PowerShell Commands
This workspace uses Windows PowerShell, not Linux/Unix bash. Do NOT use Unix commands:
- ❌ `head`, `tail`, `wc`, `grep`, `ls`, `rm` - these don't work
- ✅ Use PowerShell equivalents instead:
  - `Get-Content file.txt -Tail 10` - view last 10 lines
  - `Get-Content file.txt | Measure-Object -Line | Select-Object -ExpandProperty Lines` - count lines
  - `dir` or `Get-ChildItem` - list files
  - `del` - delete files
  - `Select-String` - search text (like grep)

### Adding Tests Without Indentation Problems
When adding new test classes to `test_editor.py`:

1. **Use `edit_file` with a unique anchor** - Find the very end of the file (last line of the last test) and replace from there
2. **Ensure tests are top-level classes** - New test classes should be at indentation level 0 (no leading spaces)
3. **Include blank lines properly** - Add `\n\n` before the new class definition to separate from previous code
4. **Example:**
   ```python
   # Find the last line of the previous test
   old_str = """        # Last line of previous test
           assert something == True"""
   
   # Replace with the same line plus new test class at top level
   new_str = """        # Last line of previous test
           assert something == True


class TestNewFeature:
    """New test class - no indentation!"""
    
    def test_something(self, qtbot):
        """Test description."""
        pass"""
   ```
5. **Never nest classes** - If indentation looks nested, use `git checkout test_editor.py` to revert and try again
