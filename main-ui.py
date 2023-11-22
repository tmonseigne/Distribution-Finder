""" Fichier principal avec UI """
import os
import sys

import pandas as pd
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from libs.distributions import check_distributions
from libs.report import make_report

result_path = "Output"

##################################################
class ImageWindow(QDialog):
    """ Classe du visualisateur d'image """
    def __init__(self, image_path, parent=None):
        super(ImageWindow, self).__init__(parent)

        # Paramétrage de la fenêtre
        screen_res = QApplication.primaryScreen().geometry().size()
        self.setMinimumSize(800, 500)                                   # Taille minimale de la Fenêtre
        self.setMaximumSize(screen_res.width(), screen_res.height())    # Taille Maximale de la Fenêtre
        self.setWindowTitle("Comparaison des distributions")            # Titre de la fenêtre
        self.setGeometry(200, 200, 1200, 750)                           # Position de la fenêtre

        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setScaledContents(True)                              # Force la mise à jour de la taille du contenu (donc l'image) selon la fenêtre
        self.layout.addWidget(self.label)
        pixmap = QPixmap(image_path)                                    # Chargement de l'image
        self.label.setPixmap(pixmap)                                    # Application de l'image au widget
        self.setLayout(self.layout)

##################################################
class DistributionFinderUI(QMainWindow):
    """ Classe de mon interface """

    ##################################################
    def __init__(self):
        super().__init__()

        self.table = QTableWidget()
        self.status = QLabel()
        self.dataframe = pd.DataFrame()
        self.path = ""
        self.file_name = ""
        self.initUI()

    ##################################################
    def initUI(self):
        """ Initialize l'interface """
        self.setWindowTitle("Distribution Finder")      # Titre de la fenêtre
        self.setGeometry(100, 100, 800, 600)            # Position de la fenêtre

        menubar = self.menuBar()
        open_action = QAction('Ouvrir CSV (Ctrl+O)', self)
        open_action.setShortcut('Ctrl+O')               # Raccourci Ctrl+O pour Ouvrir
        open_action.triggered.connect(self.openCSV)     # Connecter à la méthode openCSV
        menubar.addAction(open_action)

        process_action = QAction('Process (Ctrl+P)', self)
        process_action.setShortcut('Ctrl+P')            # Raccourci Ctrl+P pour lancer le process
        process_action.triggered.connect(self.process)  # Connecter à la méthode process
        menubar.addAction(process_action)

        self.status.setText('Prêt')                     # Message par défaut dans la barre d'état

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(self.table)                    # Ajout du tableau (vide au début)
        layout.addWidget(self.status)                   # Ajout de la barre d'état

    ##################################################
    def openCSV(self):
        """ Ouvre un fichier CSV """
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.status.setText(f"Ouverture du fichier \"{file_path}\".")
            self.loadCSV(file_path)
            self.status.setText(f"Fichier \"{file_path}\" ouvert.")

    ##################################################
    def loadCSV(self, file_path):
        """ Charge un fichier CSV """
        self.dataframe = pd.read_csv(file_path)                                      # Charger le CSV dans le DataFrame
        self.path, self.file_name = os.path.split(file_path)                         # Séparer le chemin du fichier et le nom
        self.file_name = os.path.splitext(self.file_name)[0]                         # Obtention du nom de fichier sans extension
        self.path = os.path.join(self.path, result_path)                             # Ajout du dossier de résultat au chemin
        os.makedirs(self.path, exist_ok=True)                                        # Créer le dossier de résultat (la première fois, il n'existe pas)

        self.table.setColumnCount(len(self.dataframe.columns))                       # Définition du nombre de colonnes
        self.table.setRowCount(len(self.dataframe))                                  # Définition du nombre de lignes
        self.table.setHorizontalHeaderLabels(self.dataframe.columns)                 # Titre des colonnes

        for row_num in range(len(self.dataframe)):
            for col_num in range(len(self.dataframe.columns)):
                item = QTableWidgetItem(str(self.dataframe.iloc[row_num, col_num]))  # Récupération de la valeur
                self.table.setItem(row_num, col_num, item)                           # Copie dans la table
        self.table.resizeColumnsToContents()                                         # Mise à jour des largeurs de colonnes en fonction du contenu

    ##################################################
    def openImg(self, image_path):
        """
        Ouvre une nouvelle fenêtre avec l'image des distributions
        :param image_path: Chemin vers l'image
        """
        img_window = ImageWindow(image_path, parent=self)
        img_window.exec()

    ##################################################
    def process(self):
        """ Calcul des distributions et génération du rapport """
        selected_items = self.table.selectedItems()
        if selected_items:
            column = set(item.column() for item in selected_items)
            if len(column) == 1:
                i = list(column)[0]
                col_name = self.dataframe.columns[i]
                data = self.dataframe.iloc[:, i]
                file_name = f"{self.file_name}-{col_name}"
                self.status.setText(f"Colonne {i} ({col_name}) sélectionnée, calcul en cours...")
                results = check_distributions(data)
                results["Dataframe"].to_csv(os.path.join(self.path, f"{file_name}_Results.csv"), index=False)
                make_report(data, results, f"{file_name}_Report", self.path)
                self.status.setText(f"Rapport généré ici \"{self.path}\" pour la colonne {i} ({col_name}). "
                                    f"Distribution la plus proche : {results['Dataframe'].iloc[0][0]}.")
                valid_name = file_name.replace(" ", "_")
                self.openImg(os.path.join(self.path, f"{valid_name}_Report-001.png"))
            else:
                self.status.setText(f"Veuillez sélectionner une seule colonne.")
        else:
            self.status.setText(f"Aucune colonne sélectionnée.")


##################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DistributionFinderUI()
    window.show()
    sys.exit(app.exec())
