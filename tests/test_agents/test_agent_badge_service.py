# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_agent_badge_service.py
# Content      : Unit tests for AgentBadgeService (TSK05, FN030/SU008)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the pure badge logic of state nodes.

Covers TSK05:
- badge_text: count display, '9+' beyond 9
- badge_visible: hidden at 0, visible at 1+
- tooltip_agents_line: empty list, up to 3 names, '+n more' beyond 3
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.services.agent_badge_service import AgentBadgeService


class TestBadgeText:

    def test_zero(self):
        assert AgentBadgeService.badge_text(0) == "0"

    def test_small_counts(self):
        assert AgentBadgeService.badge_text(1) == "1"
        assert AgentBadgeService.badge_text(5) == "5"
        assert AgentBadgeService.badge_text(9) == "9"

    def test_beyond_nine_capped(self):
        assert AgentBadgeService.badge_text(10) == "9+"
        assert AgentBadgeService.badge_text(42) == "9+"


class TestBadgeVisible:

    def test_hidden_at_zero(self):
        assert AgentBadgeService.badge_visible(0) is False

    def test_visible_from_one(self):
        assert AgentBadgeService.badge_visible(1) is True
        assert AgentBadgeService.badge_visible(15) is True


class TestTooltipAgentsLine:

    def test_empty(self):
        assert AgentBadgeService.tooltip_agents_line([]) == ""
        assert AgentBadgeService.tooltip_agents_line([None, ""]) == ""

    def test_single(self):
        assert AgentBadgeService.tooltip_agents_line(["Hero"]) == "Agents: Hero"

    def test_up_to_three_names(self):
        assert AgentBadgeService.tooltip_agents_line(
            ["Hero", "Sword", "Mentor"]) == "Agents: Hero, Sword, Mentor"

    def test_more_beyond_three(self):
        line = AgentBadgeService.tooltip_agents_line(
            ["Hero", "Sword", "Mentor", "Villain", "Oracle"])
        assert line == "Agents: Hero, Sword, Mentor +2 more"
