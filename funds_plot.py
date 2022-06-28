from view_factory import ViewFactory
from pyqtgraph import PlotWidget, mkPen
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDockWidget

# Camera Images
IMAGE_FORMAT = "png"
IMAGE_FOLDER = "test_data/"


class FundsPlotterSelection:
    def __init__(self, main_window):
        self.main_window = main_window
        self._connect_signals()
        self.funds_plotter = FundsPlotterWidget(self.main_window)
        self.widget_name = "Funds Plotter"
        self.funds_plotter_widget = None
        self.image_information = None

    def create_funds_plotter_widget(self):
        self.funds_plotter_widget = self.funds_plotter.createGraph(self.widget_name)
        self.plot()

    def plot(self, image_path=None):
        if self.funds_plotter_widget is None:
            return

        self.funds_plotter_widget.plot(
            self.main_window.image_info_df.index.get_level_values("ts"),
            self.main_window.image_info_df.amount,
            pen=mkPen(color=(255, 0, 0)),
        )

    def _connect_signals(self):
        self.main_window.ui.action_plot_funds.triggered.connect(
            self.create_funds_plotter_widget
        )


class FundsPlotterDockWidget(QDockWidget):
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


class FundsPlotterWidget(ViewFactory):
    def __init__(self, main_window):
        ViewFactory.__init__(main_window)
        self.main_window = main_window

    def createGraph(self, view_name):

        if view_name not in self.graph_widgets:
            funds_plotter_dock = FundsPlotterDockWidget(view_name, self.graph_widgets)
            funds_plotter_dock.setWindowTitle(view_name)
            funds_plotter_widget = PlotWidget()
            funds_plotter_dock.setWidget(funds_plotter_widget)
            self.main_window.addDockWidget(
                QtCore.Qt.DockWidgetArea(1), funds_plotter_dock
            )
            self.main_window.ui.tabifyDockWidget(
                self.main_window.ui.hands_dock, funds_plotter_dock
            )
            funds_plotter_dock.show()
            funds_plotter_dock.raise_()
            self.graph_widgets[view_name] = funds_plotter_widget
        else:
            funds_plotter_widget = self.graph_widgets[view_name]

        return funds_plotter_widget
