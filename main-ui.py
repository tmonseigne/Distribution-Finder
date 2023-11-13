import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel
)
from PyQt6.QtGui import QAction

import pandas as pd

class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.status = QLabel()
        self.dataframe = pd.DataFrame()
        self.table = QTableWidget()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Distribution Finder")
        self.resize(800, 600)  # Définition de la taille par défaut

        menubar = self.menuBar()
        open_action = QAction('Ouvrir CSV (Ctrl+O)', self)
        open_action.setShortcut('Ctrl+O')               # Raccourci Ctrl+O pour Ouvrir
        open_action.triggered.connect(self.openCSV)     # Connecter à la méthode openCSV
        menubar.addAction(open_action)

        process_action = QAction('Process (Ctrl+P)', self)
        process_action.setShortcut('Ctrl+P')            # Raccourci Ctrl+O pour Ouvrir
        process_action.triggered.connect(self.process)  # Connecter à la méthode process
        menubar.addAction(process_action)

        # Ajout de la barre d'état
        self.status.setText('Prêt')          # Message par défaut

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(self.table)
        layout.addWidget(self.status)

    def openCSV(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.status.setText(f"Ouverture du fichier \"{file_path}\".")
            self.loadCSV(file_path)
            self.status.setText(f"Fichier \"{file_path}\" Ouvert.")

    def loadCSV(self, file_path):
        self.dataframe = pd.read_csv(file_path)  # Charger le CSV dans le DataFrame

        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        for row_num in range(len(self.dataframe)):
            self.table.insertRow(row_num)
            if row_num == 0: self.table.setColumnCount(len(self.dataframe.columns))
            for col_num in range(len(self.dataframe.columns)):
                item = QTableWidgetItem(str(self.dataframe.iloc[row_num, col_num]))
                self.table.setItem(row_num, col_num, item)
        self.table.setHorizontalHeaderLabels(self.dataframe.columns)
        self.table.resizeColumnsToContents()

    def process(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            column = set(item.column() for item in selected_items)
            if len(column) == 1:
                col_index = list(column)[0]
                print(f"Selected column : {col_index}")
            else:
                print("Please select only one column.")
        else:
            print("No column selected.")

def main():
    try:
        app = QApplication(sys.argv)
        window = CSVViewer()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
