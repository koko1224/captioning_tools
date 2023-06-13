import os
import json
import re

def get_filenames(folder_path):
    filenames = []
    contents = os.listdir(folder_path)

def get_textfolder(folder_path):
    contents = sorted(os.listdir(folder_path))
    for content in contents:
        if "text" in content:
            return os.path.join(folder_path,content)
    return os.path.join(folder_path, 'text')

def get_annotation_dir(folder_path):
    ann_dir = os.path.join(folder_path, "annotation")
    contents = os.listdir(ann_dir)
    

def load_annotations(annotation_path):
    annotations = []
    if "textseg" in annotation_path:
        data = json.load(open(annotation_path, 'r'))
        for key in data.keys():
            points = data[key]["bbox"]
            annotations.append({'bbox': points, "text": data[key]["text"]})
    
    if "Total-Text" in annotation_path:
        pass

    return annotations