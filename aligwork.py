# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 13:01:22 2023

--------------------  2023/09/05  --------------------
修改函式名稱
Fun1 >> getbase_position
修改getbase_position output 
原本 x,y,T/F
正常輸出 baseX,baseY, base – side
異常輸出 none,none,none

修改 fun2
def getlayer_position(layer,image,sider_ = '',DataName = '',save_path = '')
輸入的image可能是dict 或者 單個array_image
正常輸出 baseX,baseY, base – side
異常輸出 none,none,none

2023/09/06
修正 getlayer_position,getbase_position,check_theta,新增fun2

2023/09/18
1. 將key的照片增加解釋關鍵參數
2. func2 增加輸入 - save_path
2023/10/30
1. 新增方法2(遮罩比對),

2023/12/4
修正+模糊的5*5
2023/12/6
修改 check_theta的判斷機制
因為 下列不應該為 None
{'RL': [], 'RR': [[462.0, -345.0, 'R20_400_-330']], 'FL': [[-150.0, 101.0, 'R14_0_0']], 'FR': [[-151.0, -385.0, 'R21_0_-330']]}
(None, None, None)
"""
import os
import glob
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt



'''
二版
'''

def getIamgeKeyAxis(image_array,MatchImage,TopLeft):
    axisV,axisH = image_array.shape
    KeyImage_h,KeyImage_w = MatchImage.shape
    x1,y1 = TopLeft
    
    Ax_p = (x1 + (KeyImage_w/2)) - (axisH/2)
    Ay_p = (axisV/2) - (y1 + (KeyImage_h/2))

    # KeyX1 = int(round(x1 + KeyImage_w*0.5,0))
    # KeyY1 = int(round(y1 + KeyImage_h*0.5,0))
    return (Ax_p,Ay_p)

def Pixel2mm(DataName,image_array,KeyAxis):
    _,X,Y = DataName.split('.')[0].split('_')
    Image_h,Image_w = image_array.shape
    Ax_p,Ay_p = KeyAxis
    ### mmy
    p2m = 1.172
    # Ax_m = -round(Ax_p*p2m,0) + Image_w
    # Ay_m = -round(Ay_p*p2m,0) + Image_h
    ### mmy
    Ax_m = -round(Ax_p*p2m,0)
    Ay_m = -round(Ay_p*p2m,0)
    
    sy = int(Y)
    sx = int(X)
    
    return (sx-Ax_m,sy-Ay_m)


class layerworkV2():
    
    def __init__(self, LAYER, PR, MatchPath, SaveImage):
        self.SaveImage = SaveImage
        self.buffer_res = [0]
        self.buffer_template = []
        self.buffer_AnsName = ''
        self.buffer_Object = ''

        self.LAYER = LAYER
        self.PR = PR
        Threshold = {'R':0.7,'G':0.7,'B':0.7}
        self.LayerThreshold = Threshold[self.LAYER]
        self.sx = 0
        self.sy = 0
        self.GetTF = False
        ###將要偵測的Layer Ans都存入templateDic
        self.templateDic = {}
        print(f'{MatchPath}\Ans_{LAYER}*.jpg')
        CoinList = glob.glob(f'{MatchPath}\Ans_{LAYER}*{PR}*.jpg')
        if len(CoinList) == 0:
            CoinList = glob.glob(f'{MatchPath}\Ans_{LAYER}*.jpg')
        for CoinJPG in CoinList:
            img_rgb = cv2.imread(CoinJPG, 0)
            output2 = cv2.blur(img_rgb, (5, 5)) 
            self.templateDic[CoinJPG.split('\\')[-1]] = output2
        print(f'MatchDataSet Size: {len(self.templateDic)}')

    def ClearBuffer(self):
        self.buffer_res = [0]
        self.buffer_template = []
        self.buffer_AnsName = ''
        self.buffer_Object = ''
        
    def Process(self, ImageArray, DataName, sider, save_path = ''):
        GetTF = False
        AnsP = (0,0)
        Ax = len(ImageArray.shape)

        if Ax == 2:
            img_gray1 = ImageArray.copy()
        elif Ax == 3:
            img_gray1 = cv2.cvtColor(ImageArray, cv2.COLOR_BGR2GRAY)
        MaxRes = 0
        img_gray = cv2.blur(img_gray1, (5, 5)) 
        for AnsName,template in self.templateDic.items():
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            if np.max(res)>MaxRes:
                MaxRes = np.max(res)
                self.buffer_res = res
                self.buffer_template = template.copy()
                self.buffer_AnsName = AnsName
                # self.buffer_Object = DataName
                
        # print(np.max(self.buffer_res))
        if np.max(self.buffer_res) > self.LayerThreshold:
            GetTF = True
            loc = np.where(self.buffer_res == MaxRes)
            for pt in zip(*loc[::-1]):
                pass
            
            Pixel_Axis = getIamgeKeyAxis(img_gray,self.buffer_template,pt)
            AnsP = Pixel2mm(DataName,img_gray,Pixel_Axis)
            
            if self.SaveImage:
                template_h, template_w = self.buffer_template.shape[:2]
                bottom_right = (pt[0] + template_w, pt[1] + template_h)
                
                
                cv2.rectangle(ImageArray, pt, bottom_right, (0, 0, 255), 2)
                cv2.circle(ImageArray,getIamgeKeyAxis(template,pt),10, (0, 0, 255), 2)
                fig, axs = plt.subplots(2, 2, figsize=(10, 10))
                axs[0, 0].imshow(ImageArray, cmap='gray')
                axs[0, 0].set_title(DataName)
                axs[1, 0].set_title(np.max(res))
                axs[1, 1].set_title('Pixel_Axis: '+str(Pixel_Axis))
                axs[0, 1].imshow(res, cmap='gray')
                axs[1, 0].imshow(template, cmap='gray')
                axs[1, 1].imshow(ImageArray, cmap='gray')
                plt.show()
                plt.savefig(f'{self.LAYER}{time.time()}.jpg')
                plt.savefig(os.path.join(save_path,f'{sider}_{DataName}_key.jpg'))
                plt.close()
        return AnsP[0],AnsP[1],GetTF



'''
20230906
#### 單張張  getlayer_position產出
DDDDD = {'FL': [-49.0, 142.0, ''], 'FR': [-56.0, 118.0, ''], 'RL': [-13.0, 124.0, ''], 'RR': [-18.0, 103.0, '']}

#### 25張  getlayer_position產出
CF\230817\G1-2023-08-16 13-35-19_B14H43-AG2\
DDDDD = {'RL': [[477.0, -328.0, 'G20_400_-330']], 'RR': [[474.0, -303.0, 'G20_400_-330'], [530.0, -302.0, 'GH19_800_-330']], 'FL': [[506.0, -318.0, 'G20_400_-330']], 'FR': [[493.0, -290.0, 'G20_400_-330']]}

20230911
RL|RR
FL|FR

FL,FR的左右寫錯了進行修正
20230913
FR的位置計算錯誤 應該R-L 原本寫成 L-R
'''


def check_thetaAC2(center,total_side):
    Ans = None
    Trans = {}
    try:
        a = total_side['FR'][0][1]
        for key, value in total_side.items():
            if value != []:
                Trans[key] = value[0]
            else:
                Trans[key] = []
    except:
        pass
    if center == 'FR':
        Base = Trans['FR'][1]
        try:
            Side = Trans['RR'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
        except:
            Side = Trans['FR'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
    if center == 'RR':
        Base = Trans['RR'][1]
        try:
            Side = Trans['FR'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
        except:
            Side = Trans['RL'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = -abs(Ans)
            else:
                Ans = abs(Ans)
    if center == 'RL':
        Base = Trans['RL'][1]
        try:
            Side = Trans['FL'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
        except:
            Side = Trans['RR'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
    if center == 'FL':
        Base = Trans['FL'][1]
        try:
            Side = Trans['RL'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = abs(Ans)
            else:
                Ans = -abs(Ans)
        except:
            Side = Trans['FR'][1]
            Ans = Base - Side
            if Ans>0:
                Ans = -abs(Ans)
            else:
                Ans = abs(Ans)
                
                
    print(f"judge2 base ({center}) - side : {Ans}")
    return Ans





'''
20230906
####getlayer_position
輸入 : 製成別layer , 一張大圖切分四份(sider)
輸出 : 基準座標的x,y , 可旋轉角度
'''

def getlayer_position(layer,base_side,image_dict,DataName ='99_0_0',save_path = ''):
    
    SaveImage = False
    current_dir = os.path.dirname(os.path.abspath('__file__'))
    WorkAC = layerworkV2(layer,os.path.join(current_dir,"WORK_Ans"),SaveImage)
    
    
    if type(image_dict) == dict:
        for side,image_array in image_dict.items():
            layerinX,layerinY,TF = WorkAC.Process(image_array,DataName,side,save_path)
            if TF:
                image_dict[side] = [layerinX,layerinY,DataName]
            else:
                image_dict[side] = ['','','']
                
                
                
    try:
        THETA = check_thetaAC2(base_side,image_dict)
        print('-'*10,f'GOOD     Layer base {base_side} Data : ','-'*10,'\n',image_dict[base_side])
		#### x,y,theta
        return (image_dict[base_side][0],image_dict[base_side][1],THETA)
    except:
        print('-'*10,'FAILT**** Layer Data : ','-'*10)
        print(image_dict)
        return (None,None,None)
'''
20230906
####getbase_position
輸入 : 製成別layer , 一張大圖切分四份(sider),每份各25張
參數 : 道別_layer, 光阻_PR, 基準位_BaseSide, 照片集_ImageDict, 儲存位置_SaveFile
輸出 : 基準座標的x,y , 可旋轉角度
'''
### getbase_position
def getbase_position(layer, PR, base_side, dic_image, save_path = ''):
    
    SaveImage = False
    current_dir = os.path.dirname(os.path.abspath('__file__'))
    WorkAC = layerworkV2(layer, PR, os.path.join(current_dir,"WORK_Ans"), SaveImage)
    RCOL = ['RL','RR','FL','FR']
    ANS_image = {}
    total_side_dic = {}
    for sider_ in dic_image:
        result_out = []
        for DataName, image_array in dic_image[sider_].items():
            layerinX,layerinY,TF = WorkAC.Process(image_array,DataName,sider_,    )
                
            if TF:
                _,ox,oy = DataName.split('.')[0].split('_')
                result_out.append([layerinX,layerinY,DataName])
                ANS_image[sider_] = image_array
                try:
                    RCOL.remove(sider_)
                except:
                    pass
        total_side_dic[sider_] = result_out
        
        
    for se in RCOL:
        ANS_image[se] = np.ones(image_array.shape)*255
    
    if len(ANS_image) == 4:
        left_right1 = np.concatenate((ANS_image['RL'], ANS_image['RR']),axis = 1)
        left_right2 = np.concatenate((ANS_image['FL'], ANS_image['FR']),axis = 1)
        ImageMix = np.vstack((left_right1,left_right2))
        cv2.imwrite(os.path.join(save_path,'05_found_layer_work.jpg'),ImageMix)
        
        
    try:
        THETA = check_thetaAC2(base_side,total_side_dic)
        print('*'*10,f'GOOD     Layer base {base_side} Data : ','*'*10,'\n',total_side_dic[base_side][0])
        print(total_side_dic)
		#### x,y,theta
        return (total_side_dic[base_side][0][0],total_side_dic[base_side][0][1],THETA)
    except:
        print('*'*10,'FAILT**** Layer Data : ','*'*10)
        print(total_side_dic)
        return (None,None,None)


        
if __name__ == '__main__':
    #### 測試   getbase_position
    paths = r'D:\Share_Johnny\Project_python\CF'
    
    PR = 'T50'
    LAYER = 'R'
    filelist = glob.glob(os.path.join(paths, '230*\{}1*_{}\\'.format(LAYER, PR)))
    # paths = r'D:\Share_Johnny\Project_python\Wayne'
    # filelist = glob.glob(os.path.join(paths, '230908 AAS V2 Test\*RR\\'))
    for file in filelist:
        # jpglist = glob.glob(os.path.join(file,'\*\*.jpg'))
        # jpglist = glob.glob(os.path.join(paths, '230804\G1_2023-08-01 22-58-39_B120XAN41_MHG\*\*.jpg'))
        S4 = ['RL','RR','FL','FR']
        Dic_s4 = {}
        path = file.split('\\')[-2]
        for SSI in S4:
            # jpglist = glob.glob(os.path.join(paths,f'230804\G1_2023-08-01 22-58-39_B120XAN41_MHG\{SSI}\*.jpg'))
            jpglist = glob.glob(os.path.join(file,f'{SSI}\*.jpg'))
            Dic_ins = {}
            for your_image in jpglist:
                jpgname = your_image.split('\\')[-1][:-4]
                img = cv2.imread(your_image, cv2.IMREAD_GRAYSCALE)
                Dic_ins[jpgname] = img.copy()
                inds = jpgname.split('_')[0]
            Dic_s4[SSI] = Dic_ins
            
        t1 = time.time()
        timestamp = int(time.time())  # get current timestamp
        # plt.savefig(f'av2edges_mask_{DT}{SD}_{DataName}.jpg')
        print(f'Go Process {file}')
        print(getbase_position(LAYER, PR,'RR',Dic_s4,file))
        print(f'Function Use Time: {time.time()-t1} ms\n\n')
        
        
 
        
        
    #     image_dict['RL'][1]
'''
    #### 測試   getlayer_position
    ##  NG dataset
    filelist = glob.glob(os.path.join(paths, '230825\G1_2023-08-25 09-52-03_B15H4G_MHG\*\*01_*'))
    ##  OK dataset
    filelist = glob.glob(os.path.join(paths, '230817\G1-2023-08-16 13-12-22_B15H4G-MHG\*\*20_*'))
    Dic = {}
    for your_image in filelist:
        jpgname = your_image.split('\\')[-1][:-4]
        side = your_image.split('\\')[-2]
        img = cv2.imread(your_image, cv2.IMREAD_GRAYSCALE)
        Dic[side] = img.copy()
    getlayer_position('G','FR',Dic)
'''
