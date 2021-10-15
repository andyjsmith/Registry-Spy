import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets
from Registry import Registry

import helpers
import key_tree


class FindDialog(QtWidgets.QDialog):
    def __init__(self, *args):
        super().__init__(*args)

        self.setWindowTitle("Find")
        self.resize(400, 200)
        self.setWindowFlags(QtCore.Qt.Dialog |
                            QtCore.Qt.MSWindowsFixedSizeDialogHint)

        text_group = QtWidgets.QGroupBox(self)
        text_group.setTitle("Search for")
        text_group_layout = QtWidgets.QVBoxLayout(self)
        text_group.setLayout(text_group_layout)
        self.text = QtWidgets.QLineEdit()
        self.text.setClearButtonEnabled(True)
        text_group_layout.addWidget(self.text)

        find_btn = QtWidgets.QPushButton("Find Next")
        find_btn.setDefault(True)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton(
            find_btn, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.addButton(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.rejected.connect(self.closed)
        self.buttonBox.accepted.connect(self.handle_find)

        options_container = QtWidgets.QWidget()
        options_container_layout = QtWidgets.QHBoxLayout()
        options_container.setLayout(options_container_layout)

        category_group = QtWidgets.QGroupBox(self)
        category_group.setTitle("Search in")
        category_group_layout = QtWidgets.QVBoxLayout(category_group)

        key_category = QtWidgets.QCheckBox("Keys", self)
        key_category.setChecked(True)
        value_category = QtWidgets.QCheckBox("Values", self)
        value_category.setChecked(True)
        data_category = QtWidgets.QCheckBox("Data", self)
        data_category.setChecked(True)

        category_group_layout.addWidget(key_category)
        category_group_layout.addWidget(value_category)
        category_group_layout.addWidget(data_category)
        category_group_layout.addStretch()
        options_container_layout.addWidget(category_group)

        options_group = QtWidgets.QGroupBox(self)
        options_group.setTitle("Options")
        options_group_layout = QtWidgets.QVBoxLayout(options_group)

        self.case_sensitive = QtWidgets.QCheckBox("Case Sensitive", self)
        self.exact_match = QtWidgets.QCheckBox("Exact Match", self)

        options_group_layout.addWidget(self.case_sensitive)
        options_group_layout.addWidget(self.exact_match)
        options_group_layout.addStretch()
        options_container_layout.addWidget(options_group)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(text_group)
        self.layout.addWidget(options_container)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # Override showEvent to highlight the textbox on show
    def showEvent(self, event):
        self.text.setFocus()
        super().showEvent(event)

    def handle_find(self):
        active_key: key_tree.KeyItem = self.parent().tree.get_selected_key()
        if active_key is None:
            self.close()
            self.accept()
            helpers.show_message_box(
                "Select a key or hive first.", alert_type=helpers.MessageBoxTypes.CRITICAL)
            return

        if self.text.text() == "":
            helpers.show_message_box(
                "Enter a search term first.", alert_type=helpers.MessageBoxTypes.CRITICAL)
            return

        hive: Registry.Registry = self.parent().tree.reg[active_key.filename]
        key = hive.open(active_key.path)
        self.close()
        self.accept()

        self.parent().progress_bar.show()
        self.parent().progress_bar.setRange(0, 0)
        self.parent().progress_bar.setValue(0)
        result = self.find(key,
                           self.text.text(),
                           case_sensitive=self.case_sensitive.isChecked(),
                           exact_match=self.exact_match.isChecked())
        self.parent().progress_bar.setRange(0, 100)
        self.parent().progress_bar.hide()

        if result is None:
            self.parent().tree.select_key_from_path("")
            helpers.show_message_box(
                "Term not found. Looping back to start.", alert_type=helpers.MessageBoxTypes.WARNING)
            return
        sanitized_path = self.parent().tree.parse_uri(result, root=hive.root().name())
        self.parent().tree.select_key_from_path(sanitized_path)

    def find(self, starting_key: Registry.RegistryKey, term: str, case_sensitive=False, exact_match=False) -> str:
        """Find the next matching subkey or value"""

        if not case_sensitive:
            term = term.upper()

        def check_match(subkey: Registry.RegistryKey) -> bool:
            """Check if a subkey matches the search term"""
            if case_sensitive:
                subkey_name = subkey.name()
            else:
                subkey_name = subkey.name().upper()
            if exact_match:
                if term == subkey_name:
                    return True
            else:
                if term in subkey_name:
                    return True

            return False

        def search(start_key: Registry.RegistryKey, term: str):
            for subkey in start_key.subkeys():
                if check_match(subkey):
                    return subkey.path()
                result = search(subkey, term)
                if result is not None:
                    return result
            return None

        match = search(starting_key, term)
        if match is not None:
            return match

        current_key = starting_key
        try:
            while current_key.parent():
                subkeys = current_key.parent().subkeys()
                index = next((i for i, subkey in enumerate(subkeys)
                             if subkey.name() == current_key.name()))
                subkeys = subkeys[index+1:]
                for subkey in subkeys:
                    if check_match(subkey):
                        return subkey.path()
                    result = search(subkey, term)
                    if result is not None:
                        return result
                current_key = current_key.parent()
        except Registry.RegistryKeyHasNoParentException:
            pass

        return None

    def closed(self):
        self.close()
        self.reject()
