import sys

import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

import value_table
import key_tree
import hive_info_table
import license_dialog
import find_dialog
import helpers


# Set the app ID on windows (helps with making sure icon is used)
try:
    import ctypes
    appid = "ajsmith.registryspy.desktop.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
except (AttributeError, OSError):
    pass


class RegViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up main window
        self.setWindowTitle(helpers.APP_NAME)
        self.resize(1200, 700)

        self.tree = key_tree.KeyTree(self)
        self.find_dialog = find_dialog.FindDialog(self)

        # Set up file menu
        file_menu = QtWidgets.QMenu("&File", self)
        open_action = QtGui.QAction("Open Hive", self)
        open_action.setShortcut(QtGui.QKeySequence.Open)
        open_action.triggered.connect(self.show_open_file)
        file_menu.addAction(open_action)
        close_action = QtGui.QAction("Close Selected Hive", self)
        close_action.setShortcut(QtGui.QKeySequence(
            QtCore.Qt.SHIFT | QtCore.Qt.Key_Delete))
        close_action.triggered.connect(self.tree.remove_selected_hive)
        file_menu.addAction(close_action)
        close_all_action = QtGui.QAction("Close All Hives", self)
        close_all_action.setShortcut(QtGui.QKeySequence(
            QtCore.Qt.CTRL | QtCore.Qt.SHIFT | QtCore.Qt.Key_Delete))
        close_all_action.triggered.connect(self.tree.remove_all_hives)
        file_menu.addAction(close_all_action)
        file_menu.addSeparator()
        quit_action = QtGui.QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        self.menuBar().addMenu(file_menu)

        # Set up find menu
        find_menu = QtWidgets.QMenu("Fin&d", self)
        find_action = QtGui.QAction("Find...", self)
        find_action.setShortcut(QtGui.QKeySequence.Find)
        find_action.triggered.connect(self.show_find)
        find_menu.addAction(find_action)
        find_next_action = QtGui.QAction("Find Next", self)
        find_next_action.setShortcut(QtGui.QKeySequence.FindNext)
        find_next_action.triggered.connect(self.find_dialog.handle_find)
        find_menu.addAction(find_next_action)
        find_previous_action = QtGui.QAction("Find Previous", self)
        find_previous_action.setShortcut(QtGui.QKeySequence.FindPrevious)
        find_menu.addAction(find_previous_action)
        self.menuBar().addMenu(find_menu)

        # Set up view menu
        view_menu = QtWidgets.QMenu("&View", self)
        self.native_style_action = QtGui.QAction("Use native style", self)
        self.native_style_action.setCheckable(True)
        self.native_style_action.toggled.connect(self.toggle_style)
        view_menu.addAction(self.native_style_action)
        self.menuBar().addMenu(view_menu)

        # Set up help menu
        help_menu = QtWidgets.QMenu("&Help", self)
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        licenses_action = QtGui.QAction("Third-Party Licenses", self)
        licenses_action.triggered.connect(self.show_licenses)
        help_menu.addAction(licenses_action)
        self.menuBar().addMenu(help_menu)

        self.menuBar().setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        self.statusBar()

        # Set up toolbar
        toolbar = QtWidgets.QToolBar("Main", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.toggleViewAction().setEnabled(False)
        toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        open_action = QtGui.QAction(
            QtGui.QIcon(helpers.resource_path("img/open.png")), "Open Hive", toolbar)
        open_action.triggered.connect(self.show_open_file)
        toolbar.addAction(open_action)
        close_action = QtGui.QAction(
            QtGui.QIcon(helpers.resource_path("img/close.png")), "Close Selected Hive", toolbar)
        close_action.triggered.connect(self.tree.remove_selected_hive)
        toolbar.addAction(close_action)
        close_all_action = QtGui.QAction(
            QtGui.QIcon(helpers.resource_path("img/close_all.png")), "Close All Hives", toolbar)
        close_all_action.triggered.connect(self.tree.remove_all_hives)
        toolbar.addAction(close_all_action)
        find_action = QtGui.QAction(
            QtGui.QIcon(helpers.resource_path("img/find.png")), "Find", toolbar)
        find_action.triggered.connect(self.show_find)
        toolbar.addAction(find_action)
        find_next_action = QtGui.QAction(
            QtGui.QIcon(helpers.resource_path("img/find_next.png")), "Find Next", toolbar)
        find_next_action.triggered.connect(self.find_dialog.handle_find)
        toolbar.addAction(find_next_action)
        self.addToolBar(toolbar)

        # Set up main layout
        main_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)

        self.value_table = value_table.ValueTable(main_widget)

        self.uri_textbox = QtWidgets.QLineEdit(main_widget)
        self.uri_textbox.returnPressed.connect(self.tree.handle_uri_change)
        main_layout.addWidget(self.uri_textbox)

        self.statusBar().setStyleSheet(
            "QStatusBar QLabel { border-color: lightgray; border-style: solid; border-width: 0 1px 0 0; }")

        tree_container = QtWidgets.QWidget()
        tree_container_layout = QtWidgets.QVBoxLayout(tree_container)
        tree_container_layout.setContentsMargins(0, 0, 0, 0)
        tree_container.setLayout(tree_container_layout)

        tree_container_layout.addWidget(self.tree)
        self.tree.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.hive_info = hive_info_table.HiveInfoTable(tree_container)
        hive_geometry = self.hive_info.geometry()
        hive_geometry.setHeight(5)
        self.hive_info.setGeometry(hive_geometry)
        self.hive_info.setMinimumHeight(10)
        self.hive_info.setSizeAdjustPolicy(
            self.hive_info.SizeAdjustPolicy.AdjustToContents)
        tree_container_layout.addWidget(self.hive_info)

        value_splitter = QtWidgets.QSplitter(
            QtGui.Qt.Orientation.Vertical)
        value_splitter.addWidget(self.value_table)
        self.value_hex = QtWidgets.QPlainTextEdit()
        mono_font = QtGui.QFont()
        mono_font.setFamilies(["Courier New", "Monospaced"])
        mono_font.setStyleHint(QtGui.QFont.Monospace)
        self.value_hex.setFont(mono_font)
        self.value_hex.setLineWrapMode(self.value_hex.LineWrapMode.NoWrap)
        value_splitter.addWidget(self.value_hex)
        value_splitter.setStretchFactor(0, 2)
        value_splitter.setStretchFactor(1, 1)

        main_splitter = QtWidgets.QSplitter(main_widget)
        main_splitter.addWidget(tree_container)
        main_splitter.addWidget(value_splitter)
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 5)
        main_splitter.setChildrenCollapsible(False)
        main_layout.addWidget(main_splitter)
        self.setCentralWidget(main_widget)

        self.progress_bar = QtWidgets.QProgressBar(self.statusBar())
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.hide()
        self.statusBar().addPermanentWidget(self.progress_bar)

    def show_about(self):
        QtWidgets.QMessageBox().about(
            self, f"About {helpers.APP_NAME}", helpers.ABOUT_TEXT)

    def show_licenses(self):
        license = license_dialog.LicenseDialog(self)
        license.exec()

    def show_find(self):
        self.find_dialog.exec()

    def show_open_file(self):
        """Show the open file dialog"""
        file_selection = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Open Registry File")

        self.statusBar().showMessage("Loading...")
        self.statusBar().repaint()

        if isinstance(file_selection, tuple) and len(file_selection) > 0 and len(file_selection[0]) > 0:
            for file in file_selection[0]:
                self.open_file(file)

        self.statusBar().clearMessage()

    def open_file(self, filename: str):
        self.tree.load_hive(filename)

    def toggle_style(self):
        if self.native_style_action.isChecked():
            app.setStyle(initial_style)
        else:
            app.setStyle("fusion")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    initial_style = app.style().name()
    app.setStyle("fusion")

    # f = QtCore.QFile("qdarkstyle/dark/style.qss")
    # f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    # qss = QtCore.QTextStream(f)
    # app.setStyleSheet(qss.readAll())

    # Dark Mode
    # https://github.com/mguludag/QEasySettings/blob/main/qeasysettings.cpp
    # palette = QtGui.QPalette()
    # palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    # palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    # palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    # palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    # palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.Text, QtGui.QColor(164, 166, 168))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.WindowText, QtGui.QColor(164, 166, 168))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.ButtonText, QtGui.QColor(164, 166, 168))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.HighlightedText, QtGui.QColor(164, 166, 168))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.Base, QtGui.QColor(68, 68, 68))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.Window, QtGui.QColor(68, 68, 68))
    # palette.setColor(QtGui.QPalette.Disabled,
    #                  QtGui.QPalette.Highlight, QtGui.QColor(68, 68, 68))
    # app.setPalette(palette)

    reg_viewer = RegViewer()

    app.setWindowIcon(QtGui.QIcon(helpers.resource_path("img/icon.ico")))

    reg_viewer.show()

    # Close the splash screen
    try:
        import pyi_splash  # type: ignore
        pyi_splash.close()
    except ImportError:
        pass

    # Process command-line file(s)
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            reg_viewer.open_file(filename)

    sys.exit(app.exec())
