# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_relation_usecase.py
# Version      : 1
# Date         : 23-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case pour la création de relations entre nœuds dans l'espace de travail.

Ce use case gère la création des entités de relation (Agent_rel_hist, Agent_state_rel, etc.)
et de leurs layouts visuels (ConnectionLayout), mais NE gère PAS la création des objets
graphiques Qt (QGraphicsLineItem).

Responsabilités :
- Créer une entité de relation avec des IDs uniques
- Ajouter l'entité de relation à la NarrativeMap du projet
- Créer un ConnectionLayout pour la représentation visuelle
- Retourner toutes les données nécessaires pour créer la connexion visuelle

Séparation des responsabilités :
- Ce use case : logique métier et données
- JourneyWorkspace : création et affichage des QGraphicsLineItem
"""

from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from uuid import uuid4

from core.models.data_model import (
    Agent_rel_hist,
    Agent_state_rel,
    Agent_event_rel,
    State_event_rel,
    Event_state_rel,
    NarrativeMap
)
from core.models.view_model import ConnectionLayout, NodeType
from core.services.project_service import ProjectService
from core.services.layout_service import LayoutService


class CreateRelationUseCase:
    """
    Use Case pour créer une nouvelle relation entre deux nœuds dans la carte narrative.
    
    Ce use case coordonne la création de l'entité de relation, son ajout au projet,
    et la préparation des données nécessaires pour l'affichage de la connexion.
    
    Attributes:
        project_service: Service de gestion du projet courant
    """

    # Mapping des types de relation (noms français de l'UI) vers les classes d'entités
    RELATION_MAPPING = {
        "Agent à agent": {
            'entity_class': Agent_rel_hist,
            'relation_type_key': 'agent_rel_hist',
            'source_id_attr': 'agent_1_id',
            'target_id_attr': 'agent_2_id'
        },
        "Agent à état": {
            'entity_class': Agent_state_rel,
            'relation_type_key': 'agent_state_rel',
            'source_id_attr': 'agent_id',
            'target_id_attr': 'state_id'
        },
        "Agent à évènement": {
            'entity_class': Agent_event_rel,
            'relation_type_key': 'agent_event_rel',
            'source_id_attr': 'agent_id',
            'target_id_attr': 'event_id'
        },
        "État à évènement": {
            'entity_class': State_event_rel,
            'relation_type_key': 'state_event_rel',
            'source_id_attr': 'state_id',
            'target_id_attr': 'event_id'
        },
        "Évènement à état": {
            'entity_class': Event_state_rel,
            'relation_type_key': 'event_state_rel',
            'source_id_attr': 'event_id',
            'target_id_attr': 'state_id'
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
        source_entity: Any,
        target_entity: Any,
        relation_type: str,
        narrative_map: Optional[NarrativeMap] = None
    ) -> Optional[Dict]:
        """
        Exécute la création d'une relation du type spécifié entre deux entités.
        
        Args:
            source_entity: Entité source (Agent, State, Event, etc.)
            target_entity: Entité cible (Agent, State, Event, etc.)
            relation_type: Type de relation (ex: "Agent à agent", "Agent à état", etc.)
            narrative_map: NarrativeMap cible (optionnel, utilise la première par défaut)
            
        Returns:
            Dictionnaire contenant :
                - 'success': bool (True si création réussie)
                - 'relation_entity': l'entité de relation créée
                - 'connection_layout': ConnectionLayout pour la représentation visuelle
                - 'relation_type': Type de relation
                - 'narrative_map_id': ID de la carte narrative
                
            Ou None si échec (type inconnu, pas de projet, etc.)
        """
        # 1. Vérifier qu'un projet est ouvert
        if not self.project_service or not self.project_service.current_project:
            print("CreateRelationUseCase: Aucun projet ouvert")
            return None
        
        project = self.project_service.current_project
        
        # 2. Utiliser la NarrativeMap fournie, ou la première par défaut
        if narrative_map is None:
            if not project or not project.narrative_map:
                return None
            narrative_map = project.narrative_map[0]
        
        # 3. Vérifier que le type de relation est valide
        if relation_type not in self.RELATION_MAPPING:
            print(f"CreateRelationUseCase: Type de relation inconnu: {relation_type}")
            return None
        
        relation_config = self.RELATION_MAPPING[relation_type]
        relation_class = relation_config['entity_class']
        relation_type_key = relation_config['relation_type_key']
        source_id_attr = relation_config['source_id_attr']
        target_id_attr = relation_config['target_id_attr']
        
        # 4. Générer un ID unique via la NarrativeMap
        relation_id = narrative_map.get_next_id(relation_type_key)
        
        # 5. Créer l'entité de relation avec les IDs source et cible
        relation_entity = self._create_relation_entity(
            relation_class=relation_class,
            relation_id=relation_id,
            source_entity=source_entity,
            target_entity=target_entity,
            source_id_attr=source_id_attr,
            target_id_attr=target_id_attr
        )
        
        if relation_entity is None:
            return None
        
        # 6. Ajouter l'entité de relation à la NarrativeMap
        self._add_relation_to_narrative_map(narrative_map, relation_entity, relation_type_key)
        
        # 7. Créer le ConnectionLayout via LayoutService
        connection_layout = LayoutService.create_connection_layout(
            source_node_id=source_entity.id,
            target_node_id=target_entity.id
        )
        
        # 8. Marquer le projet comme modifié
        self.project_service.set_modified(True)
        
        # 9. Retourner toutes les données nécessaires pour créer la connexion visuelle
        return {
            'success': True,
            'relation_entity': relation_entity,
            'relation_id': relation_id,
            'connection_layout': connection_layout,
            'relation_type': relation_type,
            'source_entity': source_entity,
            'target_entity': target_entity,
            'narrative_map_id': narrative_map.id
        }

    def _create_relation_entity(
        self,
        relation_class,
        relation_id: int,
        source_entity: Any,
        target_entity: Any,
        source_id_attr: str,
        target_id_attr: str
    ) -> Any:
        """
        Crée une entité de relation avec les IDs source et cible.
        
        Args:
            relation_class: Classe de l'entité de relation
            relation_id: ID unique pour la relation
            source_entity: Entité source
            target_entity: Entité cible
            source_id_attr: Nom de l'attribut pour l'ID source
            target_id_attr: Nom de l'attribut pour l'ID cible
            
        Returns:
            Instance de l'entité de relation créée
        """
        # Créer un dictionnaire avec les attributs de base
        relation_data = {
            'id': relation_id,
            'creation_date_time': datetime.now(),
            'modification_date_time': None
        }
        
        # Ajouter les IDs source et cible
        relation_data[source_id_attr] = source_entity.id
        relation_data[target_id_attr] = target_entity.id
        
        # Ajouter les attributs spécifiques optionnels
        if relation_class == Agent_rel_hist:
            relation_data['time_ref_id'] = 0
            relation_data['state_id'] = None
        elif relation_class == Agent_state_rel:
            relation_data['note'] = None
        elif relation_class == Agent_event_rel:
            relation_data['note'] = None
        elif relation_class == State_event_rel:
            relation_data['note'] = None
        elif relation_class == Event_state_rel:
            relation_data['note'] = None
        
        # Créer et retourner l'entité
        return relation_class(**relation_data)

    def _add_relation_to_narrative_map(
        self,
        narrative_map: NarrativeMap,
        relation_entity,
        relation_type_key: str
    ) -> None:
        """
        Ajoute une entité de relation à la NarrativeMap selon son type.
        
        Args:
            narrative_map: La carte narrative à mettre à jour
            relation_entity: L'entité de relation à ajouter
            relation_type_key: Clé du type de relation
        """
        # Mapping des clés vers les noms d'attributs de NarrativeMap
        attr_mapping = {
            'agent_rel_hist': 'agent_rel_hist',
            'agent_state_rel': 'agent_state_rel',
            'agent_event_rel': 'agent_event_rel',
            'state_event_rel': 'state_event_rel',
            'event_state_rel': 'event_state_rel',
        }
        
        attr_name = attr_mapping.get(relation_type_key)
        if attr_name and hasattr(narrative_map, attr_name):
            relation_list = getattr(narrative_map, attr_name)
            relation_list.append(relation_entity)
