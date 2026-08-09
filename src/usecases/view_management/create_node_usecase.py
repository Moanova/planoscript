# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_node_usecase.py
# Version      : 1
# Date         : 23-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case pour la création de nœuds dans l'espace de travail.

Ce use case gère la création des entités métiers et de leurs layouts visuels,
mais NE gère PAS la création des objets graphiques Qt (QGraphicsItem).

Responsabilités :
- Créer une entité métier (Agent, State, Event, etc.) avec un ID unique
- Ajouter l'entité à la NarrativeMap du projet
- Créer un NodeLayout pour la représentation visuelle
- Retourner toutes les données nécessaires pour créer le nœud visuel

Séparation des responsabilités :
- Ce use case : logique métier et données
- JourneyWorkspace : création et affichage des QGraphicsItem
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from core.models.data_model import (
    Agent, State, Event, Time_ref, Space_ref, NarrativeMap
)
from core.models.view_model import NodeLayout, NodeType
from core.services.project_service import ProjectService
from core.services.layout_service import LayoutService


class CreateNodeUseCase:
    """
    Use Case pour créer un nouveau nœud dans la carte narrative.
    
    Ce use case coordonne la création de l'entité métier, son ajout au projet,
    et la préparation des données nécessaires pour l'affichage.
    
    Attributes:
        project_service: Service de gestion du projet courant
    """

    COMPONENT_MAPPING = {
        "Référence temporelle": {
            'entity_class': Time_ref,
            'node_type': NodeType.TIME_REF,
            'entity_type_key': 'time_ref',
            'default_label': 'Réf. temporelle'
        },
        "Référence spatiale": {
            'entity_class': Space_ref,
            'node_type': NodeType.SPACE_REF,
            'entity_type_key': 'space_ref',
            'default_label': 'Réf. spatiale'
        },
        "Agent": {
            'entity_class': Agent,
            'node_type': NodeType.AGENT,
            'entity_type_key': 'agent',
            'default_label': 'Agent'
        },
        "État": {
            'entity_class': State,
            'node_type': NodeType.STATE,
            'entity_type_key': 'state',
            'default_label': 'État'
        },
        "Évènement": {
            'entity_class': Event,
            'node_type': NodeType.EVENT,
            'entity_type_key': 'event',
            'default_label': 'Évènement'
        },
    }

    def __init__(self, project_service: ProjectService):
        """
        Initialise le use case avec le service de projet.
        
        Args:
            project_service: Service gérant le projet courant
        """
        self.project_service = project_service

    def execute(
        self,
        component_type: str,
        x: float,
        y: float,
        narrative_map: Optional[NarrativeMap] = None
    ) -> Optional[Dict]:
        """
        Exécute la création d'un nœud du type spécifié.
        
        Args:
            component_type: Type de composant à créer (ex: "Agent", "État", etc.)
            x: Coordonnée X pour le positionnement du nœud
            y: Coordonnée Y pour le positionnement du nœud
            narrative_map: NarrativeMap cible (optionnel, utilise la première par défaut)
            
        Returns:
            Dictionnaire contenant :
                - 'success': bool (True si création réussie)
                - 'entity': l'entité métier créée (Agent, State, etc.)
                - 'entity_id': ID de l'entité
                - 'layout': NodeLayout pour la représentation visuelle
                - 'node_type': NodeType enum pour savoir quel type de nœud créer
                - 'narrative_map_id': ID de la carte narrative
                - 'component_type': Type de composant
            
            Ou None si échec (type inconnu, pas de projet, etc.)
        """
        # 1. Vérifier qu'un projet est ouvert
        if not self.project_service or not self.project_service.current_project:
            print("CreateNodeUseCase: Aucun projet ouvert")
            return None
        
        project = self.project_service.current_project
        
        # 2. Utiliser la NarrativeMap fournie, ou la première par défaut
        if narrative_map is None:
            if not project or not project.narrative_map:
                return None
            narrative_map = project.narrative_map[0]
        
        # 3. Vérifier que le type de composant est valide
        if component_type not in self.COMPONENT_MAPPING:
            print(f"CreateNodeUseCase: Type de composant inconnu: {component_type}")
            return None
        
        component_config = self.COMPONENT_MAPPING[component_type]
        entity_class = component_config['entity_class']
        node_type = component_config['node_type']
        entity_type_key = component_config['entity_type_key']
        default_label = component_config['default_label']
        
        # 4. Générer un ID unique via la NarrativeMap (BONNE PRATIQUE)
        entity_id = narrative_map.get_next_id(entity_type_key)
        
        # 5. Créer l'entité métier avec des valeurs par défaut
        entity = self._create_entity(entity_class, entity_id, default_label)
        
        # 6. Ajouter l'entité à la NarrativeMap
        self._add_entity_to_narrative_map(narrative_map, entity, entity_type_key)
        
        # 7. Créer le NodeLayout via LayoutService
        layout = LayoutService.create_node_layout(
            node_id=entity_id,
            node_type=node_type.value,
            x=x,
            y=y
        )
        
        # 8. Marquer le projet comme modifié
        self.project_service.set_modified(True)
        
        # 9. Retourner toutes les données nécessaires pour créer le nœud visuel
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity_id,
            'layout': layout,
            'node_type': node_type,
            'narrative_map_id': narrative_map.id,
            'component_type': component_type
        }

    def _create_entity(self, entity_class, entity_id: int, default_label: str):
        """
        Crée une entité métier avec des valeurs par défaut.
        
        Args:
            entity_class: Classe de l'entité (Agent, State, etc.)
            entity_id: ID unique pour l'entité
            default_label: Libellé par défaut
            
        Returns:
            Instance de l'entité créée
        """
        # Créer avec les attributs de base + champs obligatoires spécifiques
        if entity_class == Agent:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None,
                typ="Sujet"  # Champ obligatoire (même s'il a une valeur par défaut dans le modèle)
            )
        elif entity_class == State:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None,
                space_ref_id=None,  # Champ obligatoire pour State
                time_ref_id=0
            )
        elif entity_class == Event:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None,
                space_ref_id=None,  # Champ obligatoire pour Event
                time_ref_id=0
            )
        elif entity_class == Time_ref:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None,
                prev_id=0  # Champ obligatoire pour Time_ref
            )
        elif entity_class == Space_ref:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None
            )
        else:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                creation_date_time=datetime.now(),
                modification_date_time=None
            )
        
        return entity

    def _add_entity_to_narrative_map(
        self,
        narrative_map: NarrativeMap,
        entity,
        entity_type_key: str
    ) -> None:
        """
        Ajoute une entité à la NarrativeMap selon son type.
        
        Args:
            narrative_map: La carte narrative à mettre à jour
            entity: L'entité à ajouter
            entity_type_key: Clé du type d'entité ('agent', 'state', etc.)
        """
        # Mapping des clés vers les noms d'attributs de NarrativeMap
        attr_mapping = {
            'time_ref': 'time_ref',
            'space_ref': 'space_ref',
            'agent': 'agent',
            'state': 'state',
            'event': 'event'
        }
        
        attr_name = attr_mapping.get(entity_type_key)
        if attr_name and hasattr(narrative_map, attr_name):
            entity_list = getattr(narrative_map, attr_name)
            entity_list.append(entity)
