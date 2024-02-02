# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 15:26:30 2024

@author: JohnnyCCHuang
https://hackmd.io/@yizhewang/Bkd0EMyCm?type=view
https://hackmd.io/@yizhewang/By8Jb36mS
https://www.cnblogs.com/LXP-Never/p/11558302.html
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import numpy.fft as fft


def fft_ByFs(fs, L, data):
    fft_results = []
    for n in range(L//fs):
        data_seg = data[fs*n:fs*(n+1)]
        fft_result = np.fft.fft(data_seg)
        if fft_results ==[]:
            fft_results = fft_result
            continue
        fft_results = fft_results + fft_result
    return fft_results

for i, p, fs in os.walk(os.getcwd()):
    if '.csv' in fs:
        print(i,p,fs)
        break

fs.reverse()
Dic = {}
for f in fs:
    filename = os.path.join(i, f)
    # 读取时间和振动数据
    # time, vibration = np.loadtxt('data.txt', delimiter=',', unpack=True)
    if os.path.getsize(filename)>10000:
        newf = os.path.basename(f)
        data = pd.read_csv(filename)
        Dic[newf] = data


COLs = ['aX_M3', 'aY_M3', 'aZ_M3']
# COLs = ['aX_M3', 'aY_M3', 'aZ_M3']

C1S = []
C2 = []
for C1, data in Dic.items():
    for C2, data in Dic.items():
        
        if C1 == C2 or C1 in C1S:
            continue
        for COL in COLs:
                
            D1 = Dic[C1][COL]
            D2 = Dic[C2][COL]
            
            
            Xl = min(D2.__len__(), D1.__len__())
            x = range(0, Xl)
            plt.subplots(figsize=(10,8))
            plt.subplot(311)
            plt.title('{}  {} v.s. {}'.format(COL, C1, C2), color='limegreen')
            line1, = plt.plot(x, D1[:Xl], color='skyblue', label = C1)
            line2, = plt.plot(x, D2[:Xl], color='pink', label = C2)
            plt.legend(handles = [line1, line2], loc='upper right')
            
            ###################################

            
            
            data = D1[:Xl].copy()
            L = data.__len__()
            fs = 4000
            
            fft_results = fft_ByFs(fs, L, data)
            showdata = fft_results

            frequencies = np.fft.fftfreq(len(showdata), 1/fs)
            plt.subplot(312)
            plt.ylabel('Power')
            plt.tick_params(labelsize=10)
            plt.grid(linestyle=':')
            plt.plot(frequencies, np.abs(showdata))
            plt.legend()
            
            data = D2[:Xl].copy()
            fft_results = fft_ByFs(fs, L, data)
            showdata = fft_results

            frequencies = np.fft.fftfreq(len(showdata), 1/fs)
            plt.subplot(313)
            plt.ylabel('Power')
            plt.tick_params(labelsize=10)
            plt.grid(linestyle=':')
            plt.plot(frequencies, np.abs(showdata))
            plt.legend()
            
            ###################################
            
            plt.savefig('{}___{}_vs_{}.png'.format(COL, C1, C2))
            plt.show()
            plt.close()
        C1S.append(C1)

import numpy.fft as fft

data = D1[:8000]
L = data.__len__()
fs = 4000
T = 1/fs
t = [i*T for i in range(L)]
t = np.array(t)



###################################
plt.subplot(312)
S_ifft = fft.ifft(data)
# S_new是ifft变换后的序列
plt.plot(1000*t[1:51], S_ifft[1:51], label='S_ifft', color='orangered')
plt.xlabel("t（毫秒）")
plt.ylabel("S_ifft(t)幅值")
plt.title("ifft变换图")
plt.grid(linestyle=':')
plt.legend()

###################################
# 得到分解波的频率序列
freqs = fft.fftfreq(t.size, t[1] - t[0])
# 复数的模为信号的振幅（能量大小）
pows = np.abs(data)

plt.subplot(313)
plt.title('FFT变换,频谱图')
plt.xlabel('Frequency 频率')
plt.ylabel('Power 功率')
plt.tick_params(labelsize=10)
plt.grid(linestyle=':')
plt.plot(freqs[freqs > 0], pows[freqs > 0], c='orangered', label='Frequency')
plt.legend()


plt.tight_layout()
plt.show()



xfft = np.fft.rfft(data)
plt.figure(figsize = (12,8))
plt.hist(xfft)
plt.show()



            # fig,ax=plt.subplots(figsize=(10,5))
            # ax.plot(D1, color='skyblue', label=C1)
            # ax.set_ylabel(C1, color='skyblue', fontsize=20)
            # ax.tick_params(axis='y', labelcolor='skyblue')
            # plt.grid()
            # ax.legend(loc='upper left')
            
            # ax2=ax.twinx()
            # ax2.plot(D2, color='pink', label=C2)
            # ax2.set_ylabel(C2, color='pink', fontsize=20)
            # ax2.tick_params(axis='y', labelcolor='pink')
            # ax2.legend(loc='upper right')
            # plt.title('{} v.s. {}'.format(C1, C2), color='limegreen')



Dic[newf].columns

time = Dic[newf].datetime
vibration = Dic[f]['aX_M3']
time = range(0,vibration.__len__())
ee
# 绘制时域图
plt.plot(time, vibration)
plt.xlabel('Time (s)')
plt.ylabel('Vibration')
plt.show()


# 计算FFT
fft = np.fft.fft(vibration)

# 计算频率谱
freq = np.fft.fftfreq(len(vibration), time[1] - time[0])
freq = freq[:int(len(freq)/2)]

# 计算振幅谱
amp = np.abs(fft)[:int(len(fft)/2)] * 2 / len(vibration)

# 绘制频域图
plt.plot(freq, amp)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.show()

# x = np.linspace(xmin, xmax, num)     # 產生x
x = range(0,vibration.__len__())
F = vibration
U = Dic[f]['aX_M2']
# 建立繪圖物件 fig, 大小為 12 * 4.5, 內有 1 列 2 欄的小圖, 兩圖共用 x 軸和 y 軸
fig, (ax1, ax2) = plt.subplots(1, 2, sharex = True, sharey = True, figsize = (12, 4.5))

# 設定小圖 ax1 的坐標軸標籤, 格線顏色、種類、寬度, y軸繪圖範圍, 最後用 plot 繪圖
ax1.set_xlabel('r (m)', fontsize = 16)
ax1.set_ylabel('F (N)', fontsize = 16)
ax1.grid(color = 'red', linestyle = '--', linewidth = 1)
# ax1.set_ylim(0, 200)
ax1.plot(x, F, color = 'blue', linewidth = 3)

# 設定小圖 ax2 的坐標軸標籤, 格線顏色、種類、寬度, 最後用 plot 繪圖
ax2.set_xlabel('r (m)', fontsize = 16)
ax2.set_ylabel('U (J)', fontsize = 16)
ax2.grid(color = 'red', linestyle = '--', linewidth = 1)
ax2.plot(x, U, color = 'blue', linewidth = 3)

# 用 savefig 儲存圖片, 用 show 顯示圖片
fig.savefig('Fe_r_plot_2.png')
fig.show()



