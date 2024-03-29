# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 14:13:29 2023

@author: JohnnyCCHuang
"""
import cv2
import glob

path = "./my_output/*.jpg" 
result_name = 'output.mp4'

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
    # print("\rMaking videos: {}/{}".format(idx+1, len(frame_list)), end = "")
    current_frame = idx+1
    total_frame_count = len(frame_list)
    percentage = int(current_frame*30 / (total_frame_count+1))
    print("\rProcess: [{}{}] {:06d} / {:06d}".format("#"*percentage, "."*(30-1-percentage), current_frame, total_frame_count), end ='')
    out.write(frame)

out.release()
print("Finish making video !!!")
