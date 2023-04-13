import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

from . import helpers


class DataViewer(QtWidgets.QSplitter):
    """Viewer to preview data of the selected registry key entry."""

    def __init__(self):
        super().__init__(QtGui.Qt.Orientation.Horizontal)

        mono_font = QtGui.QFont()
        mono_font.setFamilies(["DejaVu Sans Mono", "Courier New", "Monospaced"])
        mono_font.setStyleHint(QtGui.QFont.Monospace)

        self.value_hex = self.add_data_viewer(mono_font)
        self.value_ascii = self.add_data_viewer(mono_font)

    def add_data_viewer(self, font: QtGui.QFont):
        """Create a data viewer widget and add it to this widget."""

        viewer = QtWidgets.QPlainTextEdit()
        viewer.setReadOnly(True)
        viewer.setFont(font)
        viewer.setLineWrapMode(viewer.LineWrapMode.NoWrap)
        self.addWidget(viewer)
        return viewer

    def set_value(self, bytes: bytes):
        """Set the value of all displayed viewers to the specified bytes."""

        self.value_hex.setPlainText("")
        self.value_ascii.setPlainText("")

        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        hex_text = ""
        ascii_text = ""

        for chunk in chunks(bytes, 16):
            hex_text += " ".join(["{:02x}".format(x) for x in chunk]) + "\n"

            # Decode text, replace control/non-printable characters
            decoded_text = helpers.bytes_to_printable(chunk)

            ascii_text += decoded_text + "\n"

        self.value_hex.setPlainText(hex_text)
        self.value_ascii.setPlainText(ascii_text)
