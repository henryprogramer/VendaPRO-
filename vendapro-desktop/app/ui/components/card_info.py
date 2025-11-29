from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame

class CardInfo(QFrame):
    def __init__(self, title, value):
        super().__init__()

        self.setObjectName("cardInfo")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(QLabel(str(value)))
        self.setLayout(layout)
