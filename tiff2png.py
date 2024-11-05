# -*- encoding: utf-8 -*-
'''
@File    :   tiff2png.py
@Time    :   2024/11/05 08:58:17
@Author  :   Lewis
@Version :   1.0
@Contact :   lewis0808zy@gmail.com
@Desc    :   TiFF转PNG
'''


import os
from osgeo import gdal
import numpy as np
from PIL import Image
# 提取432三波段
from spectral import * 
# 输入文件夹路径
 
def get_img(dataset_img):
    width = dataset_img.RasterXSize  # 获取行列数
    height = dataset_img.RasterYSize
    bands = dataset_img.RasterCount  # 获取波段数
    # print("行数为：", height)
    # print("列数为：", width)
    # print("波段数为：", bands)
 
    proj = dataset_img.GetProjection()  # 获取投影信息
    # print("投影信息", proj)
    geotrans = dataset_img.GetGeoTransform()  # 获取仿射矩阵信息
    img = dataset_img.ReadAsArray(0, 0, width, height)
    new_img = np.transpose(img, (1, 2, 0))
    return new_img
 
def tiftopng(input_folder,output_folder,band=[3, 2, 1]):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 遍历输入文件夹中的.tif文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.tif'):
            # 构建输入文件的完整路径
            input_file = os.path.join(input_folder, file_name)
            # 打开.tif文件
            image = get_img(gdal.Open(input_file))
            # 创建输出文件的完整路径
            output_file = os.path.join(output_folder, file_name.replace('.tif', '.png'))
            spectral.settings.WX_GL_DEPTH_SIZE = 16
            # save_rgb(output_file, image, bands=[29, 3, 2], format='png')
            save_rgb(output_file, image, bands=band, format='png')
    print('完成一次转换！')
 
if __name__ == '__main__':
 
    y_path = "/mnt/sfs/shandong/algo/LZY/code/dataCreate/data540/X"
 
    out_path = "/mnt/sfs/shandong/algo/LZY/code/dataCreate/dataPNG"
 
    tiftopng(y_path, out_path, band=[3, 2, 1])