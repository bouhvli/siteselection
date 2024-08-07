import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'suitability_value.ui'))


class SuitabilityValueDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SuitabilityValueDialog, self).__init__(parent)
        self.setupUi(self)
    
    def get_table_values(self):
        values = []
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                row_data.append(item.text() if item is not None else '')
            values.append(row_data)
        return values