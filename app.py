import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QAction,\
                            QLabel, QFileDialog, QTextEdit,QToolButton, QLineEdit
from PyQt5.QtGui import QPixmap,QImage, QIcon, QKeySequence

class ImageAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ImageCaptioningTool')
        
        # ウィジェットのサイズを設定
        self.setGeometry(100, 100, 950, 540)

        # 画像の表示
        self.label = QLabel(self)
        self.label.setGeometry(100, 0, 540, 540) # (80,20)(700,420)
        self.label.setFrameStyle(QLabel.Panel | QLabel.Sunken)
        
        # 画像のインデックスと合計数
        self.count_number = QLabel(self)
        self.count_number.setText("")
        self.count_number.setGeometry(650, 5, 40, 30) #(80,430)(700,460)
        
        self.all_image_number = QLabel(self)
        self.all_image_number.setText("")
        self.all_image_number.setGeometry(700, 5, 40, 30) #(80,430)(700,460)

        # labelラベル
        self.image_label_label = QLabel(self)
        self.image_label_label.setText("label:")
        self.image_label_label.setGeometry(650, 50, 60, 30) #(80,430)(700,460)
        
        # labelテキストボックスを作成
        self.image_label = QLineEdit(self)
        self.image_label.setGeometry(710, 50, 170, 30) #(80,430)(700,460)

        # captionラベル
        self.caption_label = QLabel(self)
        self.caption_label.setText("caption")
        self.caption_label.setGeometry(650, 80, 620, 30) #(80,430)(700,460)
        
        # captionテキストボックスを作成
        self.caption = QTextEdit(self)
        self.caption.setGeometry(650, 110, 950-660, 80) #(80,430)(700,460)
        
        # 画像一覧スクロール
        self.images_list_label = QLabel(self)
        self.images_list_label.setText("image list")
        self.images_list_label.setGeometry(650, 200, 150, 30) #(80,430)(700,460)
        
        self.scroll_area_content = QListWidget(self)
        self.scroll_area_content.setGeometry(650, 230, 290, 300) #(80,430)(700,460)
        self.scroll_area_content.currentItemChanged.connect(self.show_selected_image)
        
        # フォルダーボタン
        self.folder_button = QToolButton(self)
        self.folder_button.setGeometry(20, 20, 50, 70)  # 90 
        self.folder_button.setIcon(QIcon("./icon/open-file-folder-emoji.png"))
        self.folder_button.setText("Open")
        self.folder_button.setIconSize(self.folder_button.size()) # アイコンのサイズをボタンのサイズに合わせる
        self.folder_button.setStyleSheet("border: none;")
        self.folder_button.setToolButtonStyle(3) # ボ
        
        # Next ボタン
        self.next_button = QToolButton(self)
        self.next_button.setGeometry(20, 110, 50, 70)  # 180
        self.next_button.setIcon(QIcon("./icon/right.png"))
        self.next_button.setText("Next")
        self.next_button.setIconSize(self.next_button.size()) # アイコンのサイズをボタンのサイズに合わせる
        self.next_button.setStyleSheet("border: none;")
        self.next_button.setToolButtonStyle(3) # ボ
        
        # Back ボタン
        self.back_button = QToolButton(self)
        self.back_button.setGeometry(20, 200, 50, 70)  # 
        self.back_button.setIcon(QIcon("./icon/left.png"))
        self.back_button.setText("Back")
        self.back_button.setIconSize(self.back_button.size()) # アイコンのサイズをボタンのサイズに合わせる
        self.back_button.setStyleSheet("border: none;")
        self.back_button.setToolButtonStyle(3) # ボ
        
        # Save ボタン
        self.save_button = QToolButton(self)
        self.save_button.setGeometry(20, 290, 50, 70)  # 
        self.save_button.setIcon(QIcon("./icon/save.png"))
        self.save_button.setText("Save")
        self.save_button.setIconSize(self.save_button.size()) # アイコンのサイズをボタンのサイズに合わせる
        self.save_button.setStyleSheet("border: none;")
        self.save_button.setToolButtonStyle(3) 
        
        # ショートカットキー
        self.save_action = QAction('Save File',self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.save_action.triggered.connect(self.save_caption)
        
        self.open_folder_action = QAction('Open Folder',self)
        self.open_folder_action.setShortcut(QKeySequence('Ctrl+O'))
        self.open_folder_action.triggered.connect(self.load_folder)
        
        self.next_button.setShortcut(Qt.Key_Right)
        self.back_button.setShortcut(Qt.Key_Left)
        
        # メニューバー
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.open_folder_action)
        file_menu.addAction(self.save_action)
        
        # forcusをする
        self.label.setFocus()
        
        # ボタンに関数を関連付ける
        self.connect_buttons()
        
        self.open_folder = False

    def connect_buttons(self):
        self.folder_button.clicked.connect(self.load_folder)
        self.save_button.clicked.connect(self.save_caption)
        self.next_button.clicked.connect(self.next_image)
        self.back_button.clicked.connect(self.back_image)

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'フォルダーを選択', os.getcwd())
        
        if folder_path:
            self.open_folder = True
            self.folder_path = folder_path
            self.image_folder_path = os.path.join(folder_path, 'image')
            if os.path.isdir(self.image_folder_path):
                self.text_folder_path = os.path.join(folder_path, 'text')
                if not os.path.isdir(self.text_folder_path):
                    os.mkdir(self.text_folder_path)
                self.label_folder_path = os.path.join(folder_path, 'label')
                if not os.path.isdir(self.label_folder_path):
                    os.mkdir(self.label_folder_path)
                self.images = sorted(os.listdir(self.image_folder_path))
                for image in self.images:
                    self.scroll_area_content.addItem(image)
                self.current_image_index = 0
                self.all_image_number.setText("/ " + str(len(self.images)))
                self.count_number.setText(str(self.current_image_index))
                self.show_image()

    def show_image(self):
        # 画像の表示
        image_path = os.path.join(self.image_folder_path, self.images[self.current_image_index])
        
        # QListWidgetを取得
        list_widget = self.scroll_area_content
        items = list_widget.findItems(self.images[self.current_image_index], Qt.MatchExactly)

        # アイテムが見つかった場合、それを選択状態にする
        if items:
            item = items[0]
            list_widget.setCurrentItem(item)
        
        if os.path.isfile(image_path):
            self.count_number.setText(str(self.current_image_index))
            
            self.image = QImage(image_path)
            pixmap = QPixmap.fromImage(self.image)
            pixmap = pixmap.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
            self.label.setFocus()
            
            # テキストの表示
            text_path = os.path.join(self.text_folder_path, self.images[self.current_image_index].replace("jpg","txt"))
            if os.path.isfile(text_path):
                with open(text_path,mode="r") as f:
                    data = f.read()
                    self.caption.setText(data)
            else:
                self.caption.setText("")
            # ラベルの表示
            label_path = os.path.join(self.label_folder_path, self.images[self.current_image_index].replace("jpg","txt"))
            if os.path.isfile(label_path):
                with open(label_path,mode="r") as f:
                    data = f.read()
                    self.image_label.setText(data)
            else:
                self.image_label.setText("")
    
    def show_selected_image(self, current_item, previous_item):
        selected_filename = current_item.text()
        self.current_image_index = self.images.index(selected_filename)
        self.show_image()

    def save_caption(self):
        if self.open_folder:
            self.label.setFocus()
            caption_text = self.caption.toPlainText()
            text_path = os.path.join(self.text_folder_path, self.images[self.current_image_index].replace("jpg","txt"))
            print(text_path)
            with open(text_path, 'w') as f:
                f.write(caption_text)
            
            label_text = self.image_label.text()
            label_path = os.path.join(self.label_folder_path, self.images[self.current_image_index].replace("jpg","txt"))
            print(label_path)
            with open(label_path, 'w') as f:
                f.write(label_text)

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.images):
            self.current_image_index = 0
        self.show_image()
    
    def back_image(self):
        self.current_image_index -= 1
        if self.current_image_index <= 0:
            self.current_image_index = 0
        self.show_image()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # ウィンドウサイズを取得
        size = event.size()
        print(size)

        img_width = max(size.height(),700)
        
        self.label.setGeometry(100, 0, size.width()-410, size.height()) # (80,20)(700,420)
        
        # 画像のインデックスと合計数
        self.count_number.setGeometry(size.width()-300, 5, 40, 30) #(80,430)(700,460)
        self.all_image_number.setGeometry(size.width()-250, 5, 40, 30) #(80,430)(700,460)

        # labelラベル
        self.image_label_label.setGeometry(size.width()-300, 50, 60, 30) #(80,430)(700,460)
        
        # labelテキストボックスを作成
        self.image_label.setGeometry(size.width()-240, 50, 170, 30) #(80,430)(700,460)

        # captionラベル
        self.caption_label.setGeometry(size.width()-300, 80, 620, 30) #(80,430)(700,460)
        
        # captionテキストボックスを作成
        self.caption.setGeometry(size.width()-300, 110, 950-660, 80) #(80,430)(700,460)
        
        # 画像一覧スクロール
        self.images_list_label.setGeometry(size.width()-300, 200, 300, 30) #(80,430)(700,460)
        self.scroll_area_content.setGeometry(size.width()-300, 230, 290, 300) #(80,430)(700,460)


if __name__ == '__main__':
    app = QApplication([])
    image_annotator = ImageAnnotator()
    image_annotator.show()
    sys.exit(app.exec_())
