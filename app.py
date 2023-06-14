import os
import sys
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QAction,\
                            QLabel, QFileDialog, QTextEdit,QToolButton, QLineEdit,\
                            QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem
from PyQt5.QtGui import QPixmap,QImage, QIcon, QKeySequence, QPixmap, QPainter, QColor, QPen, QPolygonF, QBrush

from utils import load_annotations, get_filenames, get_textfolder, get_annotation_path, check_directory_type
from components import FolderSelectionDialog, Action_Button

class ImageAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ImageCaptioningTool')
        
        # ウィジェットのサイズを設定
        self.frame_width = 1000
        self.frame_height = 600
        self.setGeometry(100, 100, self.frame_width, self.frame_height)

        # 画像の表示
        self.img_width = 540
        self.img_height = 600
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setParent(self)
        
        # カウント
        self.image_count = QLabel(self)
        self.image_count.setText("")
        self.total_count = QLabel(self)
        self.total_count.setText("")

        # label
        self.label_label = QLabel(self)
        self.label_label.setText("label:")
        self.label_edit = QLineEdit(self)

        # caption
        self.caption_label = QLabel(self)
        self.caption_label.setText("caption")
        self.caption = QTextEdit(self)
        
        # アノテーション一覧
        self.annotation_label = QLabel(self)
        self.annotation_label.setText("annotation list")
        self.annotation_list = QListWidget(self)
        self.annotation_list.currentItemChanged.connect(self.select_bbox_list)
        
        # 画像一覧
        self.images_list_label = QLabel(self)
        self.images_list_label.setText("image list")
        self.images_list = QListWidget(self)
        self.images_list.currentItemChanged.connect(self.show_selected_image)
        
        # ボタン
        self.folder_button = Action_Button(self, "./icon/open-file-folder-emoji.png", "Open", 20, 20, 50, 70)
        self.next_button   = Action_Button(self, "./icon/right.png", "Next",20, 110, 50, 70)
        self.back_button   = Action_Button(self, "./icon/left.png", "Back", 20, 200, 50, 70)
        self.save_button   = Action_Button(self, "./icon/save.png", "Save", 20, 290, 50, 70)
        
        self.image_folder_path = None
        self.text_folder_path = None
        self.label_folder_path = None
        self.selected_annotation = None
        self.show_annotations = True  # アノテーションの表示/非表示を切り替えるフラグ
        
        self.scene.setFocus()
        self.connect_buttons()
        self.create_actions()
        self.create_menus()

    def connect_buttons(self):
        self.folder_button.clicked.connect(self.open_folder)
        self.save_button.clicked.connect(self.save_caption)
        self.next_button.clicked.connect(self.next_image)
        self.back_button.clicked.connect(self.back_image)
        
        # move action
        self.next_button.setShortcut(Qt.Key_Right)
        self.back_button.setShortcut(Qt.Key_Left)

    def create_actions(self):
        # Save action
        self.save_action = QAction('Save File',self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.save_action.triggered.connect(self.save_caption)
        
        # Open folder action
        self.open_folder_action = QAction('Open Folder',self)
        self.open_folder_action.setShortcut(QKeySequence('Ctrl+O'))
        self.open_folder_action.triggered.connect(self.open_folder)
        
        # toggle annotations action
        self.toggle_annotations_action = QAction('Toggle Annotations', self)
        self.toggle_annotations_action.setShortcut('Ctrl+T')
        self.toggle_annotations_action.setStatusTip('Toggle visibility of annotations')
        self.toggle_annotations_action.setCheckable(True)
        self.toggle_annotations_action.setChecked(True)
        self.toggle_annotations_action.triggered.connect(self.toggle_annotations)

    def create_menus(self):
        menubar = self.menuBar()
        # Fileメニュー
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.open_folder_action)
        file_menu.addAction(self.save_action)
        # Viewメニュー
        view_menu = menubar.addMenu('View')
        view_menu.addAction(self.toggle_annotations_action)
    
    def open_folder(self):
        self.images_list.clear()
        
        folder_path = QFileDialog.getExistingDirectory(self, 'フォルダーを選択', os.getcwd())
        if folder_path:
            self.image_folder_path = os.path.join(folder_path, 'image')
            if os.path.isdir(self.image_folder_path):
                content_type = check_directory_type(self.image_folder_path)
                self.text_folder_path = get_textfolder(folder_path=folder_path)
                if not os.path.isdir(self.text_folder_path):
                    if content_type == "file":
                        os.mkdir(self.text_folder_path)
                    else:
                        os.makedirs(os.path.join(self.text_folder_path,"train"), exist_ok=True)
                        os.makedirs(os.path.join(self.text_folder_path,"test"), exist_ok=True)
                        
                self.label_folder_path = os.path.join(folder_path, 'label')
                if not os.path.isdir(self.label_folder_path):
                    if content_type == "file":
                        os.mkdir(self.label_folder_path)
                    else:
                        os.makedirs(os.path.join(self.label_folder_path, "train"), exist_ok=True)
                        os.makedirs(os.path.join(self.label_folder_path, "test"), exist_ok=True)
                        
                self.annotation_path = get_annotation_path(folder_path)
                self.images = sorted(get_filenames(self.image_folder_path, content_type))
                for image in self.images:
                    self.images_list.addItem(image)
                    
                self.current_image_index = 0
                self.image_count.setText(str(self.current_image_index))
                self.total_count.setText("/ " + str(len(self.images)))
                self.show_image()
    
    def show_image(self):
        # 画像の表示
        image_path = os.path.join(self.image_folder_path, self.images[self.current_image_index])
        
        # images_listのアイテムを検索し，選択状態にする
        items = self.images_list.findItems(self.images[self.current_image_index], Qt.MatchExactly)
        if items:
            item = items[0]
            self.images_list.setCurrentItem(item)
        
        # 画像とアノテーションの表示
        if os.path.isfile(image_path):
            self.image_count.setText(str(self.current_image_index))
            
            width = self.view.width()
            height = self.view.height()
            
            # 初期化
            self.selected_annotation = None
            self.scene.clear()
            self.annotation_list.clear()
            
            # 画像の表示
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.scene.addPixmap(scaled_pixmap)
            self.scene.setFocus()
            
            # アノテーションの座標とサイズをスケーリング
            scale_factor_width = scaled_pixmap.width() / pixmap.width()
            scale_factor_height = scaled_pixmap.height() / pixmap.height()
            
            # annotationの表示
            annotation_path = self.annotation_path % tuple(self.images[self.current_image_index].split(".")[0].split("/"))
            self.draw_annotation(annotation_path, scale_factor_width, scale_factor_height)
            
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
                    self.label_edit.setText(data)
            else:
                self.label_edit.setText("")
    
    def draw_annotation(self,annotation_path, scale_factor_width, scale_factor_height):
        if os.path.exists(annotation_path):
            annotations = load_annotations(annotation_path)
            self.ann2bbox = {}
            self.bbox2ann = {}

            for annotation in annotations:
                if len(annotation["bbox"]) == 4:
                    bbox = QRectF(annotation['bbox'][0]*scale_factor_width, annotation['bbox'][1]*scale_factor_height,\
                                    annotation['bbox'][2]*scale_factor_width, annotation['bbox'][3]*scale_factor_height)
                    rect_item = QGraphicsRectItem(bbox)
                    rect_item.setPen(QPen(Qt.green))
                    rect_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    
                    ann = list(map(str,annotation.values()))
                    self.annotation_list.addItem(",".join(ann))
                    
                    self.ann2bbox[",".join(ann)] = rect_item
                    self.bbox2ann[rect_item] = ",".join(ann)
                    
                    if self.show_annotations:
                        self.scene.addItem(rect_item)
                else:
                    points = [QPointF(annotation['bbox'][i]*scale_factor_width, annotation['bbox'][i+1]*scale_factor_height) for i in range(0, len(annotation['bbox']), 2)]
                    polygon = QPolygonF(points)                
                    # 多角形をシーンに追加
                    polygon_item = QGraphicsPolygonItem(polygon)
                    # 枠線の設定
                    polygon_item.setPen(QPen(Qt.green))
                    # 塗りつぶしの設定
                    polygon_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    
                    ann = list(map(str,annotation.values()))
                    self.annotation_list.addItem(",".join(ann))
                    
                    self.ann2bbox[",".join(ann)] = polygon_item
                    self.bbox2ann[polygon_item] = ",".join(ann)
                    
                    if self.show_annotations:
                        self.scene.addItem(polygon_item)
                    
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def select_bbox_list(self, current_item, previous_item):
        if current_item is not None:
            selected_annotation = current_item.text()
            item = self.ann2bbox[selected_annotation]
            if self.selected_annotation is not None:
                self.selected_annotation.setPen(QPen(Qt.green))
                self.selected_annotation.setBrush(QBrush(QColor(0, 255, 0, 100)))
            self.selected_annotation = item
            item.setPen(QPen(Qt.yellow))
            item.setBrush(QBrush(QColor(255, 255, 0, 100)))
    
    def show_selected_image(self, current_item, previous_item):
        if current_item is not None:
            selected_filename = current_item.text()
            self.current_image_index = self.images.index(selected_filename)
            self.show_image()
        
    def toggle_annotations(self):
        self.show_annotations = not self.show_annotations
        self.show_image()

    def save_caption(self):
        if self.text_folder_path is not None and self.label_folder_path is not None:
            self.scene.setFocus()
            caption_text = self.caption.toPlainText()
            text_path = os.path.join(self.text_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt"))
            with open(text_path, 'w') as f:
                f.write(caption_text)
            
            label_text = self.label_edit.text()
            label_path = os.path.join(self.label_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt"))
            with open(label_path, 'w') as f:
                f.write(label_text)

    def next_image(self):
        if self.image_folder_path is not None:
            self.current_image_index += 1
            if self.current_image_index >= len(self.images):
                self.current_image_index = 0
            self.show_image()
    
    def back_image(self):
        if self.image_folder_path is not None:
            self.current_image_index -= 1
            if self.current_image_index <= 0:
                self.current_image_index = 0
            self.show_image()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # コンポーネントのサイズを計算
        size = event.size()
        ratio = self.img_width / (self.frame_width - 100)
        new_img_size = min(int(ratio * (size.width() - 100)), 850)
        annotation_area_x = new_img_size + 100 + 10 
        
        # 画像
        self.view.setGeometry(100, 0, new_img_size, size.height()) 
        
        # カウント
        self.image_count.setGeometry(annotation_area_x, 5, 40, 30) 
        self.total_count.setGeometry(annotation_area_x + 50, 5, 40, 30) 

        # label
        self.label_label.setGeometry(annotation_area_x, 50, 60, 30) 
        self.label_edit.setGeometry(annotation_area_x + 60, 50, 170, 30) 

        # caption
        self.caption_label.setGeometry(annotation_area_x, 80, 620, 30) 
        self.caption.setGeometry(annotation_area_x, 110, size.width() - (annotation_area_x + 10), 50) 
        
        # annotation一覧
        self.annotation_label.setGeometry(annotation_area_x, 160, 620, 30) 
        annotation_list_height = max(50, size.height()//2 - 200)
        self.annotation_list.setGeometry(annotation_area_x, 190, size.width() - (annotation_area_x + 10), annotation_list_height) 
        
        # 画像一覧スクロール
        image_list_y = 190 + annotation_list_height + 10
        image_list_height = max(50, size.height() - image_list_y - 40)
        self.images_list_label.setGeometry(annotation_area_x, image_list_y, 300, 30) 
        self.images_list.setGeometry(annotation_area_x, image_list_y + 30, size.width() - (annotation_area_x + 10), image_list_height) 
    
    def mousePressEvent(self, event):
        """
        画像中のアノテーションをクリックした際の処理
        - クリックしたアノテーションを黄色にする
        - それ以外は緑色にする
        - アノテーション一覧の該当アノテーションを選択状態にする
        """
        if event.button() == Qt.LeftButton:
            for item in self.scene.items():
                if isinstance(item, QGraphicsView):
                    continue
                if isinstance(item, QGraphicsRectItem) or isinstance(item, QGraphicsPolygonItem):
                    if item.isUnderMouse():
                        if self.selected_annotation is not None:
                            self.selected_annotation.setPen(QPen(Qt.green))
                            self.selected_annotation.setBrush(QBrush(QColor(0, 255, 0, 100)))
                        self.selected_annotation = item
                        item.setPen(QPen(Qt.yellow))
                        item.setBrush(QBrush(QColor(255, 255, 0, 100)))
                        ann_items = self.annotation_list.findItems(self.bbox2ann[item], Qt.MatchExactly)
                        if ann_items:
                            self.annotation_list.setCurrentItem(ann_items[0])
                        break

if __name__ == '__main__':
    app = QApplication([])
    image_annotator = ImageAnnotator()
    image_annotator.show()
    sys.exit(app.exec_())
