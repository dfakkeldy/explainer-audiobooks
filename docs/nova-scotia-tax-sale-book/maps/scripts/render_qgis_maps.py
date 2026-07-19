"""Build a QGIS 4 project and render orientation plus aerial detail proofs.

Run this file with the Python runtime bundled in a QGIS 4 application. The
script initializes QGIS, writes the project and image proofs, then exits.
"""

import os
from pathlib import Path

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter, QPen
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFillSymbol,
    QgsMapRendererParallelJob,
    QgsMapSettings,
    QgsPalLayerSettings,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsRendererCategory,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)


MAP_ROOT = Path(__file__).resolve().parents[1]
GEOJSON = MAP_ROOT / "working/inverness-tax-sale-parcels.geojson"
PROJECT_PATH = MAP_ROOT / "qgis/inverness-tax-sale-2026-08-11.qgz"
ORIENTATION_PATH = MAP_ROOT / "exports/inverness-all-properties-orientation.png"
DETAIL_PATH = MAP_ROOT / "exports/inverness-lien-01-aerial.png"

AERIAL_URL = (
    "https://nsgiwa.novascotia.ca/arcgis/rest/services/BASE/"
    "BASE_NSODB_10k_WM84/MapServer/tile/{z}/{y}/{x}"
)
ATTRIBUTION = (
    "Contains information obtained under license from the Province of Nova Scotia "
    "which is provided without warranty or liability for errors or omissions."
)


def styled_parcel_layer() -> QgsVectorLayer:
    layer = QgsVectorLayer(str(GEOJSON), "August 11, 2026 tax-sale parcels", "ogr")
    if not layer.isValid():
        raise RuntimeError(f"Could not open {GEOJSON}")

    categories = []
    for value, label, fill in (
        ("YES", "Redeemable", "30,177,255,100"),
        ("NO", "Non-redeemable", "255,171,64,115"),
    ):
        symbol = QgsFillSymbol.createSimple(
            {
                "color": fill,
                "outline_color": "255,255,255,255",
                "outline_width": "0.9",
            }
        )
        categories.append(QgsRendererCategory(value, symbol, label))
    layer.setRenderer(QgsCategorizedSymbolRenderer("redeemable", categories))

    text_format = QgsTextFormat()
    text_format.setFont(QFont("Helvetica Neue", 10, QFont.Weight.DemiBold))
    text_format.setSize(10)
    text_format.setColor(QColor("#ffffff"))
    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(1.4)
    buffer.setColor(QColor("#11131a"))
    text_format.setBuffer(buffer)
    labels = QgsPalLayerSettings()
    labels.enabled = True
    labels.fieldName = "'Lien ' || to_string(\"lien\")"
    labels.isExpression = True
    labels.placement = Qgis.LabelPlacement.Horizontal
    labels.setFormat(text_format)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(labels))
    layer.setLabelsEnabled(True)
    return layer


def aerial_layer() -> QgsRasterLayer:
    uri = (
        "type=xyz&url="
        + AERIAL_URL.replace("{", "%7B").replace("}", "%7D")
        + "&zmin=0&zmax=23&crs=EPSG3857"
    )
    layer = QgsRasterLayer(uri, "NS Aerial", "wms")
    if not layer.isValid():
        raise RuntimeError("NS Aerial XYZ layer did not load")
    layer.setOpacity(0.78)
    return layer


def transformed_extent(layer: QgsVectorLayer, project: QgsProject) -> QgsRectangle:
    transform = QgsCoordinateTransform(layer.crs(), project.crs(), project)
    return transform.transformBoundingBox(layer.extent())


def padded(rect: QgsRectangle, fraction: float) -> QgsRectangle:
    dx = rect.width() * fraction
    dy = rect.height() * fraction
    return QgsRectangle(
        rect.xMinimum() - dx,
        rect.yMinimum() - dy,
        rect.xMaximum() + dx,
        rect.yMaximum() + dy,
    )


def render_map(
    path: Path,
    layers,
    extent: QgsRectangle,
    title: str,
    subtitle: str,
    legend: bool,
) -> None:
    width, height = 2560, 1440
    header, footer = 150, 125
    settings = QgsMapSettings()
    settings.setLayers(layers)
    settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
    settings.setExtent(extent)
    settings.setOutputSize(QSize(width, height - header - footer))
    settings.setBackgroundColor(QColor("#12151d"))
    settings.setFlag(Qgis.MapSettingsFlag.Antialiasing, True)

    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    map_image = job.renderedImage()

    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor("#12151d"))
    painter = QPainter(image)
    painter.drawImage(0, header, map_image)

    painter.setPen(QColor("#f6f7fb"))
    painter.setFont(QFont("Helvetica Neue", 34, QFont.Weight.DemiBold))
    painter.drawText(58, 62, title)
    painter.setPen(QColor("#cbd2df"))
    painter.setFont(QFont("Helvetica Neue", 21))
    painter.drawText(60, 108, subtitle)

    if legend:
        legend_y = header + 34
        for color, text in (("#1eb1ff", "Redeemable"), ("#ffab40", "Non-redeemable")):
            painter.setBrush(QColor(color))
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawRect(width - 410, legend_y, 30, 30)
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Helvetica Neue", 18, QFont.Weight.DemiBold))
            painter.drawText(width - 365, legend_y + 24, text)
            legend_y += 48

    painter.setPen(QColor("#d6d9e2"))
    painter.setFont(QFont("Helvetica Neue", 16))
    painter.drawText(
        58,
        height - 76,
        "Dated municipal snapshot. Confirm the live list. Parcel graphics are not a survey or title opinion.",
    )
    painter.setFont(QFont("Helvetica Neue", 14))
    painter.drawText(58, height - 39, ATTRIBUTION)
    painter.end()

    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path), "PNG"):
        raise RuntimeError(f"Could not save {path}")


def run() -> None:
    project = QgsProject.instance()
    project.clear()
    project.setTitle("Inverness County tax-sale map proofs — August 11, 2026")
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

    aerial = aerial_layer()
    parcels = styled_parcel_layer()
    project.addMapLayer(aerial)
    project.addMapLayer(parcels)

    orientation_extent = padded(transformed_extent(parcels, project), 0.08)
    render_map(
        ORIENTATION_PATH,
        [parcels, aerial],
        orientation_extent,
        "Inverness County tax-sale properties",
        "August 11, 2026 public-auction snapshot · 45 liens · 47 PIDs",
        True,
    )

    detail = QgsVectorLayer(str(GEOJSON), "Lien 1 detail", "ogr")
    detail.setSubsetString('"lien" = 1')
    detail_symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,213,79,85",
            "outline_color": "255,255,255,255",
            "outline_width": "1.4",
        }
    )
    detail.renderer().setSymbol(detail_symbol)
    project.addMapLayer(detail)
    detail_extent = padded(transformed_extent(detail, project), 2.4)
    render_map(
        DETAIL_PATH,
        [detail, aerial],
        detail_extent,
        "Aerial and graphical parcel context — Lien 1",
        "PID 50203256 · Highway 19, Mabou · not a survey, access proof, appraisal, or recommendation",
        False,
    )

    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not project.write(str(PROJECT_PATH)):
        raise RuntimeError(f"Could not write {PROJECT_PATH}")

    print(f"PROJECT={PROJECT_PATH}")
    print(f"ORIENTATION={ORIENTATION_PATH}")
    print(f"DETAIL={DETAIL_PATH}")


if __name__ == "__main__":
    application = QgsApplication([], False)
    prefix_path = os.environ.get(
        "QGIS_PREFIX_PATH", "/Applications/QGIS-final-4_0_2.app"
    )
    QgsApplication.setPrefixPath(prefix_path, True)
    application.initQgis()
    try:
        run()
    finally:
        application.exitQgis()
