import sys
from PyQt5.QtWidgets import QApplication
from app.ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)

    # Apenas abre a janela de login
    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
