# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 13:49:44 2023

@author: JohnnyCCHuang
"""
import cv2
import numpy as np
import os
import glob

key_x1 = 0
key_y1 = 106
key_x2 = 640
key_y2 = 263

thold = 10
for videoFile in ['hookah.avi','Particle01.avi','Particle02.avi','Particle03.avi','Particle04.avi']:
    # 影片檔案
    # videoFile = "Particle01.avi"
    
    # 輸出目錄
    outputFolder = "%s_%s"%(videoFile.split('.')[0],thold)
    
    # 自動建立目錄
    if not os.path.exists(outputFolder):
      os.makedirs(outputFolder)
    
    # 開啟影片檔
    cap = cv2.VideoCapture(videoFile)
    
    # 取得畫面尺寸
    # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = key_x2 -key_x1
    height = key_y2 - key_y1
    
    # 計算畫面面積
    area = width * height
    
    # 初始化平均畫面
    ret, frame = cap.read()
    cut_frame = frame[key_y1:key_y2,key_x1:key_x2]
    avg = cv2.blur(cut_frame, (4, 4))
    avg_float = np.float32(avg)
    
    # 輸出圖檔用的計數器
    outputCounter = 0
    
    while(cap.isOpened()):
      # 讀取一幅影格
      ret, frame = cap.read()

      # 若讀取至影片結尾，則跳出
      if ret == False:
        break
      cut_frame = frame[key_y1:key_y2,key_x1:key_x2]        
      # 模糊處理
      blur = cv2.blur(cut_frame, (4, 4))
    
      # 計算目前影格與平均影像的差異值
      diff = cv2.absdiff(avg, blur)
    
      # 將圖片轉為灰階
      gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
      
      # 篩選出變動程度大於門檻值的區域
      ret, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
      # cv2.imwrite('aac.jpg',thresh)
      
      # 使用型態轉換函數去除雜訊
      kernel = np.ones((5, 5), np.uint8)
      thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
      thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
      # 產生等高線
      cntImg, cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
      hasMotion = False
      for c in cntImg:
        # 忽略太小的區域
        if cv2.contourArea(c) < thold:
          continue
    
        hasMotion = True
    
        # 計算等高線的外框範圍
        (x, y, w, h) = cv2.boundingRect(c)
    
        # 畫出外框
        cv2.rectangle(cut_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
      if hasMotion:
        # 儲存有變動的影像
        cv2.imwrite("%s/output_%04d.jpg" % (outputFolder, outputCounter), cut_frame)
        outputCounter += 1
    
      # 更新平均影像
      cv2.accumulateWeighted(blur, avg_float, 0.01)
      avg = cv2.convertScaleAbs(avg_float)
    
    cap.release()
    '''
    find jpg 2 mp4
    '''
    path = f"./{outputFolder}/*.jpg" 
    k1 = videoFile.split('.')[-1]
    result_name = 'output_%s_'%thold + videoFile.replace(k1,'mp4')
    
    frame_list = sorted(glob.glob(path))
    print("frame count: ",len(frame_list))
    
    fps = 30
    shape = cv2.imread(frame_list[0]).shape # delete dimension 3
    size = (shape[1], shape[0])
    print("frame size: ",size)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_name, fourcc, fps, size)
    
    for idx, path in enumerate(frame_list):
        frame = cv2.imread(path)
        os.remove(path)
        # print("\rMaking videos: {}/{}".format(idx+1, len(frame_list)), end = "")
        current_frame = idx+1
        total_frame_count = len(frame_list)
        percentage = int(current_frame*30 / (total_frame_count+1))
        print("\rProcess: [{}{}] {:06d} / {:06d}".format("#"*percentage, "."*(30-1-percentage), current_frame, total_frame_count), end ='')
        out.write(frame)
    
    out.release()
    print("Finish making video !!!")
