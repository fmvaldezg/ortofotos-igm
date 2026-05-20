# Ortofotos IGM Ecuador — Webmap

Interactive map of all orthophoto layers published by the **Instituto Geográfico Militar (IGM) Ecuador** across their WMS services.

**[View the map →](https://fmvaldezg.github.io/ortofotos-igm/OrtofotosIGM2024.html)**

---

## What it shows

466 orthophoto footprints from 9 IGM WMS services, color-coded by service:

| Service | URL |
|---|---|
| Ortofotos Año de Toma 2024 | `https://www.geoportaligm.gob.ec/orto/toma2024/wms` |
| Ortofotos Año de Toma 2023 | `https://www.geoportaligm.gob.ec/orto/toma2023/wms` |
| Ortofotos Año de Toma 2022 | `https://www.geoportaligm.gob.ec/orto/toma2022/wms` |
| Ortofotos Año de Toma 2021 | `https://www.geoportaligm.gob.ec/orto/toma2021/wms` |
| Ortofotos Año de Toma 2020 | `https://www.geoportaligm.gob.ec/orto/toma2020/wms` |
| IGM - Ortofotos | `https://www.geoportaligm.gob.ec/orto/igm/wms` |
| IGM - Ortofotos UAV | `https://www.geoportaligm.gob.ec/orto/uav_igm/wms` |
| Ortofotos UAV Ecuador | `https://www.geoportaligm.gob.ec/orto/uav_ecu/wms` |
| Ortofotos UAV U. de Cuenca | `https://www.geoportaligm.gob.ec/orto/uav_ucuenca/wms` |

## Features

- **Filter by service** — click a legend row to show only that service
- **Filter by capture year** — use the year pills in the header
- **Click any footprint** to get ready-to-use WMS URLs:
  - **iD Editor** — full GetMap URL template with `{proj}`, `{width}`, `{height}`, `{bbox}` placeholders
  - **JOSM / QGIS** — service URL to paste in "Add WMS Connection" + layer name to select

## Files

| File | Description |
|---|---|
| `OrtofotosIGM2024.html` | Self-contained interactive webmap (GeoJSON embedded, no server needed) |
| `wms_footprints.py` | Python script to re-extract footprints from all 9 WMS services |
| `OrtofotosIGM_all.geojson` | Combined GeoJSON with all 466 features |
| `{service}_footprints.geojson` | Per-service GeoJSON files |
| `favicon.ico` | IGM logo used by the map |

## Regenerating the data

Requires Python 3.10+ with `requests`, `shapely`, and `geopandas`.

```bash
pip install requests shapely geopandas
python wms_footprints.py
```

This queries `GetCapabilities` on each WMS service, extracts bounding boxes and metadata, and writes per-service GeoJSON files plus `OrtofotosIGM_all.geojson`. To update the webmap, re-embed the combined GeoJSON into `OrtofotosIGM2024.html` (replace the `const GEOJSON = {...}` block).

## Tech stack

- [MapLibre GL JS v4](https://maplibre.org/) — rendering
- [OpenFreeMap Positron](https://openfreemap.org/) — basemap
- Python: `requests`, `xml.etree.ElementTree`, `geopandas`, `shapely`
