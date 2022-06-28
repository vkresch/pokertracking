import pandas as pd


class PokerData:
    def __init__(self):
        self._current_selection = None
        self._funds = None
        self._history = self.client["poker_history"]
        self._tables = self._history["poker_tables"]

    @property
    def tables(self):
        return self._tables

    @property
    def current_selection(self):
        return self._current_selection

    @current_selection.setter
    def current_selection(self, value):
        self._current_selection = value

    @property
    def funds(self):
        result = self._tables.find({"real_money": "real"}, {"ts": 1, "my_fund": 1})
        self._funds = pd.DataFrame(result).sort_values(by="ts", ascending=True)
        return self._funds
