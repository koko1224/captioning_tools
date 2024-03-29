import os
import sys

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QKeySequence, QPen, QPixmap, QPolygonF
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QPushButton,
                             QGraphicsPolygonItem, QGraphicsRectItem,
                             QGraphicsScene, QGraphicsView, QLabel,
                             QListWidget, QMainWindow, QTextEdit)

from components import Action_Button
from utils import (check_directory_type, get_annotation_path, get_filenames,
                   get_textfolder, load_annotations, custom_sort)


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
        self.label_label.setText("label")
        self.label_edit = QTextEdit(self)

        # caption
        self.caption_label = QLabel(self)
        self.caption_label.setText("caption")
        self.caption = QTextEdit(self)

        # アノテーション一覧
        self.annotation_label = QLabel(self)
        self.annotation_label.setText("annotation list")
        self.annotation_list = QListWidget(self)
        self.annotation_list.currentItemChanged.connect(self.select_bbox_list)
        self.annotation_list.itemDoubleClicked.connect(self.get_selected_annotation_word)

        # 画像一覧
        self.images_list_label = QLabel(self)
        self.images_list_label.setText("image list")
        self.images_list = QListWidget(self)
        self.images_list.currentItemChanged.connect(self.show_selected_image)
        self.images_list.itemDoubleClicked.connect(self.get_now_filename)

        # ボタン
        self.folder_button = Action_Button(self, "./icon/open.png", "Open", 20, 20, 50, 70)
        self.next_button   = Action_Button(self, "./icon/right.png","Next", 20, 110, 50, 70)
        self.back_button   = Action_Button(self, "./icon/left.png", "Back", 20, 200, 50, 70)
        self.save_button   = Action_Button(self, "./icon/save.png", "Save", 20, 290, 50, 70)

        # トグルボタン
        self.toggle_skip = QPushButton("only none", self)
        self.toggle_skip.setCheckable(True)
        self.toggle_skip.clicked.connect(self.skip_annotated_image)

        self.toggle_skip_exist = QPushButton("only exist", self)
        self.toggle_skip_exist.setCheckable(True)
        self.toggle_skip_exist.clicked.connect(self.skip_annotated_image_exist)

        self.toggle_ann = QPushButton("Hide ###", self)
        self.toggle_ann.setCheckable(True)
        self.toggle_ann.clicked.connect(self.hide_annotations)

        self.image_folder_path = None
        self.text_folder_path = None
        self.label_folder_path = None
        self.selected_annotation = None
        self.show_annotations = True  # アノテーションの表示/非表示を切り替えるフラグ
        self.skip_mode = False  # スキップモードのフラグ
        self.skip_mode_exist = False  # スキップモードのフラグ
        self.hide_flag = False

        self.scene.setFocus()
        self.connect_buttons()
        self.create_actions()
        self.create_menus()


    def connect_buttons(self):
        self.folder_button.clicked.connect(self.open_folder)
        self.save_button.clicked.connect(self.save_caption)
        self.next_button.clicked.connect(self.next_image)
        self.back_button.clicked.connect(self.back_image)

        self.next_button.setShortcut(Qt.Key_Right)
        self.back_button.setShortcut(Qt.Key_Left)


    def create_actions(self):
        # Save action
        self.save_action = QAction('Save File', self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.save_action.triggered.connect(self.save_caption)

        # Open folder action
        self.open_folder_action = QAction('Open Folder', self)
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
                self.images = sorted(get_filenames(self.image_folder_path, content_type),key=custom_sort)
                for image in self.images:
                    self.images_list.addItem(image)

                self.current_image_index = 0
                self.image_count.setText(str(self.current_image_index))
                self.total_count.setText("/ " + str(len(self.images)))
                self.show_image(skip_option = "next")


    def show_image(self, chenge_index=True, skip_option=None):
        image_path = os.path.join(self.image_folder_path, self.images[self.current_image_index])

        # images_listのアイテムを検索し，選択状態にする
        items = self.images_list.findItems(self.images[self.current_image_index], Qt.MatchExactly)
        if items:
            item = items[0]
            self.images_list.setCurrentItem(item)

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

            if chenge_index:
                # テキストの表示
                text_path = os.path.join(self.text_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt").replace("gif","txt"))
                if os.path.isfile(text_path):
                    with open(text_path,mode="r") as f:
                        data = f.read()
                        self.caption.setText(data)
                else:
                    self.caption.setText("")

                # ラベルの表示
                label_path = os.path.join(self.label_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt").replace("gif","txt"))
                if os.path.isfile(label_path):
                    if skip_option is None or not self.skip_mode or (skip_option == "back" and len(self.images)==self.current_image_index+1) or (skip_option == "next" and self.current_image_index==0):
                        with open(label_path,mode="r") as f:
                            data = f.read()
                            self.label_edit.setText(data)
                    else:
                        if skip_option == "next":
                            self.next_image()
                        else:
                            self.back_image()
                else:
                    if skip_option is None or not self.skip_mode_exist or (skip_option == "back" and len(self.images)==self.current_image_index+1) or (skip_option == "next" and self.current_image_index==0):
                        self.label_edit.setText("")
                    else:
                        if skip_option == "next":
                            self.next_image()
                        else:
                            self.back_image()


    def draw_annotation(self,annotation_path, scale_factor_width, scale_factor_height):
        if os.path.exists(annotation_path):
            annotations = load_annotations(annotation_path)
            self.ann2bbox = {}
            self.bbox2ann = {}

            for annotation in annotations:
                if self.hide_flag and annotation["text"]=="###":
                    continue
                if len(annotation["bbox"]) == 4:
                    bbox = QRectF(annotation['bbox'][0]*scale_factor_width, annotation['bbox'][1]*scale_factor_height,\
                                    annotation['bbox'][2]*scale_factor_width, annotation['bbox'][3]*scale_factor_height)
                    ann_item = QGraphicsRectItem(bbox)
                else:
                    points = [QPointF(annotation['bbox'][i]*scale_factor_width, annotation['bbox'][i+1]*scale_factor_height) for i in range(0, len(annotation['bbox']), 2)]
                    polygon = QPolygonF(points)
                    ann_item = QGraphicsPolygonItem(polygon)

                ann_item.setPen(QPen(Qt.green))
                ann_item.setBrush(QBrush(QColor(0, 255, 0, 100)))

                ann = list(map(str,annotation.values()))
                self.annotation_list.addItem(",".join(ann))

                self.ann2bbox[",".join(ann)] = ann_item
                self.bbox2ann[ann_item] = ",".join(ann)

                if self.show_annotations:
                    self.scene.addItem(ann_item)

            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


    def next_image(self):
        if self.image_folder_path is not None:
            self.current_image_index += 1
            if self.current_image_index >= len(self.images):
                self.current_image_index = 0
            self.show_image(skip_option="next")


    def back_image(self):
        if self.image_folder_path is not None:
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.images) - 1
            self.show_image(skip_option="back")


    def show_selected_image(self, current_item, previous_item):
        if current_item is not None:
            selected_filename = current_item.text()
            self.current_image_index = self.images.index(selected_filename)
            self.show_image()


    def toggle_annotations(self):
        if self.image_folder_path is not None:
            self.show_annotations = not self.show_annotations
            self.show_image(chenge_index=False)

    def hide_annotations(self):
        if self.image_folder_path is not None:
            self.hide_flag = not self.hide_flag
            self.show_image(chenge_index=False)

    def skip_annotated_image(self):
        if not self.skip_mode_exist:
            self.skip_mode = not self.skip_mode
        else:
            self.toggle_skip.setChecked(False)

    def skip_annotated_image_exist(self):
        if not self.skip_mode:
            self.skip_mode_exist = not self.skip_mode_exist
        else:
            self.toggle_skip_exist.setChecked(False)

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


    def save_caption(self):
        if self.text_folder_path is not None and self.label_folder_path is not None:
            self.view.setFocus()
            caption_text = self.caption.toPlainText()
            text_path = os.path.join(self.text_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt").replace("gif","txt"))
            with open(text_path, 'w') as f:
                f.write(caption_text)

            label_text = self.label_edit.toPlainText()
            label_path = os.path.join(self.label_folder_path, self.images[self.current_image_index].replace("jpg","txt").replace("png","txt").replace("gif","txt"))
            with open(label_path, 'w') as f:
                f.write(label_text)


    def get_selected_annotation_word(self, item):
        text_ann = item.text().split(",")
        if len(text_ann[-1]) >= 1:
            text = text_ann[-1]
        else:
            text = text_ann[-2] + ","
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


    def get_now_filename(self, item):
        text = item.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


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
        self.toggle_skip.setGeometry(annotation_area_x + 100, 5, 100, 30)
        self.toggle_skip_exist.setGeometry(annotation_area_x + 200, 5, 100, 30)
        self.image_count.setGeometry(annotation_area_x, 5, 40, 30)
        self.total_count.setGeometry(annotation_area_x + 50, 5, 40, 30)

        # label
        self.label_label.setGeometry(annotation_area_x, 40, 60, 30)
        self.label_edit.setGeometry(annotation_area_x, 70, size.width() - (annotation_area_x + 10), 50)

        # caption
        self.caption_label.setGeometry(annotation_area_x, 120, 620, 30)
        self.caption.setGeometry(annotation_area_x, 150, size.width() - (annotation_area_x + 10), 50)

        # annotation一覧
        self.toggle_ann.setGeometry(annotation_area_x + 100, 200, 100, 30)
        self.annotation_label.setGeometry(annotation_area_x, 200, 620, 30)
        annotation_list_height = max(50, size.height()//2 - 240)
        self.annotation_list.setGeometry(annotation_area_x, 230, size.width() - (annotation_area_x + 10), annotation_list_height)

        # 画像一覧スクロール
        image_list_y = 230 + annotation_list_height + 10
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

    def mouseDoubleClickEvent(self, event):
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
                            self.get_selected_annotation_word(ann_items[0])
                        break


if __name__ == '__main__':
    app = QApplication([])
    image_annotator = ImageAnnotator()
    image_annotator.show()
    sys.exit(app.exec_())
