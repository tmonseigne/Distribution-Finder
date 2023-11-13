import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
import pandas as pd

class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataframe = pd.DataFrame()
        self.table = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CSV Viewer")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        open_button = QPushButton("Open CSV")
        open_button.clicked.connect(self.openCSV)
        layout.addWidget(open_button)

        open_button = QPushButton("Process")
        open_button.clicked.connect(self.process)
        layout.addWidget(open_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def openCSV(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")

        if file_path:
            self.loadCSV(file_path)

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
