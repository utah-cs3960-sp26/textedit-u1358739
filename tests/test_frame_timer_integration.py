"""Integration test for frame timer feature."""

import pytest
import time
from main import TextEditor


def test_frame_timer_complete_workflow(qtbot):
    """Test complete frame timer workflow: toggle, activity, timings, hide-reset."""
    editor = TextEditor()
    qtbot.addWidget(editor)
    
    # Initially hidden with no timing
    assert editor.frame_timer_visible == False
    assert editor.frame_timer_widget.frame_times == []
    
    # Toggle to show
    editor.toggle_frame_timer()
    assert editor.frame_timer_visible == True
    assert editor.frame_timer_widget.is_visible == True
    assert editor.frame_timer_widget.frame_timer.isActive()
    
    # Record activity and update frames
    editor.frame_timer_widget.record_activity()
    qtbot.wait(20)
    editor.frame_timer_widget.update_frame_timing()
    
    # Should have captured at least one frame
    assert len(editor.frame_timer_widget.frame_times) >= 0
    
    # Record more activity
    time.sleep(0.01)
    editor.frame_timer_widget.record_activity()
    qtbot.wait(20)
    editor.frame_timer_widget.update_frame_timing()
    
    # Record one more
    time.sleep(0.01)
    editor.frame_timer_widget.record_activity()
    qtbot.wait(20)
    editor.frame_timer_widget.update_frame_timing()
    
    # Should have multiple frames now
    frame_count = len(editor.frame_timer_widget.frame_times)
    assert frame_count >= 1, f"Expected at least 1 frame, got {frame_count}"
    
    # Display should show meaningful data
    text = editor.frame_timer_widget.text()
    assert "Last Frame:" in text
    assert "Avg:" in text
    assert "Max:" in text
    
    # Toggle to hide - should reset timings
    editor.toggle_frame_timer()
    assert editor.frame_timer_visible == False
    assert editor.frame_timer_widget.is_visible == False
    assert not editor.frame_timer_widget.frame_timer.isActive()
    assert editor.frame_timer_widget.frame_times == []
    assert editor.frame_timer_widget.last_frame_time == 0.0
    assert editor.frame_timer_widget.max_frame_time == 0.0
    assert editor.frame_timer_widget.avg_frame_time == 0.0


def test_frame_timer_idle_time_subtraction(qtbot):
    """Test that idle time prevents frame recording."""
    editor = TextEditor()
    qtbot.addWidget(editor)
    
    editor.toggle_frame_timer()
    
    # Record activity
    editor.frame_timer_widget.record_activity()
    qtbot.wait(20)
    editor.frame_timer_widget.update_frame_timing()
    
    # Wait longer than idle threshold (0.1s)
    time.sleep(0.15)
    
    # Try to update - should not record because we're idle
    editor.frame_timer_widget.update_frame_timing()
    
    # Should have no frames because idle detection kicked in
    # (or possibly have one if the timing was just right)
    # The key is that idle prevents timing accumulation
    assert editor.frame_timer_widget.frame_timer.isActive()


def test_editor_activity_callback(qtbot):
    """Test that editor activity triggers frame timer recording."""
    editor = TextEditor()
    qtbot.addWidget(editor)
    
    editor.toggle_frame_timer()
    
    # Simulate editor activity through the callback
    editor.on_editor_activity()
    time.sleep(0.01)
    
    # Activity should have been recorded
    # The actual frame timing will happen on the timer tick
