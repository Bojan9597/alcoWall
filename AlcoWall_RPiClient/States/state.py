# state.py

from abc import ABC, abstractmethod

class State(ABC):


    @abstractmethod
    def handle_unsuccessful(self, alcoWall):
        pass

    @abstractmethod
    def handle_successful(self, alcoWall):
        pass
    @abstractmethod
    def handle_error(self, alcoWall):
        pass
