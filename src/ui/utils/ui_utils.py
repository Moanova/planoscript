# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : ui_utils.py
# Version      : 1
# Date         : 13-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer

def create_colored_icon(svg_path, color_hex="#000000"):
    """
    Loads an SVG and applies a fill color. 

    Objective: Avoid the issue of passing the widget's color to the SVG file. 

    Args:
        svg_path (str): Path to the SVG file
        color_hex (str): Color in hex format (#RRGGBB)

    Returns:
        QIcon: Colored icon
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
