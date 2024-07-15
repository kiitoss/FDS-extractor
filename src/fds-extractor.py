import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import extractor

TITLE = "FDS Extractor"
SELECT_FOLDER = "Sélectionner un dossier"
NO_FOLDER_SELECTED = "Aucun dossier sélectionné"
SELECT_FOLDER_INPUT = "Dossier sélectionné:\n"
SELECT_FOLDER_CONTAINING_FDS = "Sélectionner un dossier contenant les fiches FDS"
RUN_EXECUTION = "Lancer l'exécution"
EXECUTION_WITH_FOLDER = "Exécution lancée avec le dossier"

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = TITLE
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 600, 150)  # Taille de la fenêtre

        # Configuration de la disposition de la fenêtre
        mainLayout = QVBoxLayout()

        # Label pour afficher le dossier sélectionné
        self.label = QLabel(NO_FOLDER_SELECTED, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 14))
        mainLayout.addWidget(self.label)

        # Layout horizontal pour les boutons
        buttonLayout = QHBoxLayout()

        # Bouton pour sélectionner un dossier
        self.folderButton = QPushButton(
            SELECT_FOLDER_CONTAINING_FDS, self
        )
        self.folderButton.setFont(QFont("Arial", 12))
        self.folderButton.clicked.connect(self.selectFolder)
        buttonLayout.addWidget(self.folderButton)

        # Bouton pour lancer l'exécution
        self.executeButton = QPushButton(RUN_EXECUTION, self)
        self.executeButton.setFont(QFont("Arial", 12))
        self.executeButton.setEnabled(False)  # Désactiver le bouton au début
        self.executeButton.clicked.connect(self.execute)
        buttonLayout.addWidget(self.executeButton)

        # Ajouter le layout des boutons au layout principal
        mainLayout.addLayout(buttonLayout)

        # Appliquer le layout principal à la fenêtre
        self.setLayout(mainLayout)

        # Appliquer un style à la fenêtre et aux widgets
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:disabled {
                background-color: #9E9E9E;
            }
        """
        )

        # Afficher la fenêtre
        self.show()

    def selectFolder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(
            self, SELECT_FOLDER, options=options
        )
        if folder:
            self.label.setText(f"{SELECT_FOLDER_INPUT}{folder}")
            self.executeButton.setEnabled(
                True
            )  # Activer le bouton si un dossier est sélectionné
        else:
            self.label.setText(NO_FOLDER_SELECTED)
            self.executeButton.setEnabled(
                False
            )  # Désactiver le bouton si aucun dossier n'est sélectionné

    def execute(self):
        selected_folder = self.label.text().replace(SELECT_FOLDER_INPUT, "")
        if selected_folder != NO_FOLDER_SELECTED:
            print(f"{EXECUTION_WITH_FOLDER} : {selected_folder}")
            extractor.extract_data(selected_folder)
        else:
            print(NO_FOLDER_SELECTED)

        self.close()

        os.startfile(selected_folder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
