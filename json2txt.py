# -*- encoding: utf-8 -*-
'''
@File    :   json2txt.py
@Time    :   2024/11/05 16:37:29
@Author  :   Lewis
@Version :   1.0
@Contact :   lewis0808zy@gmail.com
@Desc    :   Json转yolo训练格式
'''



import os
import json
from PIL import Image, ImageDraw

json_folder = '/home/niubility/project/data/json'
labels_folder = '/home/niubility/project/data/labels'

# 遍历json文件夹
for json_file in os.listdir(json_folder):

    # 读取每个json文件
    with open(os.path.join(json_folder, json_file)) as f:
        instances = json.load(f)

    # 处理坐标
    all_coords = []
    for instance in instances['shapes']:
        coords = instance['points']
        instance_points = []
        for coord in coords:
            x, y = coord
            x /= instances['imageWidth']
            y /= instances['imageHeight']
            instance_points.append([x, y])
        all_coords.append(instance_points)

    # 写入labels文件夹
    json_name = os.path.splitext(os.path.basename(json_file))[0]
    
    label_file = os.path.join(labels_folder, json_name + '.txt')
    with open(label_file, 'w') as f:
        for coords in all_coords:
            if len(coords) == 0:
                continue
            f.write('0 ')
            for x, y in coords:
                f.write(f'{x} {y} ')
            f.write('\n')
