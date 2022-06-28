import signal
import sys
import glob
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
from PyQt5.QtCore import Qt

from logger import Logger
import pandas as pd
from pandas_item_model import PandasItemModel

# from data_wrapper import PokerData
from hands_filter import HandsFilter
from table_widget import TableSelection
from funds_plot import FundsPlotterSelection

POCKER_TRACKER_UI = "pokertracking.ui"
PNG_FILTER = "PNG files (*.png)"
IMAGE_INFO_NAMES = [
    "session",
    "ts",
    "real_money",
    "player_count",
    "big_blind",
    "pocket_cards",
    "stage",
    "community_cards",
    "active_players",
    "total_pot",
    "action",
    "amount",
    "image_format",
    "date_time",
    "image_path",
]

signal.signal(signal.SIGINT, signal.SIG_DFL)


class PokerTracking(QMainWindow):
    background_thread_signal = pyqtSignal()
    hands_table_update_signal = pyqtSignal(
        pd.DataFrame, name="hands_table_update_signal"
    )

    def __init__(self):
        super(PokerTracking, self).__init__()

        self.hands_table_update_signal.connect(self.update_hands_table)
        self.backgroundthread = None
        # self.poker_data = PokerData()
        self.image_info_df = None
        self.logger = Logger(__class__.__name__, self, min_level="debug")
        self._connect_signals()

    def update_hands_table(self, hands):
        self.ui.hands_tableview.setModel(PandasItemModel(hands))
        self.ui.hands_tableview.selectionModel().selectionChanged.connect(
            self.hands_table_selection
        )

    def import_data(self):
        folder_data_path = str(
            QFileDialog.getExistingDirectory(self, "Select Directory")
        )
        if not folder_data_path:
            return
        self.load_data_png(folder_data_path)

    def get_image_info(self, image_path):
        image_name = image_path.split("/")[-1]
        image_info_list = image_name.split("_")
        date_time = datetime.utcfromtimestamp(int(image_info_list[1])).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        image_info_list = image_info_list + [date_time, image_path]
        assert len(image_info_list) == len(IMAGE_INFO_NAMES), self.logger.error(
            f"List Length are not equal for {image_path}!"
        )
        image_info_dict = dict(zip(IMAGE_INFO_NAMES, image_info_list))
        return image_info_dict

    def _cast_df(self, df):
        df[
            ["ts", "player_count", "active_players", "total_pot", "amount", "big_blind"]
        ] = df[
            ["ts", "player_count", "active_players", "total_pot", "amount", "big_blind"]
        ].apply(
            pd.to_numeric
        )
        return df

    def load_data_png(self, folder_path):
        self.logger.debug(f"Loading data: {folder_path}")
        image_paths = glob.glob(f"{folder_path}/*.png")
        self.image_info_df = pd.DataFrame(map(self.get_image_info, image_paths))
        self.image_info_df = self._cast_df(self.image_info_df)
        self.image_info_df["amount"] = self.image_info_df["amount"].fillna(0)
        self.image_info_df = self.image_info_df.sort_values(by="ts", ascending=False)
        self.image_info_df = self.image_info_df.set_index(["session", "ts"])
        self.image_info_df["invested"] = (
            self.image_info_df["total_pot"] * self.image_info_df["amount"]
        )
        display_df = self.image_info_df.head(100)
        self.update_hands_table(display_df)
        self.logger.info(
            f"Displaying most recent {display_df.shape[0]} hands from total of {self.image_info_df.shape[0]} hands."
        )

    def hands_table_selection(self, selection=None, deselection=None):
        selection = self.ui.hands_tableview.selectionModel().selectedRows()[0]
        index_selection = selection.data(Qt.UserRole)
        self.logger.debug(f"Current index selected: {index_selection}")
        image_path_selected = self.image_info_df.loc[index_selection, "image_path"]
        self.table_selection.show(image_path_selected)

    def _connect_signals(self):
        self.ui = uic.loadUi(POCKER_TRACKER_UI)
        self.setCentralWidget(None)
        self.ui.action_load_data.triggered.connect(self.import_data)
        self.hands_filter = HandsFilter(self)
        self.table_selection = TableSelection(self)
        self.funds_plotter = FundsPlotterSelection(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pt = PokerTracking()
    pt.ui.show()
    sys.exit(app.exec_())
