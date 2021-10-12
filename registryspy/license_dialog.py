import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets

import helpers


class LicenseDialog(QtWidgets.QDialog):
    def __init__(self, *args):
        super().__init__(*args)

        self.setWindowTitle("Third-Party Licenses")
        self.resize(550, 400)

        text = QtWidgets.QPlainTextEdit()
        text.setReadOnly(True)
        text_file = QtCore.QFile(
            helpers.resource_path("third_party_licenses.txt"))
        if not text_file.open(QtCore.QIODevice.ReadOnly):
            print(text_file.errorString())

        stream = QtCore.QTextStream(text_file)
        text.setPlainText(stream.readAll())

        QBtn = QtWidgets.QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(text)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
