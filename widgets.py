from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QLineEdit, QPushButton, QLabel, 
                              QMessageBox, QHeaderView, QFormLayout, QGroupBox,
                              QMainWindow, QStatusBar, QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt
from datetime import datetime
from database import DatabaseManager
from models import Artwork, ValidationError

class DeleteConfirmationDialog(QDialog):
    def __init__(self, artwork_title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтверждение удаления")
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Вы уверены, что хотите удалить произведение:\n\"{artwork_title}\"?"))
        
        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)

class ArtworkTable(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Коллекция произведений:"))
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        self.delete_btn = QPushButton("Удалить выбранное")
        self.delete_btn.clicked.connect(self.delete_selected_artwork)
        self.delete_btn.setEnabled(False)
        header_layout.addWidget(self.delete_btn)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Художник", "Год", "Стиль", "Цена (€)", "Дата добавления"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def on_selection_changed(self):
        has_selection = len(self.table.selectedItems()) > 0
        self.delete_btn.setEnabled(has_selection)
    
    def get_selected_artwork_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        return int(self.table.item(selected_items[0].row(), 0).text())
    
    def get_selected_artwork_title(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        return self.table.item(selected_items[0].row(), 1).text()
    
    def delete_selected_artwork(self):
        artwork_id = self.get_selected_artwork_id()
        artwork_title = self.get_selected_artwork_title()
        
        if artwork_id is None:
            QMessageBox.warning(self, "Предупреждение", "Не выбрано произведение для удаления")
            return
        
        dialog = DeleteConfirmationDialog(artwork_title, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.delete_artwork(artwork_id)
                self.load_data()
                QMessageBox.information(self, "Успех", "Произведение успешно удалено!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
    
    def load_data(self):
        try:
            artworks = self.db.get_all_artworks()
            self.table.setRowCount(len(artworks))
            
            for row, artwork in enumerate(artworks):
                self.table.setItem(row, 0, QTableWidgetItem(str(artwork.id)))
                self.table.setItem(row, 1, QTableWidgetItem(artwork.title))
                self.table.setItem(row, 2, QTableWidgetItem(artwork.artist))
                self.table.setItem(row, 3, QTableWidgetItem(str(artwork.year)))
                self.table.setItem(row, 4, QTableWidgetItem(artwork.style))
                self.table.setItem(row, 5, QTableWidgetItem(f"{artwork.price:,.2f}"))
                self.table.setItem(row, 6, QTableWidgetItem(artwork.created_at))
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

class InputForm(QWidget):
    def __init__(self, table_widget):
        super().__init__()
        self.table_widget = table_widget
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.artist_input = QLineEdit()
        self.year_input = QLineEdit()
        self.style_input = QLineEdit()
        self.price_input = QLineEdit()
        
        self.title_input.setPlaceholderText("Например: Звездная ночь")
        self.artist_input.setPlaceholderText("Например: Ван Гог")
        self.year_input.setPlaceholderText("Например: 1889")
        self.style_input.setPlaceholderText("Например: Постимпрессионизм")
        self.price_input.setPlaceholderText("Например: 1000000")
        
        layout.addRow("Название:", self.title_input)
        layout.addRow("Художник:", self.artist_input)
        layout.addRow("Год создания:", self.year_input)
        layout.addRow("Стиль:", self.style_input)
        layout.addRow("Цена (€):", self.price_input)
        
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить произведение")
        self.clear_btn = QPushButton("Очистить")
        
        self.add_btn.clicked.connect(self.add_artwork)
        self.clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.clear_btn)
        
        layout.addRow(button_layout)
        
        group_box = QGroupBox("Добавить новое произведение")
        group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)
    
    def add_artwork(self):
        try:
            try:
                year = int(self.year_input.text())
                price = float(self.price_input.text())
            except ValueError:
                raise ValidationError("Год и цена должны быть числами")
            
            artwork = Artwork(
                id=None,
                title=self.title_input.text(),
                artist=self.artist_input.text(),
                year=year,
                style=self.style_input.text(),
                price=price,
                created_at=""
            )
            
            self.db.add_artwork(artwork)
            self.table_widget.load_data()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Произведение успешно добавлено!")
            
        except (ValidationError, Exception) as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def clear_form(self):
        self.title_input.clear()
        self.artist_input.clear()
        self.year_input.clear()
        self.style_input.clear()
        self.price_input.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Виртуальная галерея искусства")
        self.setGeometry(100, 100, 1000, 800)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.table_widget = ArtworkTable()
        main_layout.addWidget(self.table_widget)
        
        self.input_form = InputForm(self.table_widget)
        main_layout.addWidget(self.input_form)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Подтверждение выхода',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()