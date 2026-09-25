# Cell Grid Creator — QGIS Plugin (v1.0.01)

**Cell Grid Creator** is a QGIS plugin designed to automatically generate standardized geographic degree grid coverage bounded by a selected Area of Interest (AOI). It processes various spatial input formats, calculates detailed grid cell attributes, and exports the final layer into an organized directory structure.

---

## Key Features

* **Multiple Grid Scales:** Pre-configured scale selections ranging from 1° x 1° down to 1' x 1' (0.016667°).
* **Wide AOI Format Support:** Native support for ESRI Shapefiles (`.shp`), KML (`.kml`), KMZ (`.kmz` with automatic extraction), and GeoJSON (`.geojson`, `.json`).
* **Automatic Coordinate & Code Calculation:** Calculates key attributes for every cell:
  * `GID` & `ID`: Global unique identifiers based on spatial grid indices.
  * `X_COORD` / `Y_COORD`: Centroid coordinates in EPSG:4326.
  * `XMIN` / `YMIN`: Bounding minimums.
  * `CODE` / `CELLNAME`: Standardized degree/minute alpha-numeric naming conventions (e.g., `*07800E1730N*`).
  * `EXPORT`: Formatted export string containing extent coordinates and unique scale prefix identifiers.
* **Automatic Spatial Reprojection:** Handles multi-CRS AOIs and normalizes output geometry to EPSG:4326 WGS 84.
* **Structured Output Directory:** Automatically creates a `CELL_GRID` directory inside your source folder and saves the output as an ESRI Shapefile.
* **Custom UI Theme:** Native Qt interface featuring a styled Windows 7 Aero Glass theme.

---

## Supported Grid Scales

| Dropdown Option | Grid Resolution | Scale Prefix | Output Slug |
| :--- | :--- | :--- | :--- |
| `1°x1°_Grid (1°)` | 1.0° | `A` | `1x1grid` |
| `30'x30'_Grid (0.5°)` | 0.5° | `B` | `30x30grid` |
| `15'x15'_Grid (0.25°)` | 0.25° | `C` | `15x15_grid` |
| `7.5'x7.5'_Grid (0.125°)` | 0.125° | `D` | `7.5x7.5min_grid` |
| `3.8'x3.8'_Grid (0.0625°)` | 0.0625° | `E` | `3.75min_grid` |
| `2.5'x2.5'_Grid (0.041667°)` | 0.041667° | `F` | `2.5min_grid` |
| `1.3'x1.3'_Grid (0.020833°)` | 0.020833° | `G` | `1.25min_grid` |
| `1'x1'_Grid (0.016667°)` | 0.016667° | `H` | `1min_grid` |

---

## Directory & File Structure

Place the plugin files in your QGIS Python plugins directory:

* **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\cell_grid_creator\`
* **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/cell_grid_creator/`
* **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/cell_grid_creator/`

Your plugin directory structure:

```text
cell_grid_creator/
├── __init__.py
├── cell_grid_creator.py
├── metadata.txt
├── icon.png
├── README.md
└── LICENSE
