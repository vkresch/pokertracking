from PyQt5 import QtCore, uic
import re

from logger import Logger

LABEL_FILTER_UI = "hands_filter.ui"
COMPARATORS = {
    "==": lambda df, col, row: df[col] == row,
    "!=": lambda df, col, row: df[col] != row,
    "<=": lambda df, col, row: df[col] <= row,
    ">=": lambda df, col, row: df[col] >= row,
    "<": lambda df, col, row: df[col] < row,
    ">": lambda df, col, row: df[col] > row,
}
COMPARATORS_LIST = list(COMPARATORS.keys())
LOGICAL_OPERATORS = {
    "&": lambda expr1, expr2: expr1 & expr2,
    "|": lambda expr1, expr2: expr1 | expr2,
}
LOGICAL_OPERATORS_LIST = list(LOGICAL_OPERATORS.keys())
LOGICAL_REGEX = "\&|\|"
COMPARATOR_REGEX = "\=\=|\!\=|\<\=|\>\=|\<|\>"
INVALID_CHARACTERS = [" ", "(", ")", "[", "]", "{", "}", '"']


class HandsFilter:
    def __init__(self, main_window):
        self.mw = main_window
        self.logger = Logger(__class__.__name__, self.mw, min_level="debug")
        # self.mw.ui.action_filter_hands.setDisabled(True)
        self.mw.ui.action_filter_hands.triggered.connect(self.popup_window)

    def popup_window(self):
        if not hasattr(self.mw, "hands_filter_ui"):
            self.mw.hands_filter_ui = uic.loadUi(LABEL_FILTER_UI)
        self._connect_signals()
        self.mw.hands_filter_ui.setWindowTitle("Hands Filter")
        self.mw.hands_filter_ui.show()

    def apply(self):
        filter_text = (
            self.mw.hands_filter_ui.filter_text.text()
            if hasattr(self.mw, "hands_filter_ui")
            else ""
        )
        new_hands_table = self.filter_hands_table(filter_text, self.mw.image_info_df)
        self.update_hands_table(new_hands_table)

    def _cast_row(self, column_name, row_name, df_types):
        if df_types[column_name] == "int64":
            row_name = int(row_name)
        elif df_types[column_name] == "float64":
            row_name = float(row_name)
        return row_name

    def _filter(self, data_frame, column_names, row_names, logical_list, comparators):

        if len(logical_list) == 0:
            logical_expression = COMPARATORS[comparators[0]](
                data_frame, column_names[0], row_names[0]
            )

        elif len(logical_list) >= 1:
            # TODO: Currently no paranthesis enclosing is supported
            # the evaluation goes from left to right, meaning
            # col1==row1 & col2==row2 | col3==row3 & col4<row4
            # is the same as
            # (((col1==row1 & col2==row2) | col3==row3) & col4<row4)
            logical_expression = None
            for lindex, logical in enumerate(logical_list):
                current_expression = (
                    COMPARATORS[comparators[lindex]](
                        data_frame, column_names[lindex], row_names[lindex]
                    )
                    if logical_expression is None
                    else logical_expression
                )
                next_expression = COMPARATORS[comparators[lindex + 1]](
                    data_frame, column_names[lindex + 1], row_names[lindex + 1]
                )
                logical_expression = LOGICAL_OPERATORS[logical_list[lindex]](
                    current_expression, next_expression
                )
        return data_frame[logical_expression]

    def _clean_text(self, text):
        # Remove invalid characters
        for ic in INVALID_CHARACTERS:
            text = text.replace(ic, "")

        # Replace multiple occurences of & or |
        text = re.sub(r"(&)\1+", r"\1", text)
        text = re.sub(r"(\|)\1+", r"\1", text)

        # Fix minor typos &| -> & or |& -> |
        text = re.sub(r"(&\|)", "&", text)
        text = re.sub(r"(\|&)", "|", text)
        return text

    def filter_hands_table(self, filter_text, data_frame):
        """
        A combined string can be specified to filter columns and rows
        (e.g. "Object==1" or "label=LaneChangeLeft")
        Syntax: "col1==row1 & col2==row2 | col3==row3"
        """
        df_types = data_frame.dtypes
        filter_text = self._clean_text(filter_text)
        if filter_text != "":
            logical_list = re.findall(LOGICAL_REGEX, filter_text)
            comparator_list = re.split(LOGICAL_REGEX, filter_text)

            assert len(logical_list) + 1 == len(comparator_list)

            column_names, row_names, comparators = [], [], []
            for cindex, comparator_exp in enumerate(comparator_list):

                comparator = re.findall(COMPARATOR_REGEX, comparator_exp)
                if len(comparator) == 0:
                    error_msg = (
                        f"No comparison operator found in search string: {filter_text}!"
                    )
                    self.logger.error(error_msg)
                    return data_frame

                arguments = re.split(COMPARATOR_REGEX, comparator_exp)
                column_name, row_name = arguments[0], arguments[1]
                if column_name not in list(data_frame.columns):
                    error_msg = f"No column name '{column_name}' in label table!"
                    self.logger.error(error_msg)
                    return data_frame

                try:
                    row_name = self._cast_row(column_name, row_name, df_types)
                except Exception as e:
                    error_msg = f"Casting failed: {e}"
                    self.logger.error(error_msg)
                    return data_frame

                column_names.append(column_name)
                row_names.append(row_name)
                comparators.append(comparator[0])

            new_hands_table = self._filter(
                data_frame, column_names, row_names, logical_list, comparators
            )

        else:
            new_hands_table = data_frame

        # Display the actual filtered search string
        self.logger.info(f"{filter_text} - {new_hands_table.shape[0]} hands")
        return new_hands_table

    def reset(self):
        self.logger.info(
            f"Cleared filter - Displaying {self.mw.image_info_df.shape[0]} hands"
        )
        self.update_hands_table(self.mw.image_info_df)

    def delete(self):
        self.reset()
        delattr(self.mw, "hands_filter_ui")

    def cancel(self):
        self.reset()
        self.mw.hands_filter_ui.close()

    def update_hands_table(self, hands_table):
        self.mw.hands_table_update_signal.emit(hands_table)

    def _connect_signals(self):
        self.mw.hands_filter_ui.filter_apply_button.clicked.connect(self.apply)
        self.mw.hands_filter_ui.filter_apply_button.setShortcut("Return")

        self.mw.hands_filter_ui.filter_reset_button.clicked.connect(self.reset)
        self.mw.hands_filter_ui.filter_reset_button.setShortcut("F5")

        self.mw.hands_filter_ui.filter_close_button.clicked.connect(self.cancel)
        self.mw.hands_filter_ui.filter_close_button.setShortcut("Escape")

        self.mw.hands_filter_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.mw.hands_filter_ui.destroyed.connect(self.delete)
