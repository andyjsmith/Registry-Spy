from Registry import Registry
import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets
import PySide6.QtGui as QtGui

import helpers


class KeyItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, path: str, filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.filename = filename


class KeyTree(QtWidgets.QTreeWidget):
    """Tree widget that displays registry keys"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.roots: dict[str, KeyItem] = {}
        self.reg: dict[str, Registry.Registry] = {}

        self.setColumnCount(3)
        self.setHeaderLabels(["Key", "Subkeys", "Modified"])
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.selectionModel().selectionChanged.connect(self.handle_selection_change)
        self.expanded.connect(self.handle_expand)
        self.collapsed.connect(self.handle_collapse)

        self.key_icon = QtGui.QIcon(
            helpers.resource_path("img/folder.png"))
        self.hive_icon = QtGui.QIcon(
            helpers.resource_path("img/icon.png"))

    def get_uri_textbox(self) -> QtWidgets.QLineEdit:
        """Returns the URI textbox from the main form"""
        return self.window().uri_textbox

    def get_selected_key(self) -> KeyItem:
        """Returns the selected key in the KeyTree"""
        selected = self.selectedItems()
        if len(selected) > 0:
            return selected[0]

    def get_selected_hive(self) -> KeyItem:
        """Returns the root KeyItem of the selected KeyItem"""
        key = self.get_selected_key()
        if key is None:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Error")
            msgbox.setText(
                "No key selected, select a key first.")
            msgbox.setIcon(QtWidgets.QMessageBox.Warning)
            msgbox.exec()
            return
        if self.roots.get(key.filename) is not None:
            return self.roots[key.filename]

    def remove_all_hives(self):
        """Unload all hives"""
        for root in list(self.roots.values()):
            self.remove_hive(root)

    def remove_selected_hive(self):
        """Unload the selected hive"""
        root = self.get_selected_hive()
        if root is None:
            return
        self.remove_hive(root)

    def remove_hive(self, root: KeyItem):
        """Unloads a hive specified by the provided root KeyItem"""
        self.window().hive_info.set_info("", "", "", "")

        filename = root.filename
        self.takeTopLevelItem(self.indexOfTopLevelItem(root))
        self.window().value_table.set_data([])
        self.get_uri_textbox().setText("")

        del self.roots[filename]
        del self.reg[filename]

    def load_hive(self, filename: str):
        """Load a registry hive from a file"""

        # Remove hive before loading another one
        if self.roots.get(filename) is not None:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Error")
            msgbox.setText(
                "Registry hive already open, close it first before opening again")
            msgbox.setIcon(QtWidgets.QMessageBox.Warning)
            msgbox.exec()
            return

        try:
            self.reg[filename] = Registry.Registry(filename)
        except Registry.RegistryParse.ParseException:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Error")
            msgbox.setText("Unable to parse registry file")
            msgbox.setIcon(QtWidgets.QMessageBox.Critical)
            msgbox.exec()
            return

        # Create new root KeyItem
        self.roots[filename] = KeyItem(
            "", filename, [f"{self.reg[filename].hive_type().name} ({filename})", str(self.reg[filename].root().subkeys_number()), self.reg[filename].root().timestamp().strftime("%Y-%m-%d %H:%M:%S")])

        self.roots[filename].setIcon(0, self.hive_icon)
        self.load_subkeys(self.roots[filename])

        self.indexOfTopLevelItem(self.roots[filename])
        self.insertTopLevelItems(0, [self.roots[filename]])

    def set_uri(self, index: QtCore.QModelIndex):
        """Set navbar full key path"""
        if isinstance(self.itemFromIndex(index), KeyItem):
            path = self.format_uri(self.itemFromIndex(index))
            self.get_uri_textbox().setText(path)

    def format_uri(self, key: KeyItem) -> str:
        """Format a URI path for the specified KeyItem"""
        if key.path == "":
            return self.reg[key.filename].hive_type().name
        else:
            return self.reg[key.filename].hive_type().name + "\\" + key.path

    def parse_uri(self, uri: str, hive_type: str) -> str:
        """Parses a user-specified URI into a registry path"""

        # Sanitize URI
        uri = uri.strip()
        uri = uri.strip("\\")
        uri = uri.replace(hive_type + "\\", "")
        uri = uri.strip("\\")

        if uri == "" or uri == hive_type:
            return ""

        return uri

    def remove_hive_prefix(self, root_name: str, path: str) -> str:
        prefix = root_name + "\\"
        return path.replace(prefix, "")

    def load_subkeys(self, key: KeyItem):
        for i in range(key.childCount()):
            key.removeChild(key.child(0))

        root_name = self.reg[key.filename].root().name()

        if key.childCount() > 1:
            return

        num_subkeys = self.reg[key.filename].open(key.path).subkeys_number()

        # Don't bother showing the progress bar if there aren't many items
        display_progressbar = num_subkeys > 20

        if display_progressbar:
            self.window().progress_bar.setMaximum(num_subkeys)
            self.window().progress_bar.setValue(0)
            self.window().progress_bar.show()
            i = 0

        for subkey in self.reg[key.filename].open(key.path).subkeys():
            if display_progressbar:
                # Process events once in a while so the application doesn't "stop responding" on Windows
                if i % 20 == 0:
                    self.window().progress_bar.setValue(i)
                # if i % 1000 == 0:
                #     QtCore.QCoreApplication.processEvents()
                # Removed for now because processEvents causes a TON of delay
                i += 1

            subkey_child = KeyItem(self.remove_hive_prefix(root_name, subkey.path()), key.filename, [
                                   subkey.name(), str(subkey.subkeys_number()), subkey.timestamp().strftime("%Y-%m-%d %H:%M:%S")])
            subkey_child.setIcon(0, self.key_icon)
            key.addChild(subkey_child)

            # Create a fake child so that the tree shows an arrow to drop down
            if subkey.subkeys_number() > 0:
                subkey_child.addChild(KeyItem("", ""))

            # for subsubkey in subkey.subkeys():
            #     subsubkey_child = KeyItem(
            #         self.remove_hive_prefix(root_name, subsubkey.path()), subkey_child.filename, [subsubkey.name()])
            #     subkey_child.addChild(subsubkey_child)

        if display_progressbar:
            self.window().progress_bar.hide()

    def select_key_from_path(self, path: str) -> KeyItem:
        """Find a KeyItem from a given path and highlight it"""
        parent = self.get_selected_hive()
        if parent is None:
            return
        levels = path.count("\\") + 1

        # Check if root is selected
        if path == parent.path:
            self.clearSelection()
            self.scrollToItem(parent)
            parent.setSelected(True)
            self.window().tree.setFocus()
            return

        for level in range(levels):
            # Expand parent
            parent.setExpanded(True)
            for c in range(parent.childCount()):
                subpath = "\\".join(path.split("\\")[:level+1])
                child_path = parent.child(c).path
                # Last level, should have match
                if child_path == subpath:
                    if level + 1 == levels:
                        # Found!
                        self.clearSelection()
                        self.scrollToItem(parent.child(c))
                        parent.child(c).setSelected(True)
                        self.window().tree.setFocus()
                        return parent.child(c)

                    # Set parent to new child
                    parent = parent.child(c)
                    break

    def handle_uri_change(self):
        root = self.get_selected_hive()
        if root is None:
            return

        # Get the new text
        uri: str = self.get_uri_textbox().text()
        parsed_uri = self.parse_uri(
            uri, self.reg[root.filename].hive_type().name)

        try:
            self.reg[root.filename].open(parsed_uri)
        except Registry.RegistryKeyNotFoundException:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Error")
            msgbox.setText(
                "Key was not found")
            msgbox.setIcon(QtWidgets.QMessageBox.Warning)
            msgbox.exec()
            return

        key = self.select_key_from_path(parsed_uri)

    def handle_selection_change(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        if len(selected.indexes()) < 1:
            return

        index = selected.indexes()[0]

        self.set_uri(index)

        key: KeyItem = self.itemFromIndex(index)

        self.window().hive_info.set_info(key.filename, self.reg[key.filename].hive_type(
        ).name, self.reg[key.filename].hive_name(), self.reg[key.filename].root().name())

        try:
            self.window().value_table.set_data(
                self.reg[key.filename].open(key.path).values())
        except Registry.RegistryKeyNotFoundException:
            self.window().value_table.set_data([])

    def handle_expand(self, index: QtCore.QModelIndex):
        self.window().statusBar().showMessage("Loading...")
        self.window().statusBar().repaint()
        self.setCursor(QtCore.Qt.CursorShape.BusyCursor)

        key = self.itemFromIndex(index)
        self.load_subkeys(key)

        self.window().statusBar().clearMessage()
        self.unsetCursor()

    def handle_collapse(self, index: QtCore.QModelIndex):
        key = self.itemFromIndex(index)
        for i in range(key.childCount()):
            key.removeChild(key.child(0))
        key.addChild(KeyItem("", ""))
