# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : data_model.py
# Version      : 2
# Date         : 26-08-2026
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
class Agent:
    """
    Agent
    Represents an agent, person or object, of the narrative map.
    """
    id: int
    lb: str
    typ: str = "Subject"  # Type of agent ("Subject" or "Object")
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if self.typ not in ["Subject", "Object"]:
            raise ValueError(f"Invalid Agent.typ: {self.typ}. Must be 'Subject' or 'Object'")
        if not isinstance(self.typ, str):
            self.typ = str(self.typ)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class State:
    """
    State
    Represents a status of the narrative map, linked to an agent or not, linked to an event or not.
    """
    id: int
    lb: str
    typ: str = "Action"  # Type of state ("Initial", "Action", "Relation", "Final")
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if self.typ not in ["Initial", "Action", "Relation", "Final"]:
            raise ValueError(f"Invalid State.typ: {self.typ}. Must be one of: 'Initial', 'Action', 'Relation', 'Final'")
        if not isinstance(self.typ, str):
            self.typ = str(self.typ)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Event:
    """
    Event
    Represents an event of the narrative map.
    """
    id: int
    lb: str
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Journey:
    """
    Journey
    Represents a sequence of states and events (subset of the State-to-event tree).
    """
    id: int
    lb: str
    default: bool = False  # Default journey indicator
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.id, int):
            self.id = int(self.id)
        if not isinstance(self.default, bool):
            self.default = bool(self.default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Journey':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------
# Relation Classes
# ---------------------------------------------------------------------
@dataclass
class State_agent_rel:
    """
    Relation between a state and an agent.
    """
    id: int
    state_id: int
    agent_id: int
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        for attr in ['id', 'state_id', 'agent_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State_agent_rel':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class State_node:
    """
    Node of state-to-event-to-state relations.
    Represents connections between events through states.
    """
    id: int
    from_event_id: int  # Predecessor event ID (0 = no predecessor)
    state_id: int  # State ID of the node (0 = placeholder without state)
    to_event_id: int  # Successor event ID
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        for attr in ['id', 'from_event_id', 'state_id', 'to_event_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State_node':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Journey_node:
    """
    Node of journey.
    Links state nodes to journeys.
    """
    id: int
    state_node_id: int  # Reference to State_node.id
    journey_id: int  # Reference to Journey.id
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    
    def __post_init__(self):
        for attr in ['id', 'state_node_id', 'journey_id']:
            if not isinstance(getattr(self, attr), int):
                setattr(self, attr, int(getattr(self, attr)))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        result = asdict(self)
        if isinstance(result.get('creation_date_time'), datetime):
            result['creation_date_time'] = result['creation_date_time'].isoformat()
        if isinstance(result.get('modification_date_time'), datetime):
            result['modification_date_time'] = result['modification_date_time'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Journey_node':
        """Create entity from dictionary."""
        if 'creation_date_time' in data and isinstance(data['creation_date_time'], str):
            data['creation_date_time'] = datetime.fromisoformat(data['creation_date_time'])
        if 'modification_date_time' in data and isinstance(data['modification_date_time'], str):
            data['modification_date_time'] = datetime.fromisoformat(data['modification_date_time'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------
# Narrative Map Container
# ---------------------------------------------------------------------
@dataclass
class NarrativeMap:
    """
    Narrative Map
    Container for all narrative map content (entities and relations).
    """
    id: str  # UUID
    lb: str
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    # Entities
    state: List[State] = field(default_factory=list)
    event: List[Event] = field(default_factory=list)
    journey: List[Journey] = field(default_factory=list)

    # Relations
    state_agent_rel: List[State_agent_rel] = field(default_factory=list)
    state_node: List[State_node] = field(default_factory=list)
    journey_node: List[Journey_node] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lb': self.lb,
            'creation_date_time': self.creation_date_time.isoformat(),
            'modification_date_time': self.modification_date_time.isoformat() if self.modification_date_time else None,
            'state': [s.to_dict() for s in self.state],
            'event': [e.to_dict() for e in self.event],
            'journey': [j.to_dict() for j in self.journey],
            'state_agent_rel': [r.to_dict() for r in self.state_agent_rel],
            'state_node': [n.to_dict() for n in self.state_node],
            'journey_node': [n.to_dict() for n in self.journey_node]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeMap':
        return cls(
            id=data.get('id'),
            lb=data.get('lb'),
            creation_date_time=datetime.fromisoformat(data['creation_date_time']) if isinstance(data.get('creation_date_time'), str) else data.get('creation_date_time'),
            modification_date_time=datetime.fromisoformat(data['modification_date_time']) if isinstance(data.get('modification_date_time'), str) else data.get('modification_date_time'),
            state=[State.from_dict(s) for s in data.get('state', [])],
            event=[Event.from_dict(e) for e in data.get('event', [])],
            journey=[Journey.from_dict(j) for j in data.get('journey', [])],
            state_agent_rel=[State_agent_rel.from_dict(r) for r in data.get('state_agent_rel', [])],
            state_node=[State_node.from_dict(n) for n in data.get('state_node', [])],
            journey_node=[Journey_node.from_dict(n) for n in data.get('journey_node', [])]
        )

    def get_next_id(self, entity_type: str) -> int:
        """Get the next available ID for a given entity type."""
        existing_ids = set()
        
        if entity_type == 'state':
            existing_ids = {s.id for s in self.state}
        elif entity_type == 'event':
            existing_ids = {e.id for e in self.event}
        elif entity_type == 'journey':
            existing_ids = {j.id for j in self.journey}
        elif entity_type == 'state_agent_rel':
            existing_ids = {r.id for r in self.state_agent_rel}
        elif entity_type == 'state_node':
            existing_ids = {n.id for n in self.state_node}
        elif entity_type == 'journey_node':
            existing_ids = {n.id for n in self.journey_node}
        
        if existing_ids:
            return max(existing_ids) + 1
        return 1


# ---------------------------------------------------------------------
# Project Container
# ---------------------------------------------------------------------
@dataclass
class Project:
    """
    Project
    Contains id, lb, timestamps, a list of agents, and a list of narrative maps.
    """
    id: str
    lb: str
    file_path: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    agent: List[Agent] = field(default_factory=list)
    narrative_map: List[NarrativeMap] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lb': self.lb,
            'file_path': self.file_path,
            'creation_date_time': self.creation_date_time.isoformat(),
            'modification_date_time': self.modification_date_time.isoformat() if self.modification_date_time else None,
            'agent': [a.to_dict() for a in self.agent],
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
            agent=[Agent.from_dict(a) for a in data.get('agent', [])],
            narrative_map=[NarrativeMap.from_dict(nm) for nm in data.get('narrative_map', [])]
        )

    def get_next_id(self, entity_type: str) -> int:
        """Get the next available ID for a given entity type at project level."""
        existing_ids = set()
        
        if entity_type == 'agent':
            existing_ids = {a.id for a in self.agent}
        
        if existing_ids:
            return max(existing_ids) + 1
        return 1
