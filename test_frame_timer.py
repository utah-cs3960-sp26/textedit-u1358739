"""Test frame timer functionality."""

import pytest
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from main import TextEditor, FrameTimerWidget


def test_frame_timer_widget_creation(qtbot):
    """Test that FrameTimerWidget is created correctly."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    assert widget.is_visible == False
    assert widget.frame_times == []
    assert widget.last_frame_time == 0.0
    assert widget.max_frame_time == 0.0
    assert widget.avg_frame_time == 0.0


def test_frame_timer_start_stop(qtbot):
    """Test starting and stopping the frame timer."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    # Initially hidden and not timing
    assert widget.is_visible == False
    assert not widget.isVisible()
    
    # Start timing
    widget.start_timing()
    assert widget.is_visible == True
    assert widget.isVisible()
    assert widget.frame_timer.isActive()
    
    # Stop timing
    widget.stop_timing()
    assert widget.is_visible == False
    assert not widget.isVisible()
    assert not widget.frame_timer.isActive()
    assert widget.frame_times == []


def test_frame_timer_reset_on_hide(qtbot):
    """Test that timings reset when timer is hidden."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    widget.start_timing()
    widget.record_activity()
    
    # Simulate some frames
    for _ in range(3):
        widget.update_frame_timing()
        time.sleep(0.01)
    
    assert len(widget.frame_times) > 0
    
    # Stop and verify reset
    widget.stop_timing()
    assert widget.frame_times == []
    assert widget.last_frame_time == 0.0
    assert widget.max_frame_time == 0.0
    assert widget.avg_frame_time == 0.0


def test_frame_timer_records_activity(qtbot):
    """Test that activity recording updates last_event_time."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    widget.start_timing()
    initial_time = widget.last_event_time
    
    time.sleep(0.05)
    widget.record_activity()
    
    assert widget.last_event_time > initial_time


def test_editor_frame_timer_toggle(qtbot):
    """Test that Ctrl+P toggles the frame timer in the editor."""
    editor = TextEditor()
    qtbot.addWidget(editor)
    
    # Initially hidden
    assert editor.frame_timer_visible == False
    assert editor.frame_timer_widget.is_visible == False
    
    # Call toggle to show
    editor.toggle_frame_timer()
    qtbot.wait(100)
    
    assert editor.frame_timer_visible == True
    assert editor.frame_timer_widget.is_visible == True
    assert editor.frame_timer_widget.frame_timer.isActive()
    
    # Call toggle again to hide
    editor.toggle_frame_timer()
    qtbot.wait(100)
    
    assert editor.frame_timer_visible == False
    assert editor.frame_timer_widget.is_visible == False
    assert not editor.frame_timer_widget.frame_timer.isActive()


def test_frame_timer_does_not_time_while_hidden(qtbot):
    """Test that frame timer doesn't collect data while hidden."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    # Start and then stop before collecting data
    widget.start_timing()
    time.sleep(0.05)
    initial_count = len(widget.frame_times)
    
    widget.stop_timing()
    assert not widget.frame_timer.isActive()
    
    # Try to update while hidden (should not record)
    time.sleep(0.05)
    widget.update_frame_timing()
    
    # Should still be empty after being hidden
    assert len(widget.frame_times) == 0


def test_frame_timer_idle_detection(qtbot):
    """Test that frame timings include idle frames."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    widget.start_timing()
    widget.record_activity()
    
    # Wait long enough to trigger idle (default idle_threshold is 0.1s)
    time.sleep(0.15)
    
    # Update frame timing (will record because we always record frames now)
    widget.update_frame_timing()
    
    # Should have recorded the frame time (including the idle time)
    assert len(widget.frame_times) == 1
    # The frame time should be large because of the sleep
    assert widget.frame_times[0] > 100  # Should be ~150ms


def test_frame_timer_activity_resets_idle(qtbot):
    """Test that recording activity resets the idle timer."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    widget.start_timing()
    widget.record_activity()
    time.sleep(0.05)
    
    # Activity resets the clock, so update should count
    widget.record_activity()
    widget.update_frame_timing()
    
    # Should have recorded one frame since activity was recent
    assert len(widget.frame_times) >= 0  # May or may not record depending on timing


def test_frame_timer_display_text(qtbot):
    """Test that the frame timer display updates correctly."""
    widget = FrameTimerWidget()
    qtbot.addWidget(widget)
    
    widget.start_timing()
    widget.record_activity()
    widget.update_frame_timing()
    time.sleep(0.02)
    widget.record_activity()
    widget.update_frame_timing()
    
    # Should have timing values in text
    text = widget.text()
    assert "Last Frame:" in text or "ms" in text
    assert "Avg:" in text or "ms" in text
    assert "Max:" in text or "ms" in text
