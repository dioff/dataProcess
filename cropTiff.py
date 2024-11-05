# -*- encoding: utf-8 -*-
'''
@File    :   cropTiff.py
@Time    :   2024/11/04 23:06:39
@Author  :   Lewis
@Version :   1.0
@Contact :   lewis0808zy@gmail.com
@Desc    :   裁剪TIFF影像为自定义大小
'''

import os
import sys
try:
    import gdal
except:
    from osgeo import gdal

import numpy as np

from PIL import Image


def writeTiff(im_data, im_geotrans, im_proj, path):
    '''
    用于保存裁剪后的影像
    param: im_data:裁剪后的影像数据
    param: im_geotrans:地理坐标信息
    param: im_proj:投影信息
    param: path:保存路径
    '''
    datatype = gdal.GDT_Float32
    im_data = np.array([im_data])
    _, im_bands, im_height, im_width = im_data.shape
    
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
    
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[0, i])
    
    del dataset
    
def CoordTransf(Xpixel, Ypixel, GeoTransform):
    '''
    将像素坐标转换地理坐标
    param: Xpixel 和 Ypixel:像素坐标
    param: im_geotrans:地理坐标信
    '''
    XGeo = GeoTransform[0] + GeoTransform[1] * Xpixel + Ypixel *GeoTransform[2] 
    YGeo = GeoTransform[3] + GeoTransform[4] * Xpixel + Ypixel *GeoTransform[5]
    
    return XGeo, YGeo

def TifCrop(TifPath, SavePath, CropSize, RepetitionRate):
    '''
    将影像按指定尺寸和重叠率进行裁剪
    param: TifPath:裁Tiff图像路径
    param: SavePath:保存图像路径
    param: CropSize:裁剪大小
    param: RepetitionRate: 重叠率
    '''

    CropSize = int(CropSize)
    RepetitionRate = float(RepetitionRate)
    dataset_img = gdal.Open(TifPath)
    if dataset_img == None:
        print(TifPath + "该文件无法打开")
        
    if not os.path.exists(SavePath):
        os.makedirs(SavePath)
        
    
    width = dataset_img.RasterXSize
    height = dataset_img.RasterYSize
    bands = dataset_img.RasterCount
    
    print("行数为：", height)    
    print("列数为：", width)
    print("波段数为：", bands)
    
    proj = dataset_img.GetProjection()
    print("投影信息", proj)
    
    geotrans = dataset_img.GetGeoTransform()
    img = dataset_img.ReadAsArray(0, 0, width, height)
    
    for i in range(bands):
        band = dataset_img.GetRasterBand(i + 1)
        nodata_value = band.GetNoDataValue()
        band_data = band.ReadAsArray(0, 0, width, height)
        band_data[band_data == nodata_value] = 0
        img[i] = band_data
    
    #  行上图像块数目
    RowNum = int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))
    #  列上图像块数目
    ColumnNum = int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))
    print("裁剪后行影像数为：", RowNum)
    print("裁剪后列影像数为：", ColumnNum)
    
    # 获取当前文件夹的文件个数len,并以len+1命名即将裁剪得到的图像
    new_name = len(os.listdir(SavePath)) + 1
    
    
# 裁剪图片,重复率为RepetitionRate
    for i in range(RowNum):
        for j in range(ColumnNum):
            # 如果图像是单波段
            if (bands == 1):
                cropped = img[
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            # 如果图像是多波段
            else:
                cropped = img[:,
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            # 获取地理坐标
            XGeo, YGeo = CoordTransf(int(j * CropSize * (1 - RepetitionRate)),
                                     int(i * CropSize * (1 - RepetitionRate)),
                                     geotrans)
            crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
 
            # 生成Tif图像
            writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)
 
            # 文件名 + 1
            new_name = new_name + 1
            
            
    # 向前裁剪最后一行
    for i in range(RowNum):
        if (bands == 1):
            cropped = img[int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        else:
            cropped = img[:,
                      int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        # 获取地理坐标
        XGeo, YGeo = CoordTransf(width - CropSize,
                                 int(i * CropSize * (1 - RepetitionRate)),
                                 geotrans)
        crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
 
        # 生成Tif影像
        writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)
 
        new_name = new_name + 1
    # 向前裁剪最后一列
    for j in range(ColumnNum):
        if (bands == 1):
            cropped = img[(height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        else:
            cropped = img[:,
                      (height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        # 获取地理坐标
        XGeo, YGeo = CoordTransf(int(j * CropSize * (1 - RepetitionRate)),
                                 height - CropSize,
                                 geotrans)
        crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
        # 生成tif影像
        writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)
 
        # 文件名 + 1
        new_name = new_name + 1
    # 裁剪右下角
    if (bands == 1):
        cropped = img[(height - CropSize): height,
                  (width - CropSize): width]
    else:
        cropped = img[:,
                  (height - CropSize): height,
                  (width - CropSize): width]
 
    XGeo, YGeo = CoordTransf(width - CropSize,
                             height - CropSize,
                             geotrans)
    crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
    # 生成Tif影像
    writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)
 
    new_name = new_name + 1
 
if __name__ == '__main__':

    scale = 180
    x_path = '/mnt/sfs/shandong/algo/LZY/data/RIM/GF1_WFV2_GBAL_L2C_GLL_20230624_024218_0016M_MSS.TIFF'
    # y_path = path + '\Y\Y.tif'
    # z_path = path + '\Z\Z.tif'
 
    out_root = '/mnt/sfs/shandong/algo/LZY/code/dataCreate/data' + str(scale * 3)
    out_x = out_root + '/X'
    # out_y = out_root + '\Y'
    # out_z = out_root + '\Z_3'
 
    # TifCrop(y_path, out_y, scale * 3, 0)
    # TifCrop(z_path, out_z, scale, 0)
    TifCrop(x_path, out_x, scale * 3, 0)            
    