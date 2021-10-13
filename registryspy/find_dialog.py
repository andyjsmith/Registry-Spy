import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets

import helpers


class FindDialog(QtWidgets.QDialog):
    def __init__(self, *args):
        super().__init__(*args)

        self.setWindowTitle("Find")
        self.resize(400, 200)

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
        self.buttonBox.accepted.connect(self.find)

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

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(text_group)
        self.layout.addWidget(category_group)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # Override showEvent to highlight the textbox on show
    def showEvent(self, event):
        self.text.setFocus()
        super().showEvent(event)

    def find(self):
        self.close()
        self.accept()

    def closed(self):
        self.close()
        self.reject()
