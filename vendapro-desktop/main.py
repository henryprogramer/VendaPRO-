import sys
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from app.ui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)

    # Caminho absoluto da logo
    base_path = os.path.dirname(os.path.abspath(__file__))  # vendapro-desktop/vendapro/vendapro-desktop
    icon_path = os.path.join(base_path, "..", "assets", "images", "logo.png")
    icon_path = os.path.abspath(icon_path)

    print("APP ICON PATH:", icon_path)
    print("EXISTS:", os.path.exists(icon_path))

    # Define o ícone global do aplicativo
    app.setWindowIcon(QIcon(icon_path))

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
