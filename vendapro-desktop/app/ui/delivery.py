from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class DeliveryWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Delivery"))
        self.setLayout(layout)
