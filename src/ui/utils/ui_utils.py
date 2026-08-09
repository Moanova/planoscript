# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : ui_utils.py
# Version      : 1
# Date         : 13-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer

def create_colored_icon(svg_path, color_hex="#000000"):
    """
    Charge un SVG et applique une couleur de remplissage.

    Objectif: éviter le problème de transmission de la couleur du widget au fichier SVG.

    Args:
        svg_path (str): Chemin vers le fichier SVG
        color_hex (str): Couleur au format hex (#RRGGBB)

    Returns:
        QIcon: Icône colorée
    """
    renderer = QSvgRenderer(svg_path)
    size = renderer.defaultSize()

    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)

    # Rend le SVG
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    # Applique la couleur
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color_hex))
    painter.end()

    return QIcon(pixmap)
