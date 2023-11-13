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
import csv

class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

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
        with open(file_path, newline='', encoding='utf-8') as file:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)

            for row_num, row_data in enumerate(csv.reader(file)):
                self.table.insertRow(row_num)
                if row_num == 0:
                    self.table.setColumnCount(len(row_data))
                for col_num, col_data in enumerate(row_data):
                    item = QTableWidgetItem(col_data)
                    self.table.setItem(row_num, col_num, item)

        self.table.setHorizontalHeaderLabels(next(csv.reader(open(file_path))))

    def process(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            column = set(item.column() for item in selected_items)
            if len(column) == 1:
                col_index = list(column)[0]
                column_data = [self.table.item(row, col_index).text() for row in range(self.table.rowCount())]
                print(f"Selected column data: {column_data}")
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
