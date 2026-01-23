"""Test for active pane tracking when cursor moves between views."""

import pytest
from PySide6.QtCore import Qt
from main import TextEditor


class TestActivePaneTracking:
    """Tests for active pane tracking when cursor moves between views."""
    
    def test_cursor_movement_to_different_view_updates_active_pane(self, qtbot):
        """When cursor moves to a different view, that view becomes active."""
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create first pane and add some content
        initial_pane = window.active_pane
        initial_editor = window.tab_widget.widget(0)
        initial_editor.setPlainText("View 1")
        
        # Split the view
        window.add_split_view()
        
        # Get the panes
        assert len(window.split_panes) > 0
        split_pane = window.split_panes[0]
        second_editor = split_pane.tab_widget.widget(0)
        second_editor.setPlainText("View 2")
        
        # After splitting, the second pane becomes active
        # Now let's click on the first editor to make it active
        initial_editor.setFocus()
        
        # The active pane should now be the initial pane again
        first_pane_active = window.active_pane == initial_pane
        
        # Now click on the second editor to make it active
        second_editor.setFocus()
        
        # The active pane should now be the second pane
        assert window.active_pane == split_pane, "When cursor moves to split pane via setFocus(), that pane should become active"
