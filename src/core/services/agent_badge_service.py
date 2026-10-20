# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_badge_service.py
# Version      : 1
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Pure logic for agent badges on state nodes (TSK05, FN030/SU008).

Kept free of any Qt dependency so it can be unit tested without a
QApplication. The StateNode visual items consume these helpers.
"""


class AgentBadgeService:
    """Pure helpers for the agent badge of a state node."""

    BADGE_MAX_DISPLAY_COUNT = 9
    TOOLTIP_MAX_NAMES = 3

    @classmethod
    def badge_text(cls, count: int) -> str:
        """Return the text displayed in the badge for a given count.

        '9+' beyond 9 (the badge stays a fixed size regardless of the
        number of associated agents, for readability).
        """
        if count > cls.BADGE_MAX_DISPLAY_COUNT:
            return f"{cls.BADGE_MAX_DISPLAY_COUNT}+"
        return str(count)

    @classmethod
    def badge_visible(cls, count: int) -> bool:
        """The badge is hidden when no agent is associated."""
        return count > 0

    @classmethod
    def tooltip_agents_line(cls, agent_labels) -> str:
        """Return the 'Agents:' tooltip line for a list of agent labels.

        Lists at most TOOLTIP_MAX_NAMES names, then '+n more'.
        Returns an empty string for an empty list.
        """
        labels = [str(lb) for lb in agent_labels if lb]
        if not labels:
            return ""
        shown = labels[:cls.TOOLTIP_MAX_NAMES]
        line = "Agents: " + ", ".join(shown)
        remaining = len(labels) - len(shown)
        if remaining > 0:
            line += f" +{remaining} more"
        return line
