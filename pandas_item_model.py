from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class PandasItemModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._data = data

    def index(self, row, column, parent=None):
        return self.createIndex(row, column, None)

    def parent(self, index=None):
        return QtCore.QModelIndex()

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                try:
                    return self._data.columns[section]
                except IndexError:
                    pass

    def sort(self, column, sort_order):
        ascending = sort_order == Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._data, index_order = sort_dataframe(self._data, ascending, column)
        indexes_after = [
            self.index(r, i)
            for r in range(self.rowCount())
            for i in range(self.columnCount())
        ]
        indexes_before = [
            self.index(r, i) for r in index_order for i in range(self.columnCount())
        ]
        self.changePersistentIndexList(indexes_before, indexes_after)
        self.layoutChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
            if role == Qt.UserRole:
                return self._data.index[index.row()]

    def index_from_pd_index(self, pd_index):
        row = self._data.index.get_loc(pd_index)
        return self.index(row, 0)


def sort_dataframe(df, ascending, column):
    rows = len(df.values)
    temp_df = df.copy()
    temp_df["_sort_values"] = range(rows)
    temp_df.sort_values(df.columns[column], ascending=ascending, inplace=True)
    index_order = temp_df["_sort_values"].values
    df = temp_df.drop(columns=["_sort_values"])
    return df, index_order
