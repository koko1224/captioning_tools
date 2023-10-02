import os
import json
import re

# ファイル名をソートする関数
def custom_sort(file_name):
    # 数字のパターンにマッチする部分を検索
    match = re.search(r'(\D+)(\d+)', file_name)

    # マッチしなかった場合はファイル名全体を返す
    if match:
        prefix, number = match.groups()
    else:
        prefix = file_name
        number = ""

    # プレフィックスでソートし、次に数値でソート
    return (prefix, int(number))

def check_directory_type(path):
    """
    引数で渡したディレクトリの種類が以下のどちらかを判定する
        - 画像のみが格納されているディレクトリ
        - Train, Testのディレクトリが存在し, 画像が格納されているディレクトリ

    :param path: ディレクトリのパス
    """

    # ディレクトリ内の全ての子要素を取得
    contents = os.listdir(path)
    if ".DS_Store" in contents:
        contents.remove(".DS_Store")

    has_directory = False
    has_file = False

    for item in contents:
        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            has_directory = True
        elif os.path.isfile(item_path):
            has_file = True

    if has_directory and (not has_file):
        return "directory"
    if has_file and (not has_directory):
        return "file"
    else:
        raise Exception("Invalid directory type")


def get_filenames(folder_path, content_type):
    """
    folderに格納されているファイル名を全て取得する

    :param folder_path: フォルダのパス
    :param content_type: フォルダ内のファイルの種類
    """
    if content_type == "file":
        filenames = os.listdir(folder_path)
        if ".DS_Store" in filenames:
            filenames.remove(".DS_Store")
        return filenames
    else:
        contents = os.listdir(folder_path)
        if ".DS_Store" in contents:
            contents.remove(".DS_Store")
        filenames = []
        for content in contents:
            filenames_tmp = get_filenames(os.path.join(folder_path, content), "file")
            filenames_tmp = [os.path.join(content, filename) for filename in filenames_tmp]
            filenames.extend(filenames_tmp)
        return filenames


def get_textfolder(folder_path):
    """
    テキストファイルが格納されているフォルダのパスを取得する

    :param folder_path: フォルダのパス
    """
    contents = sorted(os.listdir(folder_path))
    for content in contents:
        if "text" in content:
            return os.path.join(folder_path,content)
    return os.path.join(folder_path, 'text')


def get_annotation_path(folder_path):
    """
    アノテーションファイルのパスの型を作成する
    対応済み
        - textseg
        - Total-Text
        - IIIT5K
        - icdar2013
        - icdar2017

    :param folder_path: フォルダのパス
    """
    if "textseg" in folder_path:
        return os.path.join(folder_path, "annotation","%s_anno.json")
    elif "Total-Text" in folder_path:
        return os.path.join(folder_path, "annotation", "groundtruth_polygonal_annotation","%s","poly_gt_%s.txt")
    elif "IIIT5K" in folder_path:
        return os.path.join(folder_path, "annotation", "label", "%s", "%s.txt")
    elif "icdar" in folder_path and "2013" in folder_path:
        return os.path.join(folder_path, "annotation", "%s", "gt_%s.txt")
    elif "icdar" in folder_path and "2017" in folder_path:
        return os.path.join(folder_path, "annotation", "gt_%s.txt")
    else:
        raise Exception("This dataset is not supported")


def load_annotations(annotation_path):
    """
    annotationを読み込む
    対応済みデータセットはget_annotation_pathと同じ

    :param annotation_path: アノテーションファイルのパス
    """
    annotations = []
    if "textseg" in annotation_path:
        data = json.load(open(annotation_path, 'r'))
        for key in data.keys():
            points = data[key]["bbox"]
            annotations.append({'bbox': points, "text": data[key]["text"].lower()})
    elif "Total-Text" in annotation_path:
        with open(annotation_path, "r") as f:
            data = f.readlines()

            for ann in data:
                try:
                    ann = ann.strip().replace("\n","").split(", ")
                    x = [int(value) for value in ann[0].split(": ")[-1].strip('[ ]').split()]
                    y = [int(value) for value in ann[1].split(": ")[-1].strip('[ ]').split()]
                    text = (ann[3].split(": ")[-1].replace(" ", ","))[3:-2]
                except:
                    print(ann)
                    ann
                    exit()
                annotations.append({'bbox': [value for pair in zip(x, y) for value in pair], "text": text.lower()})
    elif "IIIT5K" in annotation_path:
        with open(annotation_path, "r") as f:
            ann = f.read()
            for a in ann.strip().split("\n"):
                bbox = list(map(int,a.split(" ")[:4]))
                text = a.split(" ")[-1]
                annotations.append({'bbox': bbox, "text": text.lower()})

    elif "icdar" in annotation_path and "2013" in annotation_path:
        if "train" in annotation_path:
            with open(annotation_path, "r") as f:
                ann = f.read()
                for a in ann.strip().split("\n"):
                    bbox = list(map(int,a.split(" ")[:4]))
                    bbox[2] -= bbox[0]
                    bbox[3] -= bbox[1]
                    text = a.split(" ")[-1][1:-1]
                    annotations.append({'bbox': bbox, "text": text.lower()})
        else:
            with open(annotation_path, "r") as f:
                ann = f.read()
                for a in ann.strip().split("\n"):
                    bbox = list(map(int,a.split(",")[:8]))
                    text = a.split(",")[-1]
                    annotations.append({'bbox': bbox, "text": text.lower()})

    elif "icdar" in annotation_path and "2017" in annotation_path:
        with open(annotation_path, "r") as f:
            ann = f.read()
            for a in ann.strip().split("\n"):
                a = a.split(",")
                bbox = list(map(int,a[:8]))
                text = ",".join(a[9:])
                annotations.append({'bbox': bbox, "text": text.lower()})

    return annotations
