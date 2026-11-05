# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : export_service.py
# Version      : 1
# Date         : 01-11-2026
# Content      : Reading preview of the narrative map (SU010/FN033, TSK33)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Service building the reading preview of a narrative map (SU010/FN033, TSK33).

The preview is an HTML 4 subset rendered read-only in the "Export" workspace
(QTextBrowser). Decisions (docs/conception/export.md, TSK31):

- centered on states, from the initial state (RG031), in the real succession
  order of each journey (RG069: Journey_node.sequence_order); each state is
  listed only once; for each state (except the initial one), its predecessor
  events and associated agents are listed, annotated with their journey
  (via Journey_node);
- journey=None -> all journeys (summary + flow of each); journey=J ->
  journey J only (single summary entry); under an active journey filter,
  agent-state associations are restricted to the filtered journey;
- per component: label as title, content as body text (label only when the
  content is empty), type for states/agents, and the note as a tooltip on
  hover (note anchors "#note-<kind>-<id>", resolved via build_note_index);
- pending events (incoming arc without outgoing arc in the journey) are
  skipped in the flow and listed at the end of the flow with a marker;
- agents section (project level; restricted to the filtered journey when a
  journey is given) and orphan components section (states/events without any
  relation, agents without any association);
- links are inert in the workspace (setOpenLinks(False)); the preview never
  marks the map nor the project as modified.
"""

from html import escape
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import NarrativeMap, Journey, Agent


def _esc(text) -> str:
    return escape(text if text is not None else "")


def _label_html(kind: str, entity) -> str:
    """Label of a component; when the entity carries a note, the label is an
    inert anchor whose href indexes the note (tooltip on hover, workspace side)."""
    note = getattr(entity, 'note', None)
    if note:
        return f'<a href="#note-{kind}-{entity.id}">{_esc(entity.lb)}</a>'
    return _esc(entity.lb)


class ExportService:
    """Build the reading preview HTML of a narrative map (SU010/FN033)."""

    @staticmethod
    def build_reading_text(narrative_map: 'NarrativeMap',
                           journey: Optional['Journey'] = None,
                           agents: Optional[List['Agent']] = None) -> str:
        """Return the reading preview HTML of the map.

        Args:
            narrative_map: The narrative map to render
            journey: None -> all journeys; a Journey -> that journey only
                (active journey filter FN029)
            agents: Project agents (project.agent), for the agents section
                and agent labels of associations

        Returns:
            HTML 4 subset string (escaped user content).
        """
        journeys = [journey] if journey is not None else list(narrative_map.journey)
        agents = list(agents) if agents else []

        parts = [f"<h1>{_esc(narrative_map.lb)}</h1>"]
        # Summary of the rendered journeys (one entry when a filter is active)
        parts.append("<h2>Journeys</h2>")
        parts.append("<ul>")
        for j in journeys:
            parts.append(f'<li><a href="#journey-{j.id}">{_esc(j.lb)}</a></li>')
        parts.append("</ul>")
        # Flow per journey
        for j in journeys:
            parts.append(f'<h2 id="journey-{j.id}">{_esc(j.lb)}</h2>')
            parts.append(ExportService._journey_flow_html(narrative_map, j, agents))
        # Agents section, then orphan components
        parts.append(ExportService._agents_section_html(narrative_map, journey, agents))
        parts.append(ExportService._orphans_section_html(narrative_map, agents))
        return "\n".join(parts)

    @staticmethod
    def build_note_index(narrative_map: 'NarrativeMap',
                         agents: Optional[List['Agent']] = None) -> Dict[str, str]:
        """Map note anchor hrefs ("#note-<kind>-<id>") to the note text, for
        every entity of the map carrying a note (states, events, agents)."""
        index: Dict[str, str] = {}
        for kind, entities in (('state', narrative_map.state),
                               ('event', narrative_map.event),
                               ('agent', agents or [])):
            for e in entities:
                if getattr(e, 'note', None):
                    index[f"#note-{kind}-{e.id}"] = e.note
        return index

    # -----------------------------------------------------------------
    # Journey flow: states in succession order (RG069), each listed once
    # -----------------------------------------------------------------

    @staticmethod
    def _journey_flow_html(narrative_map: 'NarrativeMap', journey: 'Journey',
                           agents: List['Agent']) -> str:
        nodes = [n for n in narrative_map.journey_node if n.journey_id == journey.id]
        arc_nodes = sorted(
            (n for n in nodes
             if n.state_to_event_id is not None or n.event_to_state_id is not None),
            key=lambda n: n.sequence_order)
        stes = {a.id: a for a in narrative_map.state_to_event}
        e2s = {a.id: a for a in narrative_map.event_to_state}
        rels = {r.id: r for r in narrative_map.state_agent_rel}
        states = {s.id: s for s in narrative_map.state}
        events = {e.id: e for e in narrative_map.event}

        initial = next((s for s in narrative_map.state if s.typ == "Initial"), None)

        # State order: initial first, then by rank of the first incoming arc
        incoming_rank: Dict[int, int] = {}
        for n in arc_nodes:
            if n.event_to_state_id is not None:
                arc = e2s.get(n.event_to_state_id)
                if arc is not None:
                    incoming_rank.setdefault(arc.state_id, n.sequence_order)
        ordered_state_ids = ([initial.id] if initial else []) + \
            sorted(incoming_rank, key=lambda sid: incoming_rank[sid])

        # Events of the journey and pending ones (no outgoing arc in the journey)
        journey_event_ids = set()
        for n in arc_nodes:
            if n.state_to_event_id is not None:
                arc = stes.get(n.state_to_event_id)
                if arc is not None:
                    journey_event_ids.add(arc.event_id)
        outgoing_event_ids = set()
        for n in arc_nodes:
            if n.event_to_state_id is not None:
                arc = e2s.get(n.event_to_state_id)
                if arc is not None:
                    outgoing_event_ids.add(arc.event_id)
        pending_event_ids = journey_event_ids - outgoing_event_ids

        parts: List[str] = []
        for sid in ordered_state_ids:
            state = states.get(sid)
            if state is None:
                continue
            typ = f" ({_esc(state.typ)})" if state.typ else ""
            parts.append(f"<h3>State {_label_html('state', state)}{typ}</h3>")
            items: List[str] = []
            # Predecessor events (incoming arcs of the journey), rank order
            preds = sorted(
                (n for n in arc_nodes
                 if n.event_to_state_id is not None
                 and e2s.get(n.event_to_state_id) is not None
                 and e2s[n.event_to_state_id].state_id == sid),
                key=lambda n: n.sequence_order)
            for n in preds:
                event = events.get(e2s[n.event_to_state_id].event_id)
                if event is None:
                    continue
                item = (f"<li>Event {_label_html('event', event)}"
                        f" — journey «{_esc(journey.lb)}»")
                if event.content:
                    item += f"<br/>{_esc(event.content)}"
                items.append(item + "</li>")
            # Associated agents (associations of the journey on this state)
            assoc_nodes = sorted(
                (n for n in nodes
                 if n.state_agent_rel_id is not None
                 and rels.get(n.state_agent_rel_id) is not None
                 and rels[n.state_agent_rel_id].state_id == sid),
                key=lambda n: n.sequence_order)
            for n in assoc_nodes:
                rel = rels[n.state_agent_rel_id]
                agent = next((a for a in agents if a.id == rel.agent_id), None)
                label = _label_html('agent', agent) if agent is not None \
                    else f"Agent #{_esc(rel.agent_id)}"
                typ = f" ({_esc(agent.typ)})" if agent is not None and agent.typ else ""
                items.append(f"<li>Agent {label}{typ} — journey «{_esc(journey.lb)}»</li>")
            if items:
                parts.append("<ul>" + "\n".join(items) + "</ul>")
            if state.content:
                parts.append(f"<p>{_esc(state.content)}</p>")

        # Pending events: skipped in the flow, listed at the end with a marker
        if pending_event_ids:
            items = [f"<li>{_label_html('event', events[eid])} (pending)</li>"
                     for eid in sorted(pending_event_ids)
                     if eid in events]
            if items:
                parts.append("<p><i>Pending events (no successor state):</i></p>")
                parts.append("<ul>" + "\n".join(items) + "</ul>")
        return "\n".join(parts)

    # -----------------------------------------------------------------
    # Agents section (project level; restricted to the journey when filtered)
    # -----------------------------------------------------------------

    @staticmethod
    def _agents_section_html(narrative_map: 'NarrativeMap',
                             journey: Optional['Journey'],
                             agents: List['Agent']) -> str:
        if journey is not None:
            rel_ids = {n.state_agent_rel_id for n in narrative_map.journey_node
                       if n.journey_id == journey.id and n.state_agent_rel_id is not None}
            agent_ids = {r.agent_id for r in narrative_map.state_agent_rel
                         if r.id in rel_ids}
            selected = [a for a in agents if a.id in agent_ids]
        else:
            selected = list(agents)
        parts = ["<h2>Agents</h2>"]
        for a in selected:
            typ = f" ({_esc(a.typ)})" if a.typ else ""
            parts.append(f'<h3 id="agent-{a.id}">Agent {_label_html("agent", a)}{typ}</h3>')
            if a.content:
                parts.append(f"<p>{_esc(a.content)}</p>")
        return "\n".join(parts)

    # -----------------------------------------------------------------
    # Orphan components (no relation at all, RG026)
    # -----------------------------------------------------------------

    @staticmethod
    def _orphans_section_html(narrative_map: 'NarrativeMap',
                              agents: List['Agent']) -> str:
        related_states = ({a.state_id for a in narrative_map.state_to_event}
                          | {a.state_id for a in narrative_map.event_to_state}
                          | {r.state_id for r in narrative_map.state_agent_rel})
        related_events = ({a.event_id for a in narrative_map.state_to_event}
                          | {a.event_id for a in narrative_map.event_to_state})
        orphans = ([f"<li>State {_esc(s.lb)}</li>" for s in narrative_map.state
                    if s.id not in related_states]
                   + [f"<li>Event {_esc(e.lb)}</li>" for e in narrative_map.event
                      if e.id not in related_events]
                   + [f"<li>Agent {_esc(a.lb)}</li>" for a in agents
                      if not any(r.agent_id == a.id
                                 for r in narrative_map.state_agent_rel)])
        parts = ["<h2>Orphan components</h2>"]
        if orphans:
            parts.append("<ul>" + "\n".join(orphans) + "</ul>")
        else:
            parts.append("<p><i>None</i></p>")
        return "\n".join(parts)
