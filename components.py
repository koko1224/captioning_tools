from PyQt5.QtWidgets import QListWidget, QVBoxLayout,QPushButton, QDialog, QToolButton
from PyQt5.QtGui import QIcon

class FolderSelectionDialog(QDialog):
    def __init__(self, folder_paths):
        super().__init__()
        self.setWindowTitle("Select Folder")

        self.selected_folder = None

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItems(folder_paths)
        layout.addWidget(self.list_widget)

        button = QPushButton("Select")
        button.clicked.connect(self.select_folder)
        layout.addWidget(button)

        self.setLayout(layout)

    def select_folder(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_folder = selected_items[0].text()
        self.accept()

class Action_Button(QToolButton):
    def __init__(self, parent,icon_path, tag, ax:int, ay:int, aw:int, ah:int):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setGeometry(ax, ay, aw, ah)
        self.setText(tag)
        self.setIconSize(self.size()) # アイコンのサイズをボタンのサイズに合わせる
        self.setStyleSheet("border: none;")
        self.setToolButtonStyle(3) # ボ
