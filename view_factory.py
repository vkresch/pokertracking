from abc import ABC, abstractmethod


class ViewFactory(ABC):

    # Make sure only one instace of the factory exists
    _instance = None

    def __new__(cls, mainwindow):
        if cls._instance is None:
            cls._instance = super(ViewFactory, cls).__new__(cls)
            cls.mainwindow = mainwindow
            cls.graph_widgets = {}  # Collect created widget objects
        return cls._instance

    @abstractmethod
    def createGraph(self, view_name):
        pass
