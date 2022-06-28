import os
from view_factory import ViewFactory
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGridLayout, QDockWidget, QLabel

# Camera Images
IMAGE_FORMAT = "png"
IMAGE_FOLDER = "test_data/"


class TableSelection:
    def __init__(self, main_window):
        self.main_window = main_window
        self._connect_signals()
        self.table_factory = TableWidget(self.main_window)
        self.widget_name = "Table"
        self.table_widget = None
        self.image_information = None

    def create_table_widget(self):
        self.table_widget = self.table_factory.createGraph(self.widget_name)
        self.image_information = self.table_factory.image_info
        self.show()

    def show(self, image_path=None):
        if self.table_widget is None:
            return

        self.image_information.setText(f"{image_path}")
        self.pixmap = QPixmap(image_path)
        self.pixmap = self.pixmap.scaled(750, 750, QtCore.Qt.KeepAspectRatio)
        self.table_widget.setPixmap(self.pixmap)
        self.table_widget.show()

    def _connect_signals(self):
        self.main_window.ui.action_show_table.triggered.connect(
            self.create_table_widget
        )


class TableDockWidget(QDockWidget):
    def __init__(self, graph_name, graph_widgets):
        QDockWidget.__init__(self)
        self.graph_widgets = graph_widgets
        self.graph_name = graph_name

        self.setObjectName(self.graph_name)
        self.setWindowTitle(self.graph_name)

    def closeEvent(self, event):
        if self.graph_name is not None:
            self.graph_widgets[self.graph_name].close()
            del self.graph_widgets[self.graph_name]


class TableWidget(ViewFactory):
    def __init__(self, main_window):
        ViewFactory.__init__(self)
        self.main_window = main_window
        self._image_info = None

    @property
    def image_info(self):
        """
        Image information label
        """
        return self._image_info

    def createGraph(self, view_name):

        if view_name not in self.graph_widgets:
            table_dock = TableDockWidget(view_name, self.graph_widgets)
            table_dock.setWindowTitle(view_name)

            table_widget = QLabel(self.main_window)
            table_widget.setMinimumSize(1, 1)
            table_widget.setScaledContents(True)
            table_widget.setObjectName(view_name)
            table_widget.setAlignment(QtCore.Qt.AlignCenter)
            gridLayout = QGridLayout(table_widget)
            table_dock.setWidget(table_widget)

            self._image_info = QLabel("No images available!")
            self._image_info.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            self._image_info.setObjectName("No images available!")
            gridLayout.addWidget(self._image_info)

            self.main_window.addDockWidget(QtCore.Qt.DockWidgetArea(1), table_dock)
            self.main_window.ui.tabifyDockWidget(
                self.main_window.ui.hands_dock, table_dock
            )
            table_dock.show()
            table_dock.raise_()
            self.graph_widgets[view_name] = table_widget
        else:
            table_widget = self.graph_widgets[view_name]

        return table_widget
