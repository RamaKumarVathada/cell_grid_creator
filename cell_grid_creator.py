"""
Cell Grid Creator  — QGIS Plugin 
==============================================
Cell Grid Creator is a QGIS plugin for creating standardized geographic grid cells within a selected AOI. 
Users can select the required grid scale, browse supported AOI formats, and generate the corresponding grid automatically. 
The plugin creates cell identifiers, coordinates, codes, export information, and cell names, 
and saves the generated grid as an ESRI Shapefile in a CELL_GRID output folder.

Version: 1.0.01 (Generate Cell Grid Coverage by AOI)
Author: Rama Kumar Vathada
"""

import os
import json
import zipfile
import tempfile
import xml.etree.ElementTree as ET

# PyQt Imports
from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QComboBox, 
                                 QPushButton, QLabel, QMessageBox, QHBoxLayout, 
                                 QLineEdit, QFileDialog, QGroupBox, QStyledItemDelegate)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant

# QGIS Core & Processing Imports
from qgis.core import (QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, 
                       QgsField, QgsVectorLayer, QgsVectorFileWriter, 
                       QgsCoordinateTransform, QgsApplication, QgsFeatureRequest)
import processing
from processing.core.Processing import Processing

class DegreeGridGeneratorDialog(QDialog):
    def __init__(self, geojson_data=None, parent=None):
        super(DegreeGridGeneratorDialog, self).__init__(parent)
        self.setWindowTitle("Cell Grid Creator (v1.0.01)")
        self.resize(520, 260)
        self.geojson_data = geojson_data
        
        # ==========================================
        # WINDOWS 7 AERO GLASS THEME SETTINGS
        # ==========================================
        self.setWindowOpacity(0.97) 
        
        self.setStyleSheet("""
            /* Main Dialog Background */
            QDialog {
                background-color: rgba(224, 235, 235, 180);
            }

            /* Windows 7 Style Group Boxes */
            QGroupBox {
                background-color: rgba(255, 255, 255, 60);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #003399;
                font-weight: bold;
                left: 10px;
            }

            /* Standard Labels */
            QLabel {
                color: #1a1a1a;
                font-size: 12px;
            }
            
            /* Input Fields and Dropdowns */
            QLineEdit, QComboBox {
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 4px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3c7fb1;
            }

            /* --- NEW: ComboBox Dropdown Button Windows 7 Styling --- */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border-left: 1px solid #bcbcbc;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #f2f2f2, stop: 0.5 #ebebeb,
                                                  stop: 0.51 #dddddd, stop: 1 #cfcfcf);
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::drop-down:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #eaf6fd, stop: 0.5 #d9f0fc,
                                                  stop: 0.51 #bee6fd, stop: 1 #a7d9f5);
            }
            
            /* --- NEW: ComboBox Popup List Windows 7 Styling --- */
            QComboBox QAbstractItemView {
                border: 1px solid #707070;
                background-color: rgba(255, 255, 255, 245); /* Slight glass transparency */
                selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #eaf6fd, stop: 0.5 #d9f0fc,
                                                  stop: 0.51 #bee6fd, stop: 1 #a7d9f5); /* Classic Win7 Blue Highlight */
                selection-color: black;
                outline: none; /* Removes the ugly dotted focus line */
            }
            QComboBox QAbstractItemView::item {
                min-height: 24px; /* Gives the items proper spacing */
                padding: 4px;
            }
            /* -------------------------------------------------------- */

            /* Windows 7 Glossy Buttons */
            QPushButton {
                border: 1px solid #707070;
                border-radius: 3px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #f2f2f2, stop: 0.5 #ebebeb,
                                                  stop: 0.51 #dddddd, stop: 1 #cfcfcf);
                padding: 5px 15px;
                color: black;
            }
            QPushButton:hover {
                border: 1px solid #3c7fb1;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #eaf6fd, stop: 0.5 #d9f0fc,
                                                  stop: 0.51 #bee6fd, stop: 1 #a7d9f5);
            }
            QPushButton:pressed {
                border: 1px solid #2c628b;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #e5f4fc, stop: 0.5 #c4e5f6,
                                                  stop: 0.51 #98d1ef, stop: 1 #68b3db);
            }
            QPushButton:disabled {
                border: 1px solid #999999;
                background-color: #cccccc;
                color: #777777;
            }
            
            /* Specific style for 3-dots button */
            QPushButton#BrowseBtn {
                padding: 4px;
                font-weight: bold;
            }
            
            /* Generate Button specific emphasis */
            QPushButton#GenerateBtn {
                font-weight: bold;
                padding: 8px 15px;
            }
        """)
        # ==========================================
        
        try:
            Processing.initialize()
        except Exception:
            pass
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # 1. Grid Settings
        grid_group = QGroupBox("Cell Grid Configuration")
        grid_layout = QVBoxLayout()
        
        self.label = QLabel("Select Grid Scale:")
        grid_layout.addWidget(self.label)
        
        self.combo = QComboBox()
        self.combo.addItem("1°x1°_Grid (1°)", {"size": 1.0, "prefix": "A", "slug": "1x1grid"})
        self.combo.addItem("30'x30'_Grid (0.5°)", {"size": 0.5, "prefix": "B", "slug": "30x30grid"})
        self.combo.addItem("15'x15'_Grid (0.25°)", {"size": 0.25, "prefix": "C", "slug": "15x15_grid"})
        self.combo.addItem("7.5'x7.5'_Grid (0.125°)", {"size": 0.125, "prefix": "D", "slug": "7.5x7.5min_grid"})
        self.combo.addItem("3.8'x3.8'_Grid (0.0625°)", {"size": 0.0625, "prefix": "E", "slug": "3.75min_grid"})
        self.combo.addItem("2.5'x2.5'_Grid (0.041667°)", {"size": 0.041667, "prefix": "F", "slug": "2.5min_grid"})
        self.combo.addItem("1.3'x1.3'_Grid (0.020833°)", {"size": 0.020833, "prefix": "G", "slug": "1.25min_grid"})
        self.combo.addItem("1'x1'_Grid (0.016667°)", {"size": 0.016667, "prefix": "H", "slug": "1min_grid"})
        
        # Apply item delegate fix to ensure the CSS item styling renders properly in QComboBox lists
        self.combo.setItemDelegate(QStyledItemDelegate(self.combo))
        
        grid_layout.addWidget(self.combo)
        
        grid_group.setLayout(grid_layout)
        main_layout.addWidget(grid_group)
        
        # 2. AOI Selection
        aoi_group = QGroupBox("Choose AOI for Grid")
        aoi_inner_layout = QVBoxLayout()
        
        self.aoi_label = QLabel("Select AOI File (.shp, .kml, .kmz, .geojson, .json):")
        aoi_inner_layout.addWidget(self.aoi_label)
        
        file_layout = QHBoxLayout()
        self.aoi_path_input = QLineEdit()
        self.aoi_path_input.setPlaceholderText("Select AOI file path...")
        file_layout.addWidget(self.aoi_path_input)
        
        self.btn_browse = QPushButton("...")
        self.btn_browse.setObjectName("BrowseBtn")
        self.btn_browse.setFixedWidth(25)
        self.btn_browse.clicked.connect(self.browse_aoi_file)
        file_layout.addWidget(self.btn_browse)
        
        aoi_inner_layout.addLayout(file_layout)
        aoi_group.setLayout(aoi_inner_layout)
        main_layout.addWidget(aoi_group)
        
        # 3. Generate Button
        self.btn_generate = QPushButton("Generate Cell Grid Coverage")
        self.btn_generate.setObjectName("GenerateBtn")
        self.btn_generate.clicked.connect(self.run_grid_tool)
        main_layout.addWidget(self.btn_generate)
        
        self.setLayout(main_layout)

    def browse_aoi_file(self):
        file_filter = "All Supported AOI Formats (*.shp *.kml *.kmz *.geojson *.json);;Shapefile (*.shp);;KML File (*.kml);;KMZ File (*.kmz);;GeoJSON File (*.geojson *.json)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Select AOI File", "", file_filter)
        if filepath:
            self.aoi_path_input.setText(filepath)

    def extract_kmz(self, kmz_path):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        kml_path = os.path.join(temp_dir, "doc.kml")
        if os.path.exists(kml_path):
            return kml_path
            
        for file in os.listdir(temp_dir):
            if file.lower().endswith(".kml"):
                return os.path.join(temp_dir, file)
                
        raise Exception("No valid KML file found inside the KMZ archive.")

    def get_aoi_layer_and_info(self):
        aoi_path = self.aoi_path_input.text().strip()
        from qgis.utils import iface
        
        if aoi_path:
            if not os.path.exists(aoi_path):
                raise Exception(f"AOI file path does not exist: {aoi_path}")
            
            ext = os.path.splitext(aoi_path)[1].lower()
            aoi_name = os.path.splitext(os.path.basename(aoi_path))[0]
            base_dir = os.path.dirname(aoi_path)
            
            target_file = aoi_path
            if ext == '.kmz':
                target_file = self.extract_kmz(aoi_path)
            
            layer = QgsVectorLayer(target_file, "AOI_Layer", "ogr")
            if not layer.isValid():
                raise Exception("Failed to load selected AOI file into QGIS.")
            
            crs_src = layer.crs()
            crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
            extent = layer.extent()
            
            if crs_src.isValid() and crs_src != crs_wgs84:
                transform = QgsCoordinateTransform(crs_src, crs_wgs84, QgsProject.instance())
                extent = transform.transformBoundingBox(extent)
                
            return layer, extent, base_dir, aoi_name

        if self.geojson_data:
            json_str = json.dumps(self.geojson_data) if isinstance(self.geojson_data, dict) else self.geojson_data
            layer = QgsVectorLayer(f"GeoJSON:{json_str}", "AOI_Layer", "ogr")
            geom = QgsGeometry.fromGeoJson(json_str)
            return layer, geom.boundingBox(), None, "AOI"
            
        raise Exception("No valid Area of Interest provided.")

    def run_grid_tool(self):
        if not self.aoi_path_input.text().strip() and not self.geojson_data:
            QMessageBox.warning(self, "Validation Error", "Please browse and select an Area of Interest (AOI) file before generating the grid.")
            return

        selected_info = self.combo.currentData()
        grid_size = float(selected_info["size"])
        prefix = selected_info["prefix"]
        slug = selected_info["slug"]
        
        try:
            import processing
            
            aoi_layer, extent, base_dir, aoi_name = self.get_aoi_layer_and_info()
            crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
            
            snap_xmin = round(extent.xMinimum() / grid_size) * grid_size
            snap_xmax = round(extent.xMaximum() / grid_size) * grid_size
            snap_ymin = round(extent.yMinimum() / grid_size) * grid_size
            snap_ymax = round(extent.yMaximum() / grid_size) * grid_size

            if snap_xmin > extent.xMinimum(): snap_xmin -= grid_size
            if snap_xmax < extent.xMaximum(): snap_xmax += grid_size
            if snap_ymin > extent.yMinimum(): snap_ymin -= grid_size
            if snap_ymax < extent.yMaximum(): snap_ymax += grid_size

            grid_extent = f"{snap_xmin},{snap_xmax},{snap_ymin},{snap_ymax} [{crs_wgs84.authid()}]"

            params = {
                'TYPE': 2,
                'EXTENT': grid_extent,
                'HSPACING': grid_size,
                'VSPACING': grid_size,
                'HOVERLAY': 0,
                'VOVERLAY': 0,
                'CRS': crs_wgs84,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
            
            result = processing.run("native:creategrid", params)
            grid_layer = result['OUTPUT']
            
            if aoi_layer and aoi_layer.isValid():
                if aoi_layer.crs() != crs_wgs84:
                    reproject_params = {
                        'INPUT': aoi_layer,
                        'TARGET_CRS': crs_wgs84,
                        'OUTPUT': 'TEMPORARY_OUTPUT'
                    }
                    aoi_layer = processing.run("native:reprojectlayer", reproject_params)['OUTPUT']

                extract_params = {
                    'INPUT': grid_layer,
                    'PREDICATE': [0],
                    'INTERSECT': aoi_layer,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
                grid_layer = processing.run("native:extractbylocation", extract_params)['OUTPUT']

            desired_fields = ['GID', 'ID', 'X_COORD', 'Y_COORD', 'XMIN', 'YMIN', 'CODE', 'EXPORT', 'CELLNAME']
            
            fields_to_add = [
                QgsField("GID", QVariant.Int),
                QgsField("ID", QVariant.Double),
                QgsField("X_COORD", QVariant.Double),
                QgsField("Y_COORD", QVariant.Double),
                QgsField("XMIN", QVariant.Double),
                QgsField("YMIN", QVariant.Double),
                QgsField("CODE", QVariant.String),
                QgsField("EXPORT", QVariant.String),
                QgsField("CELLNAME", QVariant.String)
            ]
            
            grid_layer.dataProvider().addAttributes(fields_to_add)
            grid_layer.updateFields()
            
            fields_to_delete = [i for i, field in enumerate(grid_layer.fields()) if field.name() not in desired_fields]
            if fields_to_delete:
                grid_layer.dataProvider().deleteAttributes(fields_to_delete)
                grid_layer.updateFields()
            
            grid_layer.startEditing()
            
            def fmt_lon(v):
                d = int(abs(v))
                m = int(round((abs(v) - d) * 60))
                return f"{d:03d}{m:02d}{'W' if v < 0 else 'E'}"
                
            def fmt_lat(v):
                d = int(abs(v))
                m = int(round((abs(v) - d) * 60))
                return f"{d:02d}{m:02d}{'S' if v < 0 else 'N'}"

            def fmt_code_val(v, pos_char, neg_char):
                char = neg_char if v < 0 else pos_char
                val_str = f"{abs(v):g}"
                return f"{char}{val_str}"

            n_lon_steps = int(round(360.0 / grid_size))
            n_lat_steps = int(round(180.0 / grid_size))

            for feat in grid_layer.getFeatures():
                geom = feat.geometry()
                bbox = geom.boundingBox()
                
                x_min, y_min = bbox.xMinimum(), bbox.yMinimum()
                x_max, y_max = bbox.xMaximum(), bbox.yMaximum()
                
                x_coord = (x_min + x_max) / 2.0
                y_coord = (y_min + y_max) / 2.0
                
                row_idx = int(round((90.0 - y_max) / grid_size))
                col_idx = int(round((x_min - (-180.0)) / grid_size))
                gid_val = (row_idx * n_lon_steps) + col_idx + 1
                
                lat_idx = int(round((90.0 - y_min) / grid_size))
                unique_num = (col_idx * n_lat_steps) + lat_idx
                unique_code = f"{prefix}{unique_num}"
                
                code_str = f"{fmt_code_val(x_min, 'E', 'W')}{fmt_code_val(y_min, 'N', 'S')}"
                cellname = f"*{fmt_lon(x_min)}{fmt_lat(y_min)}*"
                export_val = f"1,{fmt_lon(x_min)},{fmt_lat(y_min)},{fmt_lon(x_max)},{fmt_lat(y_max)},{unique_code}"
                
                feat['GID'] = gid_val
                feat['ID'] = float(gid_val)
                feat['X_COORD'] = x_coord
                feat['Y_COORD'] = y_coord
                feat['XMIN'] = x_min
                feat['YMIN'] = y_min
                feat['CODE'] = code_str
                feat['EXPORT'] = export_val
                feat['CELLNAME'] = cellname
                
                grid_layer.updateFeature(feat)
                
            grid_layer.commitChanges()
            grid_layer.updateExtents()
            
            layer_title = f"{slug}_{aoi_name}"
            grid_layer.setName(layer_title)
            
            if base_dir:
                output_folder = os.path.join(base_dir, "CELL_GRID")
                os.makedirs(output_folder, exist_ok=True)
                
                output_shp_path = os.path.join(output_folder, f"{layer_title}.shp")
                
                writer_options = QgsVectorFileWriter.SaveVectorOptions()
                writer_options.driverName = "ESRI Shapefile"
                writer_options.fileEncoding = "UTF-8"
                
                error, error_msg = QgsVectorFileWriter.writeAsVectorFormatV2(
                    grid_layer, 
                    output_shp_path, 
                    QgsProject.instance().transformContext(), 
                    writer_options
                )
                
                if error == QgsVectorFileWriter.NoError:
                    saved_layer = QgsVectorLayer(output_shp_path, layer_title, "ogr")
                    QgsProject.instance().addMapLayer(saved_layer)
                else:
                    raise Exception(f"Failed to save shapefile: {error_msg}")
            else:
                QgsProject.instance().addMapLayer(grid_layer)
                
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate grid: {str(e)}")


class CellGridCreatorPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        if not os.path.exists(icon_path):
            self.action = QAction("Cell Grid Creator", self.iface.mainWindow())
        else:
            self.action = QAction(QIcon(icon_path), "Cell Grid Creator", self.iface.mainWindow())
            
        self.action.triggered.connect(self.run)
        
        self.iface.addPluginToVectorMenu("Cell Grid Creator", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginVectorMenu("Cell Grid Creator", self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.dialog is None:
            self.dialog = DegreeGridGeneratorDialog(parent=self.iface.mainWindow())
        self.dialog.show()
