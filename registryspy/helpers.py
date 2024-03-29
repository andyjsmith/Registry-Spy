import os
import sys
import string

import PySide6.QtWidgets as QtWidgets


APP_NAME = "Registry Spy"
VERSION = (1, 1, 0)
ORGANIZATION_NAME = "Andy Smith"
ORGANIZATION_DOMAIN = "ajsmith.org"
ABOUT_TEXT = f"""\
{APP_NAME}
{".".join(str(i) for i in VERSION)}
Copyright (C) 2023 Andy Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def bytes_to_printable(b: bytes, encoding="windows-1252") -> str:
    """Convert bytes to string, replacing control and non-printable chars"""
    decoded = b.decode(encoding, "replace")
    # Replace the unicode replacement character
    decoded = decoded.replace("\uFFFD", ".")
    # Replace control characters
    banned = "".join([chr(i) for i in range(0x20)] + ["\x7f", "\xa0", "\xad"])
    decoded = "".join([c if c not in banned else "." for c in decoded])
    return decoded


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)


class MessageBoxTypes:
    INFORMATION = (QtWidgets.QMessageBox.Information, "Information")
    WARNING = (QtWidgets.QMessageBox.Warning, "Warning")
    CRITICAL = (QtWidgets.QMessageBox.Critical, "Error")
    QUESTION = (QtWidgets.QMessageBox.Question, "Question")


def show_message_box(text, alert_type=MessageBoxTypes.INFORMATION, title=None):
    msgbox = QtWidgets.QMessageBox()
    if title is None:
        msgbox.setWindowTitle(alert_type[1])
    msgbox.setText(text)
    msgbox.setIcon(alert_type[0])
    return msgbox.exec()
