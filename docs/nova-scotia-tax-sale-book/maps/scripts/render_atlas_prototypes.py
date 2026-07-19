"""Render three owner-free Inverness Packet Atlas review cards with QGIS 4."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from pathlib import Path

from qgis.PyQt.QtCore import QRect, QSize, Qt
from qgis.PyQt.QtGui import QColor, QFont, QFontMetrics, QImage, QPainter, QPen
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFillSymbol,
    QgsGeometry,
    QgsMapRendererParallelJob,
    QgsMapSettings,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)

from render_qgis_maps import ATTRIBUTION, aerial_layer


MAP_ROOT = Path(__file__).resolve().parents[1]
GEOJSON = MAP_ROOT / "working/inverness-tax-sale-parcels.geojson"
AMO_ARCHIVE = MAP_ROOT / "working/dp010v9sgkx_NS_Abandoned_Mines.zip"
AMO_SHAPE_MEMBER = "dp010v9sgkx_NS_Abandoned_Mines/d010ns/shp/d010nssh/d010nssh.shp"
LISTING_DATA = MAP_ROOT / "data/inverness-tax-sale-2026-08-11.json"
ATLAS_ROOT = MAP_ROOT / "atlas-prototypes"
SPECS_PATH = ATLAS_ROOT / "atlas-prototype-specs.json"
RECEIPT_PATH = ATLAS_ROOT / "render-receipt.json"
CONTACT_SHEET_PATH = ATLAS_ROOT / "atlas-prototype-contact-sheet.png"
PHONE_SHEET_PATH = ATLAS_ROOT / "atlas-prototype-phone-contact-sheet.png"

WIDTH = 2560
HEIGHT = 1440
MAP_RECT = QRect(55, 205, 1460, 1060)
DESTINATION_CRS = QgsCoordinateReferenceSystem("EPSG:3857")
OPEN_DATA_ATTRIBUTION = (
    "Contains information licensed under the Open Government Licence – Nova Scotia."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_specs() -> dict[str, object]:
    payload = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    if payload.get("propertyOnlineUsed") is not False:
        raise RuntimeError("atlas prototypes must not use Property Online")
    if payload.get("assessedOwnerNamesIncluded") is not False:
        raise RuntimeError("atlas prototypes must exclude assessed-owner names")
    cards = payload.get("cards")
    if not isinstance(cards, list) or [card.get("lien") for card in cards] != [
        1,
        8,
        11,
    ]:
        raise RuntimeError("expected the approved Lien 1, 8, and 11 prototype set")
    return payload


def labelled_parcel_layer(lien: int) -> QgsVectorLayer:
    layer = QgsVectorLayer(str(GEOJSON), f"Atlas Lien {lien} parcels", "ogr")
    if not layer.isValid():
        raise RuntimeError(f"Could not open {GEOJSON}")
    layer.setSubsetString(f'"lien" = {lien}')
    layer.renderer().setSymbol(
        QgsFillSymbol.createSimple(
            {
                "color": "255,213,79,72",
                "outline_color": "255,255,255,255",
                "outline_width": "1.8",
            }
        )
    )

    text_format = QgsTextFormat()
    text_format.setFont(QFont("Helvetica Neue", 10, QFont.Weight.DemiBold))
    text_format.setSize(10)
    text_format.setColor(QColor("#ffffff"))
    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(1.6)
    buffer.setColor(QColor("#11131a"))
    text_format.setBuffer(buffer)
    labels = QgsPalLayerSettings()
    labels.enabled = True
    labels.fieldName = "'PID ' || \"pid\""
    labels.isExpression = True
    labels.placement = Qgis.LabelPlacement.Horizontal
    labels.setFormat(text_format)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(labels))
    layer.setLabelsEnabled(True)
    return layer


def abandoned_mine_layer(field: str, value: str) -> QgsVectorLayer:
    source = f"/vsizip/{AMO_ARCHIVE}/{AMO_SHAPE_MEMBER}"
    layer = QgsVectorLayer(source, "2024 recorded abandoned mine openings", "ogr")
    if not layer.isValid():
        raise RuntimeError(f"Could not open AMO archive at {AMO_ARCHIVE}")
    escaped = value.replace("'", "''")
    layer.setSubsetString(f"\"{field}\" = '{escaped}'")
    layer.renderer().setSymbol(
        QgsMarkerSymbol.createSimple(
            {
                "name": "diamond",
                "color": "230,57,70,255",
                "outline_color": "255,255,255,255",
                "outline_width": "1.2",
                "size": "7.5",
            }
        )
    )

    text_format = QgsTextFormat()
    text_format.setFont(QFont("Helvetica Neue", 9, QFont.Weight.DemiBold))
    text_format.setSize(9)
    text_format.setColor(QColor("#ffffff"))
    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(1.5)
    buffer.setColor(QColor("#4a1118"))
    text_format.setBuffer(buffer)
    labels = QgsPalLayerSettings()
    labels.enabled = True
    labels.fieldName = (
        "CASE WHEN \"ShaftID\" = 'BRB-1-001' THEN 'BRB-1-001 / 004' "
        "WHEN \"ShaftID\" = 'BRB-1-004' THEN '' ELSE \"ShaftID\" END"
    )
    labels.isExpression = True
    labels.placement = Qgis.LabelPlacement.AroundPoint
    labels.setFormat(text_format)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(labels))
    layer.setLabelsEnabled(True)
    return layer


def feature_extent(layer: QgsVectorLayer, project: QgsProject) -> QgsRectangle:
    transform = QgsCoordinateTransform(layer.crs(), DESTINATION_CRS, project)
    combined: QgsRectangle | None = None
    for feature in layer.getFeatures():
        geometry = QgsGeometry(feature.geometry())
        geometry.transform(transform)
        bounds = geometry.boundingBox()
        if combined is None:
            combined = QgsRectangle(bounds)
        else:
            combined.combineExtentWith(bounds)
    if combined is None:
        raise RuntimeError(f"Filtered layer has no features: {layer.name()}")
    return combined


def combined_extent(layers: list[QgsVectorLayer], project: QgsProject) -> QgsRectangle:
    result = feature_extent(layers[0], project)
    for layer in layers[1:]:
        result.combineExtentWith(feature_extent(layer, project))
    return result


def fit_extent(rectangle: QgsRectangle, minimum_width: float = 1600) -> QgsRectangle:
    aspect = MAP_RECT.width() / MAP_RECT.height()
    width = max(rectangle.width() * 1.18, minimum_width)
    height = max(rectangle.height() * 1.18, width / aspect)
    width = max(width, height * aspect)
    center = rectangle.center()
    return QgsRectangle(
        center.x() - width / 2,
        center.y() - height / 2,
        center.x() + width / 2,
        center.y() + height / 2,
    )


def nearest_distance_metres(
    parcels: QgsVectorLayer, points: QgsVectorLayer, project: QgsProject
) -> int:
    transform = QgsCoordinateTransform(parcels.crs(), points.crs(), project)
    parcel_geometries: list[QgsGeometry] = []
    for feature in parcels.getFeatures():
        geometry = QgsGeometry(feature.geometry())
        geometry.transform(transform)
        parcel_geometries.append(geometry)
    distances = [
        parcel.distance(point.geometry())
        for parcel in parcel_geometries
        for point in points.getFeatures()
    ]
    if not distances:
        raise RuntimeError("Could not calculate parcel-to-AMO distance")
    return round(min(distances))


def render_map_image(layers: list, extent: QgsRectangle) -> QImage:
    settings = QgsMapSettings()
    settings.setLayers(layers)
    settings.setDestinationCrs(DESTINATION_CRS)
    settings.setExtent(extent)
    settings.setOutputSize(QSize(MAP_RECT.width(), MAP_RECT.height()))
    settings.setBackgroundColor(QColor("#12151d"))
    settings.setFlag(Qgis.MapSettingsFlag.Antialiasing, True)
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    return job.renderedImage()


def draw_wrapped(
    painter: QPainter,
    text: str,
    rect: QRect,
    font: QFont,
    color: QColor,
    flags: int = Qt.TextFlag.TextWordWrap.value,
) -> None:
    painter.setFont(font)
    painter.setPen(color)
    alignment = Qt.AlignmentFlag.AlignLeft.value | Qt.AlignmentFlag.AlignTop.value
    painter.drawText(rect, flags | alignment, text)


def draw_panel(
    painter: QPainter,
    rect: QRect,
    color: QColor,
    heading: str,
    bullets: list[str],
) -> None:
    painter.fillRect(rect, QColor("#19212d"))
    painter.setPen(QPen(color, 4))
    painter.drawRoundedRect(rect, 15, 15)
    painter.fillRect(QRect(rect.x(), rect.y(), 12, rect.height()), color)
    draw_wrapped(
        painter,
        heading.upper(),
        QRect(rect.x() + 34, rect.y() + 22, rect.width() - 58, 44),
        QFont("Helvetica Neue", 24, QFont.Weight.Bold),
        color,
    )

    body_font = QFont("Helvetica Neue", 25)
    metrics = QFontMetrics(body_font)
    y = rect.y() + 75
    available_width = rect.width() - 70
    for bullet in bullets:
        text = f"• {bullet}"
        bounds = metrics.boundingRect(
            QRect(0, 0, available_width, rect.height()),
            Qt.TextFlag.TextWordWrap.value,
            text,
        )
        height = bounds.height() + 14
        draw_wrapped(
            painter,
            text,
            QRect(rect.x() + 34, y, available_width, height),
            body_font,
            QColor("#f2f4f8"),
        )
        y += height


def card_key_observations(card: dict[str, object], distance: int | None) -> list[str]:
    observations = list(card["publicMapObservations"])
    if distance is not None:
        observations = [
            observations[0],
            f"Nearest displayed AMO record: about {distance / 1000:.1f} km from the graphical parcel.",
        ]
    return observations


def render_card(
    card: dict[str, object], aerial: QgsRasterLayer, project: QgsProject
) -> tuple[Path, int | None, int]:
    lien = int(card["lien"])
    parcels = labelled_parcel_layer(lien)
    project.addMapLayer(parcels)
    evidence_layers: list[QgsVectorLayer] = [parcels]
    map_layers: list = [parcels]
    mine_distance: int | None = None
    mine_count = 0

    if card["mapMode"] == "aerial-parcel-amo":
        amo_filter = card["amoFilter"]
        mines = abandoned_mine_layer(amo_filter["field"], amo_filter["value"])
        project.addMapLayer(mines)
        evidence_layers.append(mines)
        map_layers.append(mines)
        mine_count = sum(1 for _ in mines.getFeatures())
        mine_distance = nearest_distance_metres(parcels, mines, project)

    map_layers.append(aerial)
    extent = fit_extent(
        combined_extent(evidence_layers, project),
        minimum_width=float(card["mapMinimumWidthMetres"]),
    )
    map_image = render_map_image(map_layers, extent)

    image = QImage(WIDTH, HEIGHT, QImage.Format.Format_RGB32)
    image.fill(QColor("#10151e"))
    painter = QPainter(image)

    draw_wrapped(
        painter,
        card["title"],
        QRect(58, 40, 1880, 62),
        QFont("Helvetica Neue", 42, QFont.Weight.Bold),
        QColor("#ffffff"),
    )
    facts = card["municipalFacts"]
    pid_text = ", ".join(facts["pids"])
    fact_line = (
        f"August 11, 2026 · AAN {facts['aan']} · PID{'s' if len(facts['pids']) > 1 else ''} "
        f"{pid_text} · Recovery ${facts['recoveryAmount']:,.2f} · "
        f"Redeemable: {'YES' if facts['redeemable'] else 'NO'}"
    )
    painter.fillRect(QRect(55, 112, 2450, 62), QColor("#17365d"))
    draw_wrapped(
        painter,
        fact_line,
        QRect(76, 128, 2400, 38),
        QFont("Helvetica Neue", 23, QFont.Weight.DemiBold),
        QColor("#ffffff"),
    )

    painter.drawImage(MAP_RECT, map_image)
    painter.setPen(QPen(QColor("#f3f5f8"), 3))
    painter.drawRect(MAP_RECT)
    map_caption = QRect(MAP_RECT.x(), MAP_RECT.bottom() - 104, MAP_RECT.width(), 105)
    painter.fillRect(map_caption, QColor(10, 15, 22, 215))
    draw_wrapped(
        painter,
        card["mapSubtitle"],
        QRect(map_caption.x() + 26, map_caption.y() + 18, map_caption.width() - 52, 38),
        QFont("Helvetica Neue", 25, QFont.Weight.DemiBold),
        QColor("#ffffff"),
    )
    legend = "Yellow boundary: listed NSPRD graphic"
    if mine_distance is not None:
        legend += " · Red diamond: 2024 AMO record"
    draw_wrapped(
        painter,
        legend,
        QRect(map_caption.x() + 26, map_caption.y() + 59, map_caption.width() - 52, 30),
        QFont("Helvetica Neue", 19),
        QColor("#d9dee8"),
    )

    right_x = 1550
    right_width = 955
    draw_panel(
        painter,
        QRect(right_x, 205, right_width, 285),
        QColor("#d68b35"),
        "Mapped screening observation",
        card_key_observations(card, mine_distance),
    )
    draw_panel(
        painter,
        QRect(right_x, 515, right_width, 250),
        QColor("#e05c68"),
        "What this does not prove",
        list(card["limitations"][:2]),
    )
    draw_panel(
        painter,
        QRect(right_x, 790, right_width, 475),
        QColor("#d455bd"),
        "Questions to hand off",
        list(card["unresolvedQuestions"]),
    )

    status_line = (
        f"Municipal listing snapshot: July 19, 2026 · {facts['location']} · "
        "Confirm the live list · Review candidate · No ranking or bid recommendation"
    )
    draw_wrapped(
        painter,
        status_line,
        QRect(58, 1291, 2445, 30),
        QFont("Helvetica Neue", 17, QFont.Weight.DemiBold),
        QColor("#f0f2f6"),
    )
    source_line = ATTRIBUTION
    if mine_distance is not None:
        source_line += f" {OPEN_DATA_ATTRIBUTION}"
    draw_wrapped(
        painter,
        source_line,
        QRect(58, 1330, 2445, 55),
        QFont("Helvetica Neue", 14),
        QColor("#cbd2df"),
    )
    draw_wrapped(
        painter,
        "Parcel graphics are not surveys. This card is not legal access, a title opinion, hazard finding, appraisal, or permission to enter.",
        QRect(58, 1382, 2445, 34),
        QFont("Helvetica Neue", 14),
        QColor("#cbd2df"),
    )
    painter.end()

    output = ATLAS_ROOT / card["filename"]
    if not image.save(str(output), "PNG"):
        raise RuntimeError(f"Could not save {output}")
    return output, mine_distance, mine_count


def contact_sheet(
    images: list[Path], target: Path, cell_width: int, cell_height: int
) -> None:
    sheet = QImage(cell_width * len(images), cell_height, QImage.Format.Format_RGB32)
    sheet.fill(QColor("#10151e"))
    painter = QPainter(sheet)
    for index, path in enumerate(images):
        image = QImage(str(path))
        scaled = image.scaled(
            cell_width,
            cell_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(index * cell_width, 0, scaled)
    painter.end()
    if not sheet.save(str(target), "PNG"):
        raise RuntimeError(f"Could not save {target}")


def run() -> None:
    if not GEOJSON.exists():
        raise RuntimeError("Run build_map_assets.py before rendering atlas prototypes")
    if not AMO_ARCHIVE.exists():
        raise RuntimeError("AMO archive missing; run build_map_assets.py first")

    specs = load_specs()
    ATLAS_ROOT.mkdir(parents=True, exist_ok=True)
    project = QgsProject.instance()
    project.clear()
    project.setTitle("Inverness Packet Atlas — three-card prototype")
    project.setCrs(DESTINATION_CRS)
    aerial = aerial_layer()
    project.addMapLayer(aerial)

    outputs: list[Path] = []
    receipt_files: list[dict[str, object]] = []
    mine_distance: int | None = None
    mine_count = 0
    for card in specs["cards"]:
        output, card_distance, card_mine_count = render_card(card, aerial, project)
        outputs.append(output)
        receipt_files.append(
            {
                "lien": card["lien"],
                "filename": output.name,
                "sha256": sha256(output),
                "width": WIDTH,
                "height": HEIGHT,
                "mode": "RGB",
            }
        )
        if card_distance is not None:
            mine_distance = card_distance
            mine_count = card_mine_count

    contact_sheet(outputs, CONTACT_SHEET_PATH, 1280, 720)
    contact_sheet(outputs, PHONE_SHEET_PATH, 640, 360)
    if mine_distance is None:
        raise RuntimeError("Mine-screening prototype did not calculate a distance")

    receipt = {
        "schemaVersion": 1,
        "assetStatus": "review-candidate",
        "renderer": "QGIS 4",
        "qgisVersion": Qgis.QGIS_VERSION,
        "renderedDate": date.today().isoformat(),
        "specPath": "atlas-prototype-specs.json",
        "specSHA256": sha256(SPECS_PATH),
        "listingDataSHA256": sha256(LISTING_DATA),
        "amoArchiveSHA256": sha256(AMO_ARCHIVE),
        "canonicalFigureManifestChanged": False,
        "propertyOnlineUsed": False,
        "humanAcceptance": "pending",
        "files": receipt_files,
        "reviewAids": [
            {
                "filename": CONTACT_SHEET_PATH.name,
                "sha256": sha256(CONTACT_SHEET_PATH),
                "width": 3840,
                "height": 720,
            },
            {
                "filename": PHONE_SHEET_PATH.name,
                "sha256": sha256(PHONE_SHEET_PATH),
                "width": 1920,
                "height": 360,
            },
        ],
        "mineScreening": {
            "sourceProduct": "DP ME 10, Version 9, 2024",
            "filter": "S_Location = BRIGEND BROOK (SOAPSTONE MINE)",
            "recordedOpeningCount": mine_count,
            "nearestRecordedOpeningMetres": mine_distance,
            "measurement": "Minimum planar distance after transforming the NSPRD graphic into the AMO layer CRS.",
            "limitations": [
                "Inventory is incomplete.",
                "Database excludes surface expressions of subsidence.",
                "Private-land positions could be inaccurate by up to about 50 metres.",
            ],
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


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
