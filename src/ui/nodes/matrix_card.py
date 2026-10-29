# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : matrix_card.py
# Version      : 1
# Date         : 26-10-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Graphical items of the agents x states matrix (TSK15).

The agents workspace matrix is a QGraphicsView (like the events
workspace): each State and each Agent is drawn as a card with the same
appearance as the events nodes (rounded rectangle, surface background,
type-colored outline, centered label, hover outline, immediate tooltip).
Agents use the event tint (copper): agents have no node in the events
view (decision TSC 26-10-2026).

Each intersection of an agent row and a state column holds a
``MatrixCheckItem``: a always-visible checkbox (20x20 by default, from
config.json) whose click toggles the association. The click is active
only inside the checkbox rect; clicking anywhere else on the card is a
no-op (TSK12 point 09 behavior, preserved).
"""

from PySide6.QtCore import QEvent, QPointF, Qt, QRectF
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPainterPath, QPen
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QToolTip
)

from config.config_loader import get as _get_config
from core.services.event_badge_service import EventBadgeService
from ui.utils import theme


class MatrixCardItem(QGraphicsRectItem):
    """A card of the agents matrix (state column header or agent row
    header), rendered like an events node.

    Not movable by itself: the agents workspace controls the drag (RG068
    reordering, initial state pinned). Reports press/release positions
    through callbacks set by the workspace.

    Selectable (TSK13 review): like the events nodes, a card can be
    selected; the selection is shown by a dashed outline in the type
    color (charter 98: selection > hover > type). A click selects the
    card, a drag still reorders it (RG068).

    Event badges (TSK13, agents view only): a state card carries two
    badges at the bottom, same pill + counter style as the agent badge
    of the events view — left badge = source events (Event_to_state
    arcs pointing to the state), right badge = target events
    (State_to_event arcs leaving the state), copper fill (event tint).
    Agent cards carry no event badge.
    """

    WIDTH = _get_config("node_default_width", 80.0)
    HEIGHT = _get_config("node_default_height", 40.0)
    CORNER_RADIUS = _get_config("node_corner_radius_px", 6.0)
    HOVER_BORDER_COLOR = theme.color("hover_color", theme.HOVER_COLOR)

    LABEL_MAX_DISPLAY_LENGTH = 8  # same truncation rule as BaseNode

    # Event badge constants (state cards): same style as the events
    # agent badge (charter 98), copper fill (event tint) per the TSK13
    # decision. Position: centered vertically; horizontally, mostly
    # inside the outline — 2/3 in, 1/3 out (TSK18, same horizontal rule
    # as the events agent badge, TSK17) — so the badge still marks the
    # same side as the events connection port it counts (input left,
    # output right).
    EVENT_BADGE_DIAMETER = 16.0
    EVENT_BADGE_BG_COLOR = theme.color(
        "event_badge_bg_color", theme.EVENT_COLOR)
    EVENT_BADGE_BORDER_COLOR = theme.color(
        "badge_border_color", theme.BADGE_BORDER_COLOR)
    EVENT_BADGE_TEXT_COLOR = theme.color(
        "badge_text_color", theme.BADGE_TEXT_COLOR)

    def __init__(self, entity, kind, border_color, parent=None):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT, parent)
        self.entity = entity
        # 'state' or 'agent': resolved by the workspace from this item
        self.kind = kind
        self._border_color = QColor(border_color)
        self.event_badge_in = None
        self.event_badge_in_text = None
        self.event_badge_out = None
        self.event_badge_out_text = None
        self._source_event_labels = []
        self._target_event_labels = []
        if kind == 'state':
            self._init_event_badges()
        self._hovered = False

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

        self.setPen(QPen(self._border_color, 2))
        self.setBrush(QBrush(theme.color("bg_surface", theme.BG_SURFACE)))

        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(self.display_label(entity.lb))
        font = QFont(theme.FONT_FAMILY, theme.NODE_LABEL_FONT_SIZE_PX)
        self.label.setFont(font)
        self.label.setDefaultTextColor(
            theme.color("text_primary", theme.TEXT_PRIMARY))
        self.label.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._position_label()

        self.setToolTip(self._tooltip_text())

    @classmethod
    def display_label(cls, lb) -> str:
        """Label truncation rule shared with BaseNode."""
        text = str(lb) if lb else ''
        if len(text) > cls.LABEL_MAX_DISPLAY_LENGTH:
            return text[:cls.LABEL_MAX_DISPLAY_LENGTH]
        return text

    def _tooltip_text(self) -> str:
        tooltip = str(self.entity.lb) if self.entity.lb else ''
        typ = getattr(self.entity, 'typ', None)
        if typ:
            tooltip += f"\nType: {typ}"
        note = getattr(self.entity, 'note', None)
        if note:
            tooltip += f"\n{note}"
        # Event badge lines (state cards only, TSK13)
        events_in_line = EventBadgeService.tooltip_events_line(
            "in", self._source_event_labels)
        if events_in_line:
            tooltip += f"\n{events_in_line}"
        events_out_line = EventBadgeService.tooltip_events_line(
            "out", self._target_event_labels)
        if events_out_line:
            tooltip += f"\n{events_out_line}"
        return tooltip

    def _position_label(self) -> None:
        text_rect = self.label.boundingRect()
        self.label.setPos(
            (self.rect().width() - text_rect.width()) / 2,
            (self.rect().height() - text_rect.height()) / 2)

    def _init_event_badges(self) -> None:
        """Create the event badge items of a state card (left: source
        events, right: target events), hidden by default (TSK13)."""
        diameter = self.EVENT_BADGE_DIAMETER
        font = QFont(theme.FONT_FAMILY, 7)
        font.setBold(True)

        self.event_badge_in = QGraphicsEllipseItem(
            0, 0, diameter, diameter, self)
        self.event_badge_in.setBrush(QBrush(self.EVENT_BADGE_BG_COLOR))
        self.event_badge_in.setPen(QPen(self.EVENT_BADGE_BORDER_COLOR))
        self.event_badge_in.setFlag(
            QGraphicsItem.ItemIsSelectable, False)
        self.event_badge_in.setFlag(
            QGraphicsItem.ItemIsMovable, False)
        self.event_badge_in.setAcceptedMouseButtons(
            Qt.MouseButton.NoButton)
        self.event_badge_in_text = QGraphicsTextItem(self.event_badge_in)
        self.event_badge_in_text.setFont(font)
        self.event_badge_in_text.setDefaultTextColor(
            self.EVENT_BADGE_TEXT_COLOR)

        self.event_badge_out = QGraphicsEllipseItem(
            0, 0, diameter, diameter, self)
        self.event_badge_out.setBrush(QBrush(self.EVENT_BADGE_BG_COLOR))
        self.event_badge_out.setPen(QPen(self.EVENT_BADGE_BORDER_COLOR))
        self.event_badge_out.setFlag(
            QGraphicsItem.ItemIsSelectable, False)
        self.event_badge_out.setFlag(
            QGraphicsItem.ItemIsMovable, False)
        self.event_badge_out.setAcceptedMouseButtons(
            Qt.MouseButton.NoButton)
        self.event_badge_out_text = QGraphicsTextItem(self.event_badge_out)
        self.event_badge_out_text.setFont(font)
        self.event_badge_out_text.setDefaultTextColor(
            self.EVENT_BADGE_TEXT_COLOR)

        self.event_badge_in.hide()
        self.event_badge_out.hide()
        self._position_event_badges()

    def _position_event_badges(self) -> None:
        """Place the event badges on the state card: centered vertically,
        and on the horizontal axis mostly inside the outline — two
        thirds inside, one third outside (TSK18, TSC 29-10-2026, same
        horizontal rule as the events agent badge TSK17). The outside
        part is one third of the diameter, rounded to an integer
        (= 5 px on a 16 px diameter). The left badge (source events)
        stays on the left side, the right badge (target events) on the
        right side — the same sides as the events connection ports.
        """
        if self.event_badge_in is None:
            return
        diameter = self.EVENT_BADGE_DIAMETER
        outside = round(diameter / 3)
        rect = self.rect()
        y = rect.height() / 2 - diameter / 2
        self.event_badge_in.setPos(-outside, y)
        text_rect = self.event_badge_in_text.boundingRect()
        self.event_badge_in_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )
        x = rect.width() - diameter + outside
        self.event_badge_out.setPos(x, y)
        text_rect = self.event_badge_out_text.boundingRect()
        self.event_badge_out_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )

    def refresh_event_badges(self, in_count: int, out_count: int,
                             in_labels=None, out_labels=None) -> None:
        """Refresh the event badges of a state card (TSK13, agents view).

        The left badge counts the source events (Event_to_state arcs
        pointing to the state), the right badge the target events
        (State_to_event arcs leaving the state). Badges are hidden at 0;
        they show the count ('9+' beyond 9). The tooltip event lines are
        updated from the event labels when provided.
        """
        self._source_event_labels = list(in_labels or [])
        self._target_event_labels = list(out_labels or [])
        for badge, text_item, count in (
                (self.event_badge_in, self.event_badge_in_text, in_count),
                (self.event_badge_out, self.event_badge_out_text,
                 out_count)):
            if EventBadgeService.badge_visible(count):
                text_item.setPlainText(EventBadgeService.badge_text(count))
                badge.show()
            else:
                badge.hide()
        self._position_event_badges()
        # Refresh the tooltip so the events lines stay in sync
        self.setToolTip(self._tooltip_text())

    def set_highlighted(self, highlighted: bool) -> None:
        """Focus highlight (TSK10): raised surface instead of the type
        outline; restores the type outline when cleared."""
        if highlighted:
            self.setBrush(QBrush(QColor(theme.FOCUS_COLOR)))
        else:
            self.setBrush(QBrush(theme.color("bg_surface", theme.BG_SURFACE)))

    def itemChange(self, change, value):
        """Apply the charter 98 outline priority (selection > hover >
        type) when the selection changes (TSK13 review). During
        ItemSelectedChange, isSelected() still holds the previous
        state, so the new value is passed explicitly (same pattern as
        BaseNode._apply_outline)."""
        if change == QGraphicsItem.ItemSelectedChange:
            self._apply_outline(selected=bool(value))
        return super().itemChange(change, value)

    def _apply_outline(self, selected=None) -> None:
        """Apply the outline according to the priority rule (charter
        98): selection (dashed, type color) > hover (soft white, solid)
        > type. DashLine with a 6/4 pattern matches the charter's dotted
        selection outline (Qt.DotLine renders a fixed dot pattern).

        Args:
            selected: Explicit selection state. During
                itemChange(ItemSelectedChange), isSelected() still
                holds the previous state, so the new value must be
                passed.
        """
        if selected if selected is not None else self.isSelected():
            pen = QPen(self._border_color, 2)
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern([6.0, 4.0])
            pen.setCapStyle(Qt.FlatCap)
            self.setPen(pen)
        elif self._hovered:
            self.setPen(QPen(self.HOVER_BORDER_COLOR, 2))
        else:
            self.setPen(QPen(self._border_color, 2))

    def _rounded_path(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.CORNER_RADIUS,
                            self.CORNER_RADIUS)
        return path

    def boundingRect(self):
        return self._rounded_path().boundingRect().adjusted(-2, -2, 2, 2)

    def shape(self):
        return self._rounded_path()

    def paint(self, painter, option, widget=None) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self._rounded_path())

    def hoverEnterEvent(self, event) -> None:
        self._hovered = True
        self._apply_outline()
        # Immediate tooltip (AGENTS.md pattern): the workspace swallows
        # Qt's delayed automatic tooltip event
        lb = getattr(self.entity, 'lb', None)
        if lb:
            self.setToolTip(str(lb))
            QToolTip.showText(event.screenPos(), str(lb))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self._apply_outline()
        QToolTip.hideText()
        super().hoverLeaveEvent(event)


class MatrixCheckItem(QGraphicsRectItem):
    """The association checkbox of one matrix cell (TSK15).

    Always visible, centered on its cell rect. Checked = association
    exists: filled with the checkbox color and a light check mark;
    unchecked = outline only. The click is active only inside the
    checkbox rect (mousePressEvent on this item); the parent workspace
    is notified through the ``toggled`` callback with the entity pair.
    """

    SIZE = _get_config("agents_view_checkbox_size", 20)
    BOX_COLOR = theme.color("agents_view_checkbox_color", "#383838")
    CHECK_COLOR = theme.color("agents_view_checkbox_check_color", "#F0F0F0")

    def __init__(self, agent, state, checked, parent=None):
        super().__init__(0, 0, self.SIZE, self.SIZE, parent)
        self.agent = agent
        self.state = state
        self._checked = bool(checked)
        self._hovered = False
        self._highlighted = False

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)

        self.toggled = None  # callback(agent, state, new_checked)
        self.setToolTip(f"{agent.lb} / {state.lb}")

    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Update the visual state (no callback, no use case)."""
        self._checked = bool(checked)
        self.update()

    def set_highlighted(self, highlighted: bool) -> None:
        """Focus highlight (TSK10): lighten the checkbox while its
        column is focused."""
        self._highlighted = bool(highlighted)
        self.update()

    def boundingRect(self):
        return self.rect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        if self._checked:
            painter.setBrush(QBrush(self.BOX_COLOR))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._highlighted:
            pen_color = QColor(self.CHECK_COLOR)
        elif self._hovered:
            pen_color = self.CHECK_COLOR
        else:
            pen_color = self.BOX_COLOR
        painter.setPen(QPen(pen_color, 2))
        painter.drawRoundedRect(rect, 3.0, 3.0)
        if self._checked:
            # Check mark: two segments inside the box
            painter.setPen(QPen(self.CHECK_COLOR, 2))
            w, h = rect.width(), rect.height()
            painter.drawLine(QPointF(rect.left() + w * 0.22,
                                     rect.top() + h * 0.52),
                             QPointF(rect.left() + w * 0.44,
                                     rect.top() + h * 0.74))
            painter.drawLine(QPointF(rect.left() + w * 0.44,
                                     rect.top() + h * 0.74),
                             QPointF(rect.left() + w * 0.80,
                                     rect.top() + h * 0.26))

    def mousePressEvent(self, event) -> None:
        """Toggle only on a left click inside the checkbox rect."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.toggled is not None:
                self.toggled(self.agent, self.state, not self._checked)
            event.accept()
            return
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().hoverLeaveEvent(event)
