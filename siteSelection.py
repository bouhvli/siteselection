# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SiteSelection
                                 A QGIS plugin
 site selection
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-06-27
        git sha              : $Format:%H$
        copyright            : (C) 2024 by hamza bouhali / none
        email                : elbouhalihamza34@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
# from functions import shapefile_to_raster, get_extent

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .siteSelection_dialog import SiteSelectionDialog
import os.path
from osgeo import gdal, ogr
from .suitability_value import SuitabilityValueDialog

def get_extent(shapefile):
        ds = ogr.Open(shapefile)
        layer = ds.GetLayer()
        extent = layer.GetExtent()
        ds = None
        return extent

def shapefile_to_raster(shapefile, output_path, xmin, xmax, ymin, ymax, resolution):
    try:
        source_ds = ogr.Open(shapefile)
        if source_ds is None:
            raise Exception(f"Failed to open source dataset: {shapefile}")

        source_layer = source_ds.GetLayer()

        # Create the destination raster dataset
        x_res = int((xmax - xmin) / resolution)
        y_res = int((ymax - ymin) / resolution)
        target_ds = gdal.GetDriverByName('GTiff').Create(output_path, x_res, y_res, 1, gdal.GDT_Byte)
            
        if target_ds is None:
            raise Exception(f"Failed to create raster dataset at: {output_path}")

        target_ds.SetGeoTransform((xmin, resolution, 0, ymax, 0, -resolution))

            # Set the projection from the source shapefile
        target_ds.SetProjection(source_layer.GetSpatialRef().ExportToWkt())

            # Rasterize the shapefile layer to the destination raster
        gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])

            # Close the datasets
        source_ds = None
        target_ds = None

        print(f"Rasterization completed successfully: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        if target_ds is not None:
            target_ds = None

def get_full_file_paths(directory):
    # List all files in the directory
    files = os.listdir(directory)
    
    # Get the full path for each file
    full_paths = [os.path.join(directory, file) for file in files]
    
    return full_paths

def calculate_proximity(input_raster, output_raster):
    try:
        # Open the input raster
        src_ds = gdal.Open(input_raster)
        if src_ds is None:
            raise Exception(f"Failed to open input raster: {input_raster}")

        # Create the output raster
        driver = gdal.GetDriverByName('GTiff')
        if driver is None:
            raise Exception("GTiff driver is not available")

        dst_ds = driver.Create(output_raster, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
        if dst_ds is None:
            raise Exception(f"Failed to create output raster: {output_raster}")

        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjectionRef())

        # Compute proximity
        gdal.ComputeProximity(src_ds.GetRasterBand(1), dst_ds.GetRasterBand(1), ["DISTUNITS=GEO"])

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Ensure datasets are properly closed
        if src_ds:
            src_ds = None
        if dst_ds:
            dst_ds = None

class SiteSelection:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        #
        
        self.sites_selection_dialog = SiteSelectionDialog()
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SiteSelection_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&site selection')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SiteSelection', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/siteSelection/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'site finder'),
            callback=self.run,
            parent=self.iface.mainWindow())
        #add variables
        self.sites_selection_dialog.runBtn.clicked.connect(self.__get_data)
        self.sites_selection_dialog.CriteriaNumberOneBtn.clicked.connect(self.open_suitability_dialog)
        self.sites_selection_dialog.CriteriaNumberTwoBtn.clicked.connect(self.open_suitability_dialog)
        self.sites_selection_dialog.CriteriaNumberThreeBtn.clicked.connect(self.open_suitability_dialog)
        self.sites_selection_dialog.CriteriaNumberFourBtn.clicked.connect(self.open_suitability_dialog)
        self.sites_selection_dialog.CriteriaNumberFiveBtn.clicked.connect(self.open_suitability_dialog)
        self.sites_selection_dialog.CriteriaNumberSixBtn.clicked.connect(self.open_suitability_dialog)
        # will be set False in run()
        self.first_start = True

    def open_suitability_dialog(self):
        # Create an instance of the new dialog
        suitability_dialog = SuitabilityValueDialog()
        # Show the new dialog
        suitability_dialog.exec_()
        values = suitability_dialog.get_table_values()
        print("User entered values:", values)

    def get_criterion(self):
        data = []
        data.append(self.sites_selection_dialog.criteriaNumberOneFile.filePath())
        data.append(self.sites_selection_dialog.criteriaNumberTwoFile.filePath())
        data.append(self.sites_selection_dialog.criteriaNumberThreeFile.filePath())
        data.append(self.sites_selection_dialog.criteriaNumberFourFile.filePath())
        data.append(self.sites_selection_dialog.criteriaNumberFiveFile.filePath())
        data.append(self.sites_selection_dialog.criteriaNumberSixFile.filePath())
        return data

    def __get_data(self):
        # rasterasation:
        study_area = self.sites_selection_dialog.studyAreaShapeFile.filePath()
        xmin, xmax, ymin, ymax = get_extent(study_area)

        resolution = 28.38985503875978011
        output_dir = r'C:\Users\elbou\Documents\Master_siggr\sig_project\Integration of GIS and MCA for school site selection\school_project_SIG\rasterize'
        os.makedirs(output_dir, exist_ok=True)

        data = self.get_criterion()
        for shapefile in data:
            base_name = os.path.basename(shapefile).replace('.shp', '.tif')
            output_path = os.path.join(output_dir, base_name)
            # rasterize 
            shapefile_to_raster(shapefile, output_path, xmin, xmax, ymin, ymax, resolution)
        
        # applaying the proximity
        proximity_dir = r'C:\Users\elbou\Documents\Master_siggr\sig_project\Integration of GIS and MCA for school site selection\school_project_SIG\proxymity'
        os.makedirs(proximity_dir, exist_ok=True)

        data = get_full_file_paths(output_dir)

        for raster in data:
            base_name = os.path.basename(raster)
            proximity_path = os.path.join(proximity_dir, "prox_" + base_name)
            # Calculate proximity
            calculate_proximity(raster, proximity_path)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&site selection'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False

        # show the dialog
        self.sites_selection_dialog.show()
        # Run the dialog event loop
        result = self.sites_selection_dialog.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
