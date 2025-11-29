from PyQt5.QtWidgets import QPushButton

class NavButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("navButton")
