"""
Extract layer footprints from multiple WMS services and save per-service GeoJSON files.
"""

import re
import requests
import urllib3
import xml.etree.ElementTree as ET
from datetime import date
from shapely.geometry import box
import geopandas as gpd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVICES = [
    ("toma2024",    "Ortofotos Año de Toma 2024",         "https://www.geoportaligm.gob.ec/orto/toma2024/wms"),
    ("toma2023",    "Ortofotos Año de Toma 2023",         "https://www.geoportaligm.gob.ec/orto/toma2023/wms"),
    ("toma2022",    "Ortofotos Año de Toma 2022",         "https://www.geoportaligm.gob.ec/orto/toma2022/wms"),
    ("toma2021",    "Ortofotos Año de Toma 2021",         "https://www.geoportaligm.gob.ec/orto/toma2021/wms"),
    ("toma2020",    "Ortofotos Año de Toma 2020",         "https://www.geoportaligm.gob.ec/orto/toma2020/wms"),
    ("igm",         "IGM - Ortofotos",                   "https://www.geoportaligm.gob.ec/orto/igm/wms"),
    ("uav_igm",     "IGM - Ortofotos UAV",               "https://www.geoportaligm.gob.ec/orto/uav_igm/wms"),
    ("uav_ecu",     "Ortofotos UAV Ecuador",              "https://www.geoportaligm.gob.ec/orto/uav_ecu/wms"),
    ("uav_ucuenca", "Ortofotos UAV U. de Cuenca",         "https://www.geoportaligm.gob.ec/orto/uav_ucuenca/wms"),
]

NS = "http://www.opengis.net/wms"


def tag(name):
    return f"{{{NS}}}{name}"


def find(el, name):
    return el.find(tag(name))


def findtext(el, name):
    child = find(el, name)
    return child.text.strip() if child is not None and child.text else ""


def fetch_capabilities(url):
    resp = requests.get(
        url,
        params={"SERVICE": "WMS", "REQUEST": "GetCapabilities"},
        timeout=60,
        verify=False,
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def parse_geo_bbox(layer_el):
    ex = find(layer_el, "EX_GeographicBoundingBox")
    if ex is None:
        return None
    try:
        return (
            float(findtext(ex, "westBoundLongitude")),
            float(findtext(ex, "southBoundLatitude")),
            float(findtext(ex, "eastBoundLongitude")),
            float(findtext(ex, "northBoundLatitude")),
        )
    except (ValueError, AttributeError):
        return None


def parse_capture_date(abstract):
    match = re.search(r"Fecha captura/toma:\s*(\d{8})", abstract)
    if match is None:
        return None
    raw = match.group(1)
    try:
        return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
    except ValueError:
        return None


def extract_year(text: str) -> int | None:
    """Extract a plausible capture year from a name or title string."""
    # 1. YYYYMMDD — 8 consecutive digits with valid month/day
    m = re.search(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1990 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
            return y

    # 2. YYYY-MM-DD or YYYY_MM_DD
    m = re.search(r"(?<!\d)(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1990 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
            return y

    # 3. Any standalone 4-digit year in valid range
    years = [int(y) for y in re.findall(r"(?<!\d)(\d{4})(?!\d)", text)
             if 1990 <= int(y) <= 2030]
    if years:
        return years[0]

    return None


def process_service(service_id, service_label, url):
    print(f"\n[{service_id}] {service_label}")
    print(f"  Fetching {url}")
    root = fetch_capabilities(url)

    capability = find(root, "Capability")
    root_layer = find(capability, "Layer")
    layers = root_layer.findall(tag("Layer"))
    print(f"  Found {len(layers)} layers")

    records = []
    for layer_el in layers:
        name = findtext(layer_el, "Name")
        if not name:
            continue
        title    = findtext(layer_el, "Title")
        abstract = findtext(layer_el, "Abstract")
        bbox     = parse_geo_bbox(layer_el)

        if bbox is None:
            print(f"    [skip] {name!r} — no bbox")
            continue

        west, south, east, north = bbox
        capture_date = parse_capture_date(abstract)
        if capture_date is not None:
            anio = capture_date.year
        else:
            anio = extract_year(name) or extract_year(title)

        records.append({
            "service":        service_id,
            "service_label":  service_label,
            "name":           name,
            "title":          title,
            "abstract":       abstract,
            "fecha_toma":     capture_date.isoformat() if capture_date is not None else None,
            "anio_toma":      anio,
            "west":  west, "south": south, "east": east, "north": north,
            "geometry": box(west, south, east, north),
        })

    print(f"  Saved {len(records)} features")
    return records


def main():
    all_records = []
    for service_id, service_label, url in SERVICES:
        try:
            records = process_service(service_id, service_label, url)
            all_records.extend(records)
            # individual file
            gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
            out = f"{service_id}_footprints.geojson"
            gdf.to_file(out, driver="GeoJSON")
        except Exception as exc:
            print(f"  ERROR: {exc}")

    # combined file
    combined = gpd.GeoDataFrame(all_records, crs="EPSG:4326")
    combined.to_file("OrtofotosIGM_all.geojson", driver="GeoJSON")
    print(f"\nDone — {len(all_records)} total features across {len(SERVICES)} services.")
    print("Combined → OrtofotosIGM_all.geojson")


if __name__ == "__main__":
    main()
