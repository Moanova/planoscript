# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_workspace.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QFrame,
    QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon
import os

from ui.nodes.agent_node import AgentNode
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode
from ui.nodes.time_ref_node import TimeRefNode
from ui.nodes.space_ref_node import SpaceRefNode
from core.models.view_model import NodeType

class JourneyWorkspace(QGraphicsView):
    """Central workspace with dynamic grid resizing and scrollbar management"""
    
    def __init__(self, initial_width=2000, initial_height=1600, narrative_map=None):
        super().__init__()

        self.narrative_map = narrative_map

        self.initial_width = initial_width
        self.initial_height = initial_height
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setStyleSheet("""
            /* Barres de défilement */
            QScrollBar:horizontal {
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                margin: 0px;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                margin: 0px;
                border: none;
            }

            /* Poignée (slider) */
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
                min-width: 20px;
            } 
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }

            /* Boutons +/- (flèches de défilement) */
            QScrollBar::add-line, QScrollBar::sub-line {
                background: #e0e0e0;
                border: none;
                border-radius: 4px;
                height: 4px;  /* Hauteur pour les barres verticales */
                width: 4px;   /* Largeur pour les barres horizontales */
            }

            /* Flèches pour les boutons */
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 4px;
                height: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height:4px;
                width: 4px;
            }

            /* Positionnement des flèches */
            QScrollBar::sub-line:horizontal {
                subcontrol-position: left;
            }
            QScrollBar::add-line:horizontal {
                subcontrol-position: right;
            }
            QScrollBar::sub-line:vertical {
                subcontrol-position: top;
            }
            QScrollBar::add-line:vertical {
                subcontrol-position: bottom;
            }

            /* Style des flèches (icônes) */
            QScrollBar::add-line, QScrollBar::sub-line {
                background: #e0e0e0;
            }
            QScrollBar::add-line:hover, QScrollBar::sub-line:hover {
                background: #d0d0d0;
            }
            QScrollBar::add-line:pressed, QScrollBar::sub-line:pressed {
                background: #b0b0b0;
            }
        """)


        # Initial scene size (fixed at startup)
        self.setSceneRect(0, 0, initial_width, initial_height)
        self._draw_grid()

        # Disable scrollbars initially
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Enable drag-and-drop for items
        self.setAcceptDrops(True)
        # RG009: Désactiver RubberBandDrag pour éviter la sélection multiple
        self.setDragMode(QGraphicsView.NoDrag)

        # Track scene boundaries
        self.min_scene_size = QSizeF(800, 600)  # Minimum size to avoid shrinking
        self._update_scrollbars()

        # Style
        self.setRenderHint(QPainter.Antialiasing)


    def _draw_grid(self):
        """Draw grid lines based on current scene size"""
        self.scene.clear()  # Clear existing grid
        grid_size = 20
        subgrid_size = 80
        scene_rect = self.sceneRect()
        width = int(scene_rect.width())
        height = int(scene_rect.height())

        # Main grid (20px)
        pen_main = QPen(QColor("#e0e0e0"))
        pen_main.setWidth(1)
        for x in range(0, width + grid_size, grid_size):
            self.scene.addLine(x, 0, x, height, pen_main)
        for y in range(0, height + grid_size, grid_size):
            self.scene.addLine(0, y, width, y, pen_main)

        # Subgrid (80px)
        pen_sub = QPen(QColor("#808080"))
        pen_sub.setWidth(1)
        for x in range(0, width + subgrid_size, subgrid_size):
            self.scene.addLine(x, 0, x, height, pen_sub)
        for y in range(0, height + subgrid_size, subgrid_size):
            self.scene.addLine(0, y, width, y, pen_sub)


    def _update_scrollbars(self):
        """Toggle scrollbars based on scene vs viewport size"""
        viewport_width = self.viewport().width()
        viewport_height = self.viewport().height()
        scene_width = self.sceneRect().width()
        scene_height = self.sceneRect().height()

        # Enable scrollbars only if scene is larger than viewport
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if scene_width > viewport_width else Qt.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded if scene_height > viewport_height else Qt.ScrollBarAlwaysOff
        )


    def resizeEvent(self, event):
        """Handle window resize: redraw grid if needed"""
        super().resizeEvent(event)
        self._update_scrollbars()


    def ensure_visible(self, x: float, y: float, margin: int = 200):
        """
        RG011: Extend scene to include (x, y) and all selectable items near the edges.
        `margin` = extra space around the new bounds.
        """
        scene_rect = self.sceneRect()
        new_rect = scene_rect

        # 1. Check if (x, y) is outside current bounds + margin
        if x < new_rect.left() - margin:
            new_left = x - margin
            new_rect.setLeft(new_left)
        elif x > new_rect.right() + margin:
            new_right = x + margin
            new_rect.setRight(new_right)

        if y < new_rect.top() - margin:
            new_top = y - margin
            new_rect.setTop(new_top)
        elif y > new_rect.bottom() + margin:
            new_bottom = y + margin
            new_rect.setBottom(new_bottom)

        # 2. RG011: Vérifier aussi les composants sélectables près des bords
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item_rect = item.sceneBoundingRect()
                # Étendre si le composant dépasse les limites actuelles + marge
                if item_rect.left() < new_rect.left() - margin:
                    new_rect.setLeft(item_rect.left() - margin)
                if item_rect.right() > new_rect.right() + margin:
                    new_rect.setRight(item_rect.right() + margin)
                if item_rect.top() < new_rect.top() - margin:
                    new_rect.setTop(item_rect.top() - margin)
                if item_rect.bottom() > new_rect.bottom() + margin:
                    new_rect.setBottom(item_rect.bottom() + margin)

        # Apply new bounds if changed
        if new_rect != scene_rect:
            # Ensure minimum size
            new_width = max(new_rect.width(), self.min_scene_size.width())
            new_height = max(new_rect.height(), self.min_scene_size.height())
            new_rect = QRectF(
                new_rect.left(),
                new_rect.top(),
                new_width,
                new_height
            )
            self.setSceneRect(new_rect)
            self._draw_grid()  # Redraw grid for new size
            self._update_scrollbars()  # RG012: Update scrollbar visibility

        # Center view on the new position if it was outside
        if not scene_rect.contains(x, y):
            self.centerOn(x, y)


    def add_item_at(self, x: float, y: float, item: QGraphicsItem):
        """Add an item to the scene and extend scene if needed"""
        self.scene.addItem(item)
        item.setPos(x, y)
        self.ensure_visible(x, y)


    def mouseMoveEvent(self, event):
        # 1. Laisser Qt traiter le déplacement du nœud D'ABORD
        super().mouseMoveEvent(event)

        # 2. Auto-scrolling (RG012) + contrainte (RG011)
        if event.buttons() == Qt.LeftButton:
            # Auto-scrolling si la souris est près des bords du viewport
            viewport_rect = self.viewport().rect()
            mouse_viewport_pos = event.position().toPoint()
            scroll_margin = 50
            scroll_speed = 20

            # Vérifier les bords
            near_left = mouse_viewport_pos.x() < scroll_margin
            near_right = mouse_viewport_pos.x() > viewport_rect.width() - scroll_margin
            near_top = mouse_viewport_pos.y() < scroll_margin
            near_bottom = mouse_viewport_pos.y() > viewport_rect.height() - scroll_margin

            # Défilement automatique
            if near_left:
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - scroll_speed
                )
            elif near_right:
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() + scroll_speed
                )

            if near_top:
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - scroll_speed
                )
            elif near_bottom:
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() + scroll_speed
                )

            # Mettre à jour les scrollbars
            self._update_scrollbars()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.ensure_visible(scene_pos.x(), scene_pos.y())
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        """
        RG009: Gère la sélection unique des composants et connexions.
        - Si clic sur un item sélectable (nœud ou connexion) → le sélectionner et désélectionner tous les autres
        - Si clic sur l'espace vide → désélectionner tout
        """
        # Récupérer l'item sous le curseur
        item = self.itemAt(event.position().toPoint())
        
        # Appeler la méthode parente d'abord pour que Qt gère le clic normalement
        super().mousePressEvent(event)
        
        # Ensuite appliquer notre logique RG009
        if event.button() == Qt.LeftButton:
            if item is None:
                # Clic sur espace vide : désélectionner tout
                self._clear_all_selections()
            elif item.isEnabled() and item.isVisible():
                # Vérifier si c'est un item sélectable (nœud ou connexion)
                if item.flags() & QGraphicsItem.ItemIsSelectable:
                    # RG009: Sélectionner uniquement cet item
                    self._select_item_only(item)


    def create_node_from_data(self, node_data: dict):
        """
        Crée un nœud visuel à partir des données retournées par le use case.
        
        Args:
            node_data: Dictionnaire contenant :
                - 'entity': l'entité métier
                - 'layout': NodeLayout
                - 'node_type': NodeType
                - 'component_type': str (optionnel)
        """
        entity = node_data['entity']
        layout = node_data['layout']
        node_type = node_data['node_type']

        # Mapping NodeType -> Classe de nœud visuel
        NODE_CLASS_MAPPING = {
            NodeType.AGENT: AgentNode,
            NodeType.STATE: StateNode,
            NodeType.EVENT: EventNode,
            NodeType.TIME_REF: TimeRefNode,
            NodeType.SPACE_REF: SpaceRefNode,
        }

        node_class = NODE_CLASS_MAPPING.get(node_type)
        if not node_class:
            print(f"Type de nœud inconnu: {node_type}")
            return None

        # Créer le nœud visuel
        node = node_class(entity, layout)

        # Ajouter à la scène
        self.add_item_at(layout.x, layout.y, node)
        
        # RG009: Sélectionner le nouveau nœud et désélectionner les autres
        self._select_item_only(node)

        return node

    def create_connection_from_data(self, connection_data: dict):
        """
        Crée une connexion visuelle à partir des données retournées par le use case.
    
        Args:
            connection_data: Dictionnaire contenant :
                - 'connection_layout': ConnectionLayout
                - 'source_entity': entité source
                - 'target_entity': entité cible
        """
        from ui.nodes.connection import Connection  # À vérifier si cette classe existe
        from PySide6.QtCore import QPointF

        connection_layout = connection_data['connection_layout']
        source_entity = connection_data['source_entity']
        target_entity = connection_data['target_entity']

        # Trouver les nœuds visuels correspondants dans la scène
        source_node = self._find_node_by_entity_id(source_entity.id)
        target_node = self._find_node_by_entity_id(target_entity.id)

        if not source_node or not target_node:
            print("Nœud source ou cible non trouvé")
            return None

        # Créer la connexion visuelle
        connection = Connection(connection_layout)

        # Positionner la connexion (à adapter selon votre implémentation)
        self.scene.addItem(connection)
        connection.update_path(source_node, target_node)
        
        # RG009: Sélectionner la nouvelle connexion et désélectionner les autres
        self._select_item_only(connection)

        return connection


    def _find_node_by_entity_id(self, entity_id: int):
        """Trouve un nœud dans la scène par son entity_id."""
        for item in self.scene.items():
            if hasattr(item, 'entity') and item.entity.id == entity_id:
                return item
        return None

    def _select_item_only(self, item):
        """
        RG009: Sélectionne uniquement l'item spécifié et désélectionne tous les autres.
        
        Args:
            item: Le QGraphicsItem à sélectionner
        """
        # Désélectionner tous les items sélectables
        for existing_item in self.scene.items():
            if (existing_item != item and 
                existing_item.flags() & QGraphicsItem.ItemIsSelectable and
                existing_item.isEnabled()):
                existing_item.setSelected(False)
        
        # Sélectionner l'item spécifié
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)

    def _clear_all_selections(self):
        """
        RG009: Désélectionne tous les items sélectables dans la scène.
        """
        for item in self.scene.items():
            if (item.flags() & QGraphicsItem.ItemIsSelectable and 
                item.isEnabled()):
                item.setSelected(False)
