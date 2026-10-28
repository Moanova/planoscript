# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : event_badge_service.py
# Version      : 1
# Date         : 28-10-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Pure logic for event badges on state nodes (TSK13).

A state node carries two event badges: a left one counting the source
events (Event_to_state arcs pointing to the state) and a right one
counting the target events (State_to_event arcs leaving the state).
Same display rules as the agent badge (TSK05): fixed-size pill with a
counter, hidden at 0, '9+' beyond 9.

Kept free of any Qt dependency so it can be unit tested without a
QApplication. The StateNode visual items consume these helpers.
"""


class EventBadgeService:
    """Pure helpers for the event badges of a state node."""

    BADGE_MAX_DISPLAY_COUNT = 9
    TOOLTIP_MAX_NAMES = 3

    @classmethod
    def badge_text(cls, count: int) -> str:
        """Return the text displayed in the badge for a given count.

        '9+' beyond 9 (the badge stays a fixed size regardless of the
        number of connected events, for readability).
        """
        if count > cls.BADGE_MAX_DISPLAY_COUNT:
            return f"{cls.BADGE_MAX_DISPLAY_COUNT}+"
        return str(count)

    @classmethod
    def badge_visible(cls, count: int) -> bool:
        """The badge is hidden when no event is connected."""
        return count > 0

    @classmethod
    def tooltip_events_line(cls, direction: str, event_labels) -> str:
        """Return the 'Events (in):' / 'Events (out):' tooltip line for
        a list of event labels.

        direction: 'in' (source events, left badge) or 'out' (target
        events, right badge). Lists at most TOOLTIP_MAX_NAMES names,
        then '+n more'. Returns an empty string for an empty list.
        """
        labels = [str(lb) for lb in event_labels if lb]
        if not labels:
            return ""
        shown = labels[:cls.TOOLTIP_MAX_NAMES]
        line = f"Events ({direction}): " + ", ".join(shown)
        remaining = len(labels) - len(shown)
        if remaining > 0:
            line += f" +{remaining} more"
        return line
