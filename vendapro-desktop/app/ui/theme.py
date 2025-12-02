from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

class Theme:
    @staticmethod
    def apply_dark(app: QApplication):
        palette = QPalette()

        # Fundo geral
        palette.setColor(QPalette.Window, QColor("#0d1b2a"))
        palette.setColor(QPalette.Base, QColor("#0d1b2a"))
        palette.setColor(QPalette.AlternateBase, QColor("#1b263b"))

        # Texto
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))

        # Botões
        palette.setColor(QPalette.Button, QColor("#1b263b"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))

        # Seleção
        palette.setColor(QPalette.Highlight, QColor("#2d7dff"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))

        app.setPalette(palette)

        # Estilos globais no app inteiro
        app.setStyleSheet("""
            QWidget {
                background-color: #0d1b2a;
                color: #e2e8f0;
                font-family: 'Segoe UI';
            }

            /* Botões */
            QPushButton {
                background-color: #1e40af;
                color: white;
                padding: 10px 18px;
                border-radius: 10px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #2563eb;
            }

            QPushButton:pressed {
                background-color: #1d4ed8;
            }

            /* Cards (usado em PainelWindow e outros) */
            .card {
                background-color: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 18px;
            }

            /* Labels */
            QLabel {
                font-size: 15px;
            }

            /* LineEdits */
            QLineEdit {
                background-color: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                padding: 8px;
                border-radius: 8px;
                color: white;
            }
        """)
