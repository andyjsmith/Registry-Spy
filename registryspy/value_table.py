import struct

from Registry import Registry
import PySide6.QtWidgets as QtWidgets
import PySide6.QtGui as QtGui
import PySide6.QtCore as QtCore

from . import helpers


class ValueData(QtWidgets.QTableWidgetItem):
    def __init__(self, raw_data: bytes, value, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raw_data = raw_data
        self.value = value


class ValueTable(QtWidgets.QTableWidget):
    """Value table that shows the values of the selected registry key"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Name", "Type", "Data"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 120)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.data = None
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.resizeRowsToContents()
        self.setAutoScroll(False)
        self.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setWordWrap(False)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.selectionModel().selectionChanged.connect(self.handle_selection_change)

        self.REG_BIN_ICON = QtGui.QIcon(
            helpers.resource_path("img/reg_bin.png"))
        self.REG_NUM_ICON = QtGui.QIcon(
            helpers.resource_path("img/reg_num.png"))
        self.REG_STR_ICON = QtGui.QIcon(
            helpers.resource_path("img/reg_str.png"))

    def handle_selection_change(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        if len(selected.indexes()) < 1:
            return

        index = selected.indexes()[2]

        value: ValueData = self.itemFromIndex(index)
        self.window().data_viewer.set_value(value.raw_data)

    def set_data(self, reg_values: "list[Registry.RegistryValue]"):
        self.clearContents()
        self.setRowCount(0)
        self.window().data_viewer.set_value(b"")

        for value in reg_values:
            index = self.rowCount()
            self.insertRow(index)
            value_name = QtWidgets.QTableWidgetItem(value.name())
            value_name.setFlags(value_name.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
            value_name.setIcon(self.get_icon(value.value_type()))
            value_type = QtWidgets.QTableWidgetItem(
                self.reg_type_to_str(value.value_type()))
            value_type.setFlags(value_type.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
            value_data = ValueData(value.raw_data(), value.value(), self.reg_data_to_str(
                value.value_type(), value.raw_data(), value.value()))
            if len(value.raw_data()) == 0:
                font = QtGui.QFont()
                font.setItalic(True)
                value_data.setFont(font)
            value_data.setFlags(value_data.flags() & ~
                                QtCore.Qt.ItemFlag.ItemIsEditable)
            self.setItem(index, 0, value_name)
            self.setItem(index, 1, value_type)
            self.setItem(index, 2, value_data)

        self.resizeRowsToContents()

    def get_icon(self, datatype: int) -> QtGui.QIcon:
        if datatype == Registry.RegBin:
            return self.REG_BIN_ICON
        if datatype == Registry.RegDWord:
            return self.REG_NUM_ICON
        if datatype == Registry.RegQWord:
            return self.REG_NUM_ICON
        if datatype == Registry.RegBigEndian:
            return self.REG_NUM_ICON
        if datatype == Registry.RegExpandSZ:
            return self.REG_STR_ICON
        if datatype == Registry.RegLink:
            return self.REG_STR_ICON
        if datatype == Registry.RegMultiSZ:
            return self.REG_STR_ICON
        if datatype == Registry.RegNone:
            return self.REG_NUM_ICON
        if datatype == Registry.RegResourceList:
            return self.REG_STR_ICON
        if datatype == Registry.RegSZ:
            return self.REG_STR_ICON
        return self.REG_BIN_ICON

    def reg_type_to_str(self, datatype: int) -> str:
        if datatype == Registry.RegBin:
            return "REG_BINARY"
        if datatype == Registry.RegDWord:
            return "REG_DWORD"
        if datatype == Registry.RegQWord:
            return "REG_QWORD"
        if datatype == Registry.RegBigEndian:
            return "REG_DWORD_BIG_ENDIAN"
        if datatype == Registry.RegExpandSZ:
            return "REG_EXPAND_SZ"
        if datatype == Registry.RegLink:
            return "REG_LINK"
        if datatype == Registry.RegMultiSZ:
            return "REG_MULTI_SZ"
        if datatype == Registry.RegNone:
            return "REG_NONE"
        if datatype == Registry.RegResourceList:
            return "REG_RESOURCE_LIST"
        if datatype == Registry.RegSZ:
            return "REG_SZ"
        return "UNKNOWN"

    def reg_data_to_str(self, datatype: int, raw_data: bytes, value) -> str:
        if len(raw_data) == 0:
            return "(value not set)"
        if datatype == Registry.RegDWord:
            try:
                return "{0:#010x} ({0})".format(value)
            except (struct.error, IndexError):
                pass
        if datatype == Registry.RegQWord:
            try:
                return "{0:#018x} ({0})".format(value)
            except (struct.error, IndexError):
                pass
        if datatype == Registry.RegBigEndian:
            try:
                return "{0:#010x} ({0})".format(value)
            except (struct.error, IndexError):
                pass
        if datatype == Registry.RegLink:
            # Not sure what format this will actually be
            return str(value)
        if datatype == Registry.RegMultiSZ:
            return " ".join(value)
        if datatype == Registry.RegResourceList:
            # Not sure what format this will actually be
            return str(value)
        if datatype == Registry.RegSZ or datatype == Registry.RegExpandSZ:
            return value
        else:
            return " ".join(["{:02x}".format(x) for x in raw_data])

    def select_value(self, value: str):
        for i in range(self.rowCount()):
            if (value == self.item(i, 0).text()):
                self.clearSelection()
                self.selectRow(i)
                self.scrollToItem(self.item(i, 0))
                self.setFocus()

    def get_selected_row(self):
        if len(self.selectedItems()) > 0:
            return self.selectedItems()[0].row()
        else:
            return -1
