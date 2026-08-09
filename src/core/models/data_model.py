# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : data_model.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import json

# ---------------------------------------------------------------------
# Entity classes
# ---------------------------------------------------------------------
@dataclass
class BaseEntity:
    """Base class for all entities with common fields."""
    creation_date_time: datetime
    modification_date_time: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Time_ref(BaseEntity):
    """
    Time_ref (Timeline Reference)
    Represents a timeline reference point of the narrative map.
    """
    id: int
    lb: str
    desc: Optional[str] = None
    prev_id: int = 0  # Previous Time_ref Id

    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.prev_id, int):
            self.prev_id = int(self.prev_id)


@dataclass
class Space_ref(BaseEntity):
    """
    Space_ref (Spatial Reference)
    Represents a spatial reference point of the narrative map.
    """
    id: int
    lb: str
    desc: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)


@dataclass
class Agent(BaseEntity):
    """
    Agent
    Represents a agent, person or object, of the narrative map.
    """
    id: int
    lb: str
    desc: Optional[str] = None
    typ: str = "Sujet"  # Type of agent ("Subject" or "Object")
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.typ, str):
            self.typ = str(self.typ)


@dataclass
class State(BaseEntity):
    """
    State
    Represents a status of the narrative map, linked to an agent or not, linked to an event or not.
    """
    id: int
    lb: str
    space_ref_id: Optional[int]  # Linked Space_ref Id
    time_ref_id: int = 0  # Linked Time_ref Id
    desc: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.time_ref_id, int):
            self.time_ref_id = int(self.time_ref_id)


@dataclass
class Event(BaseEntity):
    """
    Event
    Represents an event of the narrative map.
    """
    id: int
    lb: str
    space_ref_id: Optional[int]  # Linked Space_ref Id
    time_ref_id: int = 0  # Linked Time_ref Id
    desc: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.time_ref_id, int):
            self.time_ref_id = int(self.time_ref_id)


@dataclass
class Journey(BaseEntity):
    """
    Journey
    Represents a sequence of states and events (subset of the State-to-event tree).
    """
    id: int
    lb: str
    desc: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)


@dataclass
class Chapter(BaseEntity):
    """
    Chapter
    Represents a sequence of journeys (subset of the Journey tree).
    """
    id: int
    lb: str
    desc: Optional[str] = None
    prev_id: int = 0  # Previous Chapter Id

    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.prev_id, int):
            self.prev_id = int(self.prev_id)


# ---------------------------------------------------------------------
# Relation Classes
# ---------------------------------------------------------------------
@dataclass
class Agent_rel_hist(BaseEntity):
    """
    Relation history if two agents.
    """
    id: int
    agent_1_id: int
    agent_2_id: int
    state_id: Optional[int]  # Linked State Id
    time_ref_id: int = 0  # Linked Time_ref Id
    desc: Optional[str] = None

    def __post_init__(self):
        for attr in ['id', 'agent_1_id', 'agent_2_id', 'time_ref_id', 'state_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class Agent_state_rel(BaseEntity):
    """
    Relation between an agent and a state.
    """
    id: int
    agent_id: int
    state_id: int
    note: Optional[str] = None

    def __post_init__(self):
        for attr in ['id', 'agent_id', 'state_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class Agent_event_rel(BaseEntity):
    """
    Relation between an agent and an event.
    """
    id: int
    agent_id: int
    event_id: int
    note: Optional[str] = None

    def __post_init__(self):
        for attr in ['id', 'agent_id', 'event_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class State_event_rel(BaseEntity):
    """
    Relation of a state to an event.
    """
    id: int
    state_id: int
    event_id: int
    note: Optional[str] = None

    def __post_init__(self):
        for attr in ['id', 'state_id', 'event_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class Event_state_rel(BaseEntity):
    """
    Relation of an event to a state.
    """
    id: int
    event_id: int
    state_id: int
    note: Optional[str] = None

    def __post_init__(self):
        for attr in ['id', 'event_id', 'state_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class State_event_tree(BaseEntity):
    """
    Tree of a State-to-event relation.
    """
    id: int
    state_event_id: int  # Linked State_event_rel Id
    prev_state_event_id: int = 0  # Previous State_event_rel Id

    def __post_init__(self):
        for attr in ['id', 'state_event_id', 'prev_state_event_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class State_event_subtree(BaseEntity):
    """
    Subset of a State_event_tree object.
    """
    id: int
    state_event_tree_id: int  # Linked State_event_tree Id
    journey_id: int  # Linked Journey Id
    
    def __post_init__(self):
        for attr in ['id', 'state_event_tree_id', 'journey_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class Journey_tree(BaseEntity):
    """
    Tree of journeys.
    """
    id: int
    journey_id: int
    prev_journey_id: int = 0  # Previous Journey Id
    
    def __post_init__(self):
        for attr in ['id', 'journey_id', 'prev_journey_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


@dataclass
class Journey_subtree(BaseEntity):
    """
    Relation between a journey and a chapter.
    """
    id: int
    journey_tree_id: int  # Linked Journey_tree Id
    chapter_id: int  # Linked Chapter Id
    
    def __post_init__(self):
        for attr in ['id', 'journey_tree_id', 'chapter_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))


# ---------------------------------------------------------------------
# Narrative Map Container
# ---------------------------------------------------------------------
@dataclass
class NarrativeMap(BaseEntity):
    """
    Narrative Map
    Container for all narrative map content (entities and relations).
    """
    id: str  # UUID
    lb: str

    time_ref: List[Time_ref] = field(default_factory=list)
    space_ref: List[Space_ref] = field(default_factory=list)
    agent: List[Agent] = field(default_factory=list)
    state: List[State] = field(default_factory=list)
    event: List[Event] = field(default_factory=list)
    journey: List[Journey] = field(default_factory=list)
    chapter: List[Chapter] = field(default_factory=list)

    agent_rel_hist: List[Agent_rel_hist] = field(default_factory=list)
    agent_state_rel: List[Agent_state_rel] = field(default_factory=list)
    agent_event_rel: List[Agent_event_rel] = field(default_factory=list)
    state_event_rel: List[State_event_rel] = field(default_factory=list)
    event_state_rel: List[Event_state_rel] = field(default_factory=list)
    state_event_tree: List[State_event_tree] = field(default_factory=list)
    state_event_subtree: List[State_event_subtree] = field(default_factory=list)
    journey_tree: List[Journey_tree] = field(default_factory=list)
    journey_subtree: List[Journey_subtree] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lb': self.lb,
            'creation_date_time': self.creation_date_time.isoformat(),
            'modification_date_time': self.modification_date_time.isoformat() if self.modification_date_time else None,
            'time_ref': [t.to_dict() for t in self.time_ref],
            'space_ref': [s.to_dict() for s in self.space_ref],
            'agent': [a.to_dict() for a in self.agent],
            'state': [s.to_dict() for s in self.state],
            'event': [e.to_dict() for e in self.event],
            'journey': [j.to_dict() for j in self.journey],
            'chapter': [c.to_dict() for c in self.chapter],
            'agent_rel_hist': [a.to_dict() for a in self.agent_rel_hist],
            'agent_state_rel': [a.to_dict() for a in self.agent_state_rel],
            'agent_event_rel': [a.to_dict() for a in self.agent_event_rel],
            'state_event_rel': [s.to_dict() for s in self.state_event_rel],
            'event_state_rel': [e.to_dict() for e in self.event_state_rel],
            'state_event_tree': [s.to_dict() for s in self.state_event_tree],
            'state_event_subtree': [s.to_dict() for s in self.state_event_subtree],
            'journey_tree': [j.to_dict() for j in self.journey_tree],
            'journey_subtree': [j.to_dict() for j in self.journey_subtree]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeMap':
        return cls(
            id=data.get('id'),
            lb=data.get('lb'),
            creation_date_time=datetime.fromisoformat(data['creation_date_time']) if isinstance(data.get('creation_date_time'), str) else data.get('creation_date_time'),
            modification_date_time=datetime.fromisoformat(data['modification_date_time']) if isinstance(data.get('modification_date_time'), str) else data.get('modification_date_time'),
            time_ref=[Time_ref.from_dict(t) for t in data.get('time_ref', [])],
            space_ref=[Space_ref.from_dict(s) for s in data.get('space_ref', [])],
            agent=[Agent.from_dict(a) for a in data.get('agent', [])],
            state=[State.from_dict(s) for s in data.get('state', [])],
            event=[Event.from_dict(e) for e in data.get('event', [])],
            journey=[Journey.from_dict(j) for j in data.get('journey', [])],
            chapter=[Chapter.from_dict(c) for c in data.get('chapter', [])],
            agent_rel_hist=[Agent_rel_hist.from_dict(a) for a in data.get('agent_rel_hist', [])],
            agent_state_rel=[Agent_state_rel.from_dict(a) for a in data.get('agent_state_rel', [])],
            agent_event_rel=[Agent_event_rel.from_dict(a) for a in data.get('agent_event_rel', [])],
            state_event_rel=[State_event_rel.from_dict(s) for s in data.get('state_event_rel', [])],
            event_state_rel=[Event_state_rel.from_dict(e) for e in data.get('event_state_rel', [])],
            state_event_tree=[State_event_tree.from_dict(s) for s in data.get('state_event_tree', [])],
            state_event_subtree=[State_event_subtree.from_dict(s) for s in data.get('state_event_subtree', [])],
            journey_tree=[Journey_tree.from_dict(j) for j in data.get('journey_tree', [])],
            journey_subtree=[Journey_subtree.from_dict(j) for j in data.get('journey_subtree', [])]
        )

    def get_next_id(self, entity_type: str) -> int:
        """Get the next available ID for a given entity type."""
        existing_ids = set()
        
        if entity_type == 'time_ref':
            existing_ids = {e.id for e in self.time_ref}
        elif entity_type == 'space_ref':
            existing_ids = {s.id for s in self.space_ref}
        elif entity_type == 'agent':
            existing_ids = {a.id for a in self.agent}
        elif entity_type == 'state':
            existing_ids = {s.id for s in self.state}
        elif entity_type == 'event':
            existing_ids = {e.id for e in self.event}
        elif entity_type == 'journey':
            existing_ids = {j.id for j in self.journey}
        elif entity_type == 'chapter':
            existing_ids = {c.id for c in self.chapter}
        elif entity_type == 'agent_rel_hist':
            existing_ids = {a.id for a in self.agent_rel_hist}
        elif entity_type == 'agent_state_rel':
            existing_ids = {a.id for a in self.agent_state_rel}
        elif entity_type == 'agent_event_rel':
            existing_ids = {a.id for a in self.agent_event_rel}
        elif entity_type == 'state_event_rel':
            existing_ids = {s.id for s in self.state_event_rel}
        elif entity_type == 'event_state_rel':
            existing_ids = {e.id for e in self.event_state_rel}
        elif entity_type == 'state_event_tree':
            existing_ids = {s.id for s in self.state_event_tree}
        elif entity_type == 'state_event_subtree':
            existing_ids = {s.id for s in self.state_event_subtree}
        elif entity_type == 'journey_tree':
            existing_ids = {j.id for j in self.journey_tree}
        elif entity_type == 'journey_subtree':
            existing_ids = {j.id for j in self.journey_subtree}
        
        if existing_ids:
            return max(existing_ids) + 1
        return 1


# ---------------------------------------------------------------------
# Project Container
# ---------------------------------------------------------------------
@dataclass
class Project(BaseEntity):
    """
    Project
    Contains only id, lb, timestamps, and a list of narrative maps.
    """
    id: str
    lb: str
    file_path: Optional[str] = None
    narrative_map: List[NarrativeMap] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lb': self.lb,
            'file_path': self.file_path,
            'creation_date_time': self.creation_date_time.isoformat(),
            'modification_date_time': self.modification_date_time.isoformat() if self.modification_date_time else None,
            'narrative_map': [nm.to_dict() for nm in self.narrative_map]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(
            id=data.get('id'),
            lb=data.get('lb'),
            file_path=data.get('file_path'),
            creation_date_time=datetime.fromisoformat(data['creation_date_time']) if isinstance(data.get('creation_date_time'), str) else data.get('creation_date_time'),
            modification_date_time=datetime.fromisoformat(data['modification_date_time']) if isinstance(data.get('modification_date_time'), str) else data.get('modification_date_time'),
            narrative_map=[NarrativeMap.from_dict(nm) for nm in data.get('narrative_map', [])]
        )
