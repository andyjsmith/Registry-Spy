import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore


class HiveInfoTable(QtWidgets.QTableWidget):
    """Value table that shows the values of the selected registry key"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setParent(parent)
        self.setColumnCount(1)

        header_labels = ["Path", "Type", "Hive Name", "Root Name"]
        self.setRowCount(len(header_labels))
        self.setVerticalHeaderLabels(header_labels)

        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                           QtWidgets.QSizePolicy.Maximum)
        self.setMinimumHeight(0)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setVisible(False)
        self.resizeRowsToContents()
        self.setAutoScroll(False)
        self.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setWordWrap(False)
        self.verticalHeader().setSectionResizeMode(self.verticalHeader().Fixed)

        # Call so that the cells become uneditable
        self.set_info("", "", "", "")

    def set_info(self, hive_path, hive_type, hive_name, root_name):
        """Set the hive info table data"""

        hive_path_item = QtWidgets.QTableWidgetItem(hive_path)
        hive_path_item.setFlags(hive_path_item.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, 0, hive_path_item)

        hive_type_item = QtWidgets.QTableWidgetItem(hive_type)
        hive_type_item.setFlags(hive_type_item.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, 1, hive_type_item)

        hive_name_item = QtWidgets.QTableWidgetItem(hive_name)
        hive_name_item.setFlags(hive_name_item.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, 2, hive_name_item)

        root_name_item = QtWidgets.QTableWidgetItem(root_name)
        root_name_item.setFlags(root_name_item.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, 3, QtWidgets.QTableWidgetItem(root_name_item))
