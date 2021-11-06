import enum

import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets
from Registry import Registry

from . import helpers
from . import key_tree


class ResultType(enum.Enum):
    KEY = 0
    VALUE = 1
    DATA = 2


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
        self.text.setToolTip(
            "For binary data, enter it in hexadecimal with spaces between bytes. E.g. 0A 54 D3")
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

        self.key_search = QtWidgets.QCheckBox("Keys", self)
        self.key_search.setChecked(True)
        self.value_search = QtWidgets.QCheckBox("Values", self)
        self.value_search.setChecked(True)
        self.data_search = QtWidgets.QCheckBox("Data", self)
        self.data_search.setChecked(True)

        category_group_layout.addWidget(self.key_search)
        category_group_layout.addWidget(self.value_search)
        category_group_layout.addWidget(self.data_search)
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
        if self.text.text() == "":
            helpers.show_message_box(
                "Enter a search term first.", alert_type=helpers.MessageBoxTypes.CRITICAL)
            return

        if not (self.key_search.isChecked() or self.value_search.isChecked() or self.data_search.isChecked()):
            helpers.show_message_box(
                "You must select one type to search in.", alert_type=helpers.MessageBoxTypes.CRITICAL)
            return

        self.close()
        self.accept()

        if active_key is None:
            helpers.show_message_box(
                "Select a key or hive first.", alert_type=helpers.MessageBoxTypes.CRITICAL)
            return

        hive: Registry.Registry = self.parent().tree.reg[active_key.filename]
        current_key = hive.open(active_key.path)

        self.parent().progress_bar.show()
        self.parent().progress_bar.setRange(0, 0)
        self.parent().progress_bar.setValue(1)
        self.parent().progress_bar.setValue(0)
        result = self.find(current_key,
                           self.text.text(),
                           case_sensitive=self.case_sensitive.isChecked(),
                           exact_match=self.exact_match.isChecked(),
                           search_keys=self.key_search.isChecked(),
                           search_values=self.value_search.isChecked(),
                           search_data=self.data_search.isChecked())
        self.parent().progress_bar.setRange(0, 100)
        self.parent().progress_bar.hide()

        if result is None:
            self.parent().tree.select_key_from_path("")
            helpers.show_message_box(
                "Term not found. Looping back to start.", alert_type=helpers.MessageBoxTypes.WARNING)
            return

        result_type, result_key, result_value = result
        sanitized_path = self.parent().tree.parse_uri(
            result_key, root=hive.root().name())
        self.parent().tree.select_key_from_path(sanitized_path)
        if result_type == ResultType.VALUE or result_type == ResultType.DATA:
            self.parent().value_table.select_value(result_value)

    def find(self, starting_key: Registry.RegistryKey, term: str, case_sensitive=False, exact_match=False, search_keys=True, search_values=True, search_data=True, reverse=False) -> "tuple[ResultType, str, str]":
        """Find the next matching subkey or value. Returns (ResultType, key, value)"""

        if not case_sensitive:
            term = term.upper()

        def check_match(text: str) -> bool:
            """Check if a subkey matches the search term"""
            if not case_sensitive:
                text = text.upper()
            if exact_match:
                if term == text:
                    return True
            else:
                if term in text:
                    return True

            return False

        def search(start_key: Registry.RegistryKey, term: str, start_at_value=0, skip_start_key_name=False) -> tuple[ResultType, str, str]:
            """Returns (ResultType, key, value)"""

            # Check the start key name if asked (i.e. if the search has just started)
            if search_keys and not skip_start_key_name:
                if check_match(start_key.name()):
                    return ResultType.KEY, start_key.path(), None

            values = start_key.values()[start_at_value:]
            # Skip extra looping if values and data are not searched for
            if search_values or search_data:
                for value in values:
                    # Check through the value
                    if search_values and check_match(value.name()):
                        return ResultType.VALUE, start_key.path(), value.name()
                    # Check through the value's data
                    if search_data and (
                            check_match(str(value.value())) or
                            check_match(self.parent().value_table.reg_data_to_str(value.value_type(), value.raw_data(), value.value()))):
                        return ResultType.DATA, start_key.path(), value.name()

            # Recurse through the subkeys
            for subkey in start_key.subkeys():
                # Check subkey name
                if search_keys and check_match(subkey.name()):
                    return ResultType.KEY, subkey.path(), None
                result = search(subkey, term)
                if result is not None:
                    # Found a recursive match!
                    return result

            # No match was found
            return None

        match = search(starting_key, term,
                       start_at_value=self.parent().value_table.get_selected_row() + 1, skip_start_key_name=True)
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
