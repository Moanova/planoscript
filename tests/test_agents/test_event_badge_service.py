# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_event_badge_service.py
# Content      : Unit tests for EventBadgeService (TSK13)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the pure event badge logic of state nodes.

Covers TSK13:
- badge_text: count display, '9+' beyond 9
- badge_visible: hidden at 0, visible at 1+
- tooltip_events_line: 'in'/'out' directions, empty list, up to 3
  names, '+n more' beyond 3
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.services.event_badge_service import EventBadgeService


class TestBadgeText:

    def test_zero(self):
        assert EventBadgeService.badge_text(0) == "0"

    def test_small_counts(self):
        assert EventBadgeService.badge_text(1) == "1"
        assert EventBadgeService.badge_text(9) == "9"

    def test_beyond_max(self):
        assert EventBadgeService.badge_text(10) == "9+"
        assert EventBadgeService.badge_text(42) == "9+"


class TestBadgeVisible:

    def test_hidden_at_zero(self):
        assert EventBadgeService.badge_visible(0) is False

    def test_visible_from_one(self):
        assert EventBadgeService.badge_visible(1) is True
        assert EventBadgeService.badge_visible(9) is True


class TestTooltipEventsLine:

    def test_empty(self):
        assert EventBadgeService.tooltip_events_line("in", []) == ""
        assert EventBadgeService.tooltip_events_line("out", []) == ""

    def test_in_direction(self):
        assert (EventBadgeService.tooltip_events_line("in", ["Evt A"])
                == "Events (in): Evt A")

    def test_out_direction(self):
        assert (EventBadgeService.tooltip_events_line("out", ["Evt A", "Evt B"])
                == "Events (out): Evt A, Evt B")

    def test_up_to_three_names(self):
        labels = ["E1", "E2", "E3"]
        assert (EventBadgeService.tooltip_events_line("in", labels)
                == "Events (in): E1, E2, E3")

    def test_more_than_three_names(self):
        labels = ["E1", "E2", "E3", "E4", "E5"]
        assert (EventBadgeService.tooltip_events_line("out", labels)
                == "Events (out): E1, E2, E3 +2 more")

    def test_blank_labels_ignored(self):
        assert (EventBadgeService.tooltip_events_line("in", ["", None, "E1"])
                == "Events (in): E1")
