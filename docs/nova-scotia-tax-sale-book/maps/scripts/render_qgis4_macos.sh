#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
qgis_app="${QGIS4_APP:-/Applications/QGIS-final-4_0_2.app}"
qgis_python="$qgis_app/Contents/MacOS/python3.12"
qgis_resources="$qgis_app/Contents/Resources"

if [[ ! -x "$qgis_python" ]]; then
  print -u2 "QGIS 4 Python runtime not found: $qgis_python"
  print -u2 "Set QGIS4_APP to the QGIS 4 application bundle."
  exit 1
fi

env \
  QT_QPA_PLATFORM=offscreen \
  QGIS_PREFIX_PATH="$qgis_app" \
  PYTHONPATH="$qgis_resources/python3.11:$qgis_resources/python3.11/lib-dynload:$qgis_resources/python3.11/site-packages" \
  DYLD_LIBRARY_PATH="$qgis_app/Contents/Frameworks" \
  PROJ_DATA="$qgis_resources/qgis/proj" \
  "$qgis_python" \
  "$script_dir/render_qgis_maps.py"

env \
  QT_QPA_PLATFORM=offscreen \
  QGIS_PREFIX_PATH="$qgis_app" \
  PYTHONPATH="$qgis_resources/python3.11:$qgis_resources/python3.11/lib-dynload:$qgis_resources/python3.11/site-packages" \
  DYLD_LIBRARY_PATH="$qgis_app/Contents/Frameworks" \
  PROJ_DATA="$qgis_resources/qgis/proj" \
  "$qgis_python" \
  "$script_dir/render_atlas_prototypes.py"
