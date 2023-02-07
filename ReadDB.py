import sqlite3
import json
import os.path
import pandas as pd
import numpy as np
#sqldb_path = 'sensor.db'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = BASE_DIR.replace('Lib','SQLiteDB')
db_path = os.path.join(BASE_DIR,"sensor.db")
db_path = '/home/pi/Desktop/flask_web/SQLiteDB/sensor.db'
print(db_path)
	
def double_linear(input_signal, zoom_multiples,n = 2):
    '''
    雙線性插值
    :param input_signal: 輸入圖像
    :param zoom_multiples: 放大倍數
    :return: 雙線性插值後的圖像
    '''
    input_signal_cp = np.copy(input_signal)   # 輸入圖像的副本

    input_row, input_col = input_signal_cp.shape # 輸入圖像的尺寸（行、列）

    # 輸出圖像的尺寸
    output_row = int(input_row * zoom_multiples)
    output_col = int(input_col * zoom_multiples)

    output_signal = np.zeros((output_row, output_col)) # 輸出圖片

    for i in range(output_row):
        for j in range(output_col):
            # 輸出圖片中座標 （i，j）對應至輸入圖片中的最近的四個點點（x1，y1）（x2, y2），（x3， y3），(x4，y4)的均值
            temp_x = i / output_row * input_row
            temp_y = j / output_col * input_col

            x1 = int(temp_x)
            y1 = int(temp_y)

            x2 = x1
            y2 = y1 + 1

            x3 = x1 + 1
            y3 = y1

            x4 = x1 + 1
            y4 = y1 + 1

            u = temp_x - x1
            v = temp_y - y1

            # 防止越界
            if x4 >= input_row:
                x4 = input_row - 1
                x2 = x4
                x1 = x4 - 1
                x3 = x4 - 1
            if y4 >= input_col:
                y4 = input_col - 1
                y3 = y4
                y1 = y4 - 1
                y2 = y4 - 1

            # 插值
            output_signal[i, j] = round((1-u)*(1-v)*float(input_signal_cp[x1, y1]) + (1-u)*v*float(input_signal_cp[x2, y2]) + u*(1-v)*int(input_signal_cp[x3, y3]) + u*v*int(input_signal_cp[x4, y4]),n)
    return output_signal

def PDSelectWhereTabel(Table,WhereObj):
    mydb=sqlite3.connect(db_path)
    print(Table)
    print(WhereObj)
    try:
        if WhereObj == None:
            sql =f"SELECT * from '{Table}'"
        else:
            sql = f"SELECT * from '{Table}' where "
            i=1
            for key,value in WhereObj.items():
                sql += f"{key} = '{value}' "
                if len(WhereObj) != i:
                    sql += f"and "
                else:
                    sql +=f";"
                i+=1
            print(sql)
        print(sql)
        qdf = pd.read_sql_query(f"{sql}", mydb)

        mydb.close()
        qdf = json.loads(qdf.to_json(orient='records'))
        return qdf
    except:
        return False

def FindMacSpc(mac):
    mydb=sqlite3.connect(db_path)
    print('check Mac',mac)
    try:
        sql = "select * from MacSpc where (mac='%s'and parameter='Max') order by input_time desc limit 1"%mac
        SpcMax = pd.read_sql_query(f"{sql}", mydb).value.values[0]
    except Exception as e:
        print(e)
        SpcMax = '-99'
    try:
        sql = "select * from MacSpc where (mac='%s'and parameter='Min') order by input_time desc limit 1"%mac
        SpcMin = pd.read_sql_query(f"{sql}", mydb).value.values[0]
    except:
        SpcMin = '-99'
    try:
        sql = "select * from MacSpc where (mac='%s'and parameter='Avg') order by input_time desc limit 1"%mac
        SpcAvg = pd.read_sql_query(f"{sql}", mydb).value.values[0]
    except:
        SpcAvg = '-99'
    print(SpcMax,SpcMin,SpcAvg)
    
    dic = {'Max':SpcMax,'Min':SpcMin,'Avg':SpcAvg}
    print(dic)
#    js = json.dumps(a)

    mydb.close()
#    qdf = json.loads(dic)
#    qdf = json.loads(dic)
    return dic


def SENSOR_Top2(Table):
    mydb=sqlite3.connect(db_path)
    print(Table)
    try:
        sql = f"SELECT * from(SELECT * ,ROW_NUMBER() OVER (PARTITION BY sensor_no ORDER BY sensor_id desc) sn from %s)R where (R.sn=1 or R.sn=2) and sensor_type =4"%Table

        
        qdf = pd.read_sql_query(f"{sql}", mydb)
        print(qdf)
        mydb.close()
        qdf = json.loads(qdf.to_json(orient='records'))
        return qdf
    except:
        return False


def All_mac():
    mydb=sqlite3.connect(db_path)
    try:
        sql = f"SELECT sensor_no as mac, MAX(sensor_id) FROM sensor_data2 GROUP BY sensor_no"
        snesofdf = pd.read_sql_query(f"{sql}", mydb)
        
        sql = f"SELECT mac,name,MAX(_id) FROM MacNo GROUP BY mac"
        nodf = pd.read_sql_query(f"{sql}", mydb)
        mydb.close()
        
        redf = pd.merge(snesofdf,nodf,how="left")
        
        redf = redf[['mac','name']]
        
        rdf = json.loads(redf.to_json(orient='records'))
        return rdf
    except Exception as e:
        return e

def SENSOR_TopN(mac,Days=30):
#    mac = "94:B9:7E:D3:22:14"
    try:
        mydb=sqlite3.connect(db_path)
        sql = "select * from sensor_data2 where (sensor_no='%s') order by input_time desc limit %s"%(mac,Days)
        df = pd.read_sql_query(f"{sql}", mydb)
        df_sort = df.sort_values(by = 'input_time')
        mydb.close()
        json_df = json.loads(df.to_json(orient='records'))
        return df_sort,json_df
    except:
        return False

def SENSOR_Top30(Table):
    mydb=sqlite3.connect(db_path)
    print(Table)
    TOPs = ''
    for i in range(1,31):
        TOPs = TOPs + 'R.sn=' + str(i) + ' or '
    TOPs2 = TOPs[:-4]
#    print(TOPs2)
    
    try:
        sql = f"SELECT * from(SELECT * ,ROW_NUMBER() OVER (PARTITION BY sensor_no ORDER BY sensor_id desc) sn from %s)R where (%s) and sensor_type =4"%(Table,TOPs2)

        
        df = pd.read_sql_query(f"{sql}", mydb)
        print(df)
        mydb.close()
        json_df = json.loads(df.to_json(orient='records'))
        return df,json_df
    except:
        return False

def Math_(LIST):
    count_ = 0
    for i in LIST:
        try:
            n = float(i)
            if count_ == 0:
                imax = n
                imin = n
                isum = 0
            if n > imax:
                imax = n
            if n < imin:
                imin = n
            isum = isum + n
            count_ = count_ +1
        except Exception as e:
            print('*************************************''',e)
        # print('ssssss',isum/count_)
    return imax,imin,isum/count_

def GetIRdata__(mac):
    mydb=sqlite3.connect(db_path)
    sql = "select * from sensor_data2 where (sensor_no='%s') order by input_time desc limit 1"%mac
    data = pd.read_sql_query(f"{sql}", mydb)
    mydb.close()
    Value = data['sensor_value'][0]
    dt = data['input_time'][0]
    return [{'sensor_no':mac,'sensor_value':Value,'input_time':dt}]

def GetIRdata(mac):
    mydb=sqlite3.connect(db_path)
    sql = "select * from sensor_data2 where (sensor_no='%s') order by input_time desc limit 1"%mac
    data = pd.read_sql_query(f"{sql}", mydb)
    mydb.close()
    Value = data['sensor_value'][0]
    dt = data['input_time'][0]
    k = 0
    j = 0
    Lsx = []
    LsAry = []
    for i in Value.split(','):
        try:
            fi = float(i)
            Lsx.append([j,k,fi])
            k = k + 1
            if k == 32:
                j = j+1
                k = 0
                LsAry.append(Lsx)
                Lsx = []
        except:
            pass

    return [{'sensor_no':mac,'sensor_value':LsAry,'input_time':dt}]

def GetIRdata_plus(mac):
    mydb=sqlite3.connect(db_path)
    sql = "select * from sensor_data2 where (sensor_no='%s') order by input_time desc limit 1"%mac
    data = pd.read_sql_query(f"{sql}", mydb)
    mydb.close()
    Value = data['sensor_value'][0]
    dt = data['input_time'][0]
    
    
    indata = Value.split(',')
    indata = list(map(float, indata))
    scale = 2

    ROWS = 32
    COLS = 24
    indata2D = np.reshape(indata, (COLS, ROWS))
    indata2D_T = indata2D.transpose()
    
    iframe = double_linear(indata2D,scale)
    
    Lsx = []
    LsAry = []
    Li,Lk = iframe.shape
    for i in range(Li):
        for k in range(Lk):
            Lsx.append([i,k,iframe[i,k]])
        LsAry.append(Lsx)
        Lsx = []

    return [{'sensor_no':mac,'sensor_value':LsAry,'input_time':dt}]


def Mixtemp(data):
    dts = []
    tempMaxs = []
    tempMins = []
    tempAvgs = []
    for i in data.index:
#        print(data_byNo.loc[i]['sensor_value'])
        temp = data.loc[i]['sensor_value']
        dts.append(data.loc[i]['input_time'])
        x,n,s = Math_(temp.split(','))
        tempMaxs.append(x)
        tempMins.append(n)
        tempAvgs.append(s)
    return dts,tempMaxs,tempMins,tempAvgs

if __name__ == '__main__':
#    print(All_mac())
#    Js = { "mac":"no1" , "Max" : "10"}
#    print(Js['mac'])
#    InsertDataTabel('MacSpc',Js)### save to db    
#    ee
#    import SQLiteLogicalInstruction

#        sql = f"SELECT * from(SELECT * ,ROW_NUMBER() OVER (PARTITION BY sensor_no ORDER BY sensor_id desc) sn from %s)R where (%s) and sensor_type =4"%(Table,TOPs2)

        
#    json_string = SQLiteLogicalInstruction.SENSOR_Top2('sensor_data2')
    MacNo = "94:B9:7E:D3:22:14"
    IrData = GetIRdata__(MacNo)
#    Days = 30
#    mydb=sqlite3.connect(db_path)
#    
#    sql = "select * from sensor_data2 where (sensor_no='%s') order by input_time desc limit %s"%(MacNo,Days)
#    SpcAvg = pd.read_sql_query(f"{sql}", mydb)
#
#    mydb.close()
#    
#    
#    data,json_df = SENSOR_Top30('sensor_data2')
#    data_byNo = data[data['sensor_no']==MacNo].sort_values(by = 'input_time')
#    dts,tempMaxs,tempMins,tempAvgs = Mixtemp(data_byNo)
    
#    with open('/home/pi/Desktop/flask_web/static/json_data.json', 'w') as outfile:
#        json.dumps(json_string, outfile)
#    
    
#    e
#    data = '27.05,26.70,26.89,26.62,26.27,26.58,26.10,26.83,26.67,26.40,26.30,26.67,26.53,26.65,26.43,26.61,26.45,26.65,26.66,26.66,26.55,26.65,26.73,27.03,26.87,26.53,27.05,26.74,26.84,26.38,27.47,27.48,27.48,26.89,26.59,26.43,26.68,26.46,26.16,26.43,26.56,26.37,26.65,26.36,26.47,26.62,26.37,26.79,26.75,26.62,26.61,26.57,26.31,26.98,26.84,27.07,26.74,26.42,26.86,27.43,27.15,26.81,26.70,27.33,26.55,26.46,26.32,26.27,26.30,25.97,26.37,26.84,26.22,26.38,26.91,26.66,26.53,26.63,26.40,26.43,26.57,26.71,26.55,26.74,26.88,26.54,26.74,26.77,26.85,26.78,26.84,26.81,26.44,26.49,27.11,26.93,26.20,26.35,26.55,26.31,26.13,26.33,26.28,26.17,26.40,26.45,26.46,26.47,26.70,26.36,26.55,26.80,26.48,26.42,26.72,26.70,26.78,26.58,26.52,26.81,26.69,26.98,26.84,26.95,26.61,26.88,26.91,27.71,26.54,26.09,26.31,26.79,25.98,26.11,26.46,26.27,26.58,26.40,26.47,26.39,26.53,26.51,26.50,26.85,26.42,26.59,26.70,26.55,26.74,26.32,26.63,26.81,26.68,26.63,26.88,26.65,26.50,26.90,27.35,27.22,26.52,26.30,26.13,26.29,25.73,26.43,26.25,26.34,26.27,26.44,26.41,26.31,26.47,26.45,26.45,26.59,26.46,26.52,26.50,26.81,26.76,26.66,26.75,27.06,26.92,26.67,26.74,27.18,26.47,27.03,27.31,27.19,26.22,26.43,26.18,26.41,26.48,26.23,26.49,26.29,26.41,26.54,26.66,26.40,26.52,26.18,26.58,26.78,26.65,26.64,26.74,26.58,26.71,26.36,26.69,26.60,26.75,26.66,27.08,26.59,26.76,26.86,27.26,27.02,26.69,25.94,26.14,26.14,26.33,26.49,26.46,26.55,26.31,26.54,26.46,26.73,26.50,26.58,26.67,26.53,26.47,26.61,26.56,26.71,26.41,26.69,26.78,26.92,26.83,26.82,26.92,26.85,26.56,26.84,26.69,26.96,26.18,26.38,26.33,26.34,26.46,26.23,26.27,26.55,26.36,26.60,26.54,26.47,26.48,26.43,26.58,26.59,26.52,26.58,26.70,26.27,26.84,26.57,26.60,26.92,26.58,26.73,26.70,26.86,27.10,27.12,27.32,26.72,26.64,26.52,26.58,26.33,26.53,26.34,26.25,26.79,26.35,26.41,26.05,26.58,26.56,26.62,26.66,26.49,26.60,26.50,26.50,26.76,26.78,26.57,26.60,26.57,26.53,27.07,26.40,27.21,27.04,26.95,26.92,27.28,26.68,26.49,26.20,26.26,26.21,26.32,26.23,26.30,26.42,26.42,26.40,26.67,26.56,26.63,26.46,26.48,26.62,26.63,26.60,26.53,26.52,26.85,26.71,26.67,26.83,26.60,26.90,26.90,26.98,26.60,27.16,27.07,26.10,26.34,26.27,26.71,26.42,26.31,26.32,26.41,26.41,26.41,26.55,26.67,26.35,26.46,26.41,26.65,26.49,26.61,26.65,26.77,26.57,26.66,26.55,26.64,26.76,26.57,26.84,26.85,26.86,27.11,27.21,27.49,26.61,26.21,26.27,26.47,26.19,26.41,26.66,26.55,26.38,26.49,26.39,26.55,26.40,26.48,26.64,26.50,26.52,26.31,26.48,26.70,26.52,26.54,26.64,26.77,26.65,26.87,26.83,26.50,27.01,26.95,26.80,27.34,26.31,26.45,26.46,26.25,26.44,26.37,26.28,26.63,26.31,26.44,26.60,26.77,26.48,26.53,26.75,26.72,26.71,26.72,26.81,26.80,26.52,26.52,26.56,26.80,26.67,26.60,26.83,26.89,26.78,26.98,27.16,27.37,26.07,26.71,26.26,26.65,26.60,26.41,26.42,26.44,26.63,26.45,26.59,26.77,26.74,26.37,26.35,26.68,26.63,26.35,26.58,26.63,26.76,26.61,26.78,26.45,26.76,26.53,26.84,27.11,26.93,27.02,26.94,27.41,26.62,26.35,26.62,26.54,26.61,26.45,26.21,26.59,26.52,26.79,26.59,26.71,26.38,26.65,26.76,26.51,26.59,26.74,26.65,26.72,26.75,26.44,26.65,26.96,26.76,26.87,26.81,27.26,26.79,27.23,27.14,26.99,26.59,26.70,26.66,26.80,26.64,26.37,26.50,26.51,26.62,26.59,26.64,26.80,26.50,26.58,26.62,26.58,26.57,26.49,26.66,26.67,26.80,26.68,26.78,27.01,26.77,26.76,26.71,26.78,27.00,26.77,27.51,26.99,26.90,26.93,26.47,26.87,26.51,26.41,26.57,26.64,26.61,26.31,26.32,26.82,26.66,26.67,26.59,26.54,26.62,26.51,26.61,26.76,26.66,26.77,26.85,26.82,26.83,26.87,26.95,26.94,26.86,26.89,26.89,27.33,27.07,26.95,27.17,27.11,26.62,26.92,26.49,26.67,26.25,26.26,26.54,26.60,26.79,26.46,26.61,26.56,26.85,26.77,26.71,26.75,26.65,26.68,26.75,26.79,26.95,26.64,26.96,26.78,26.64,26.84,27.12,27.22,26.89,27.17,26.71,27.15,26.85,26.82,26.82,26.68,26.66,26.71,26.49,26.78,26.33,26.66,26.57,26.84,26.68,26.66,26.55,26.89,26.58,26.64,26.68,26.97,26.88,26.62,26.91,27.20,26.76,26.71,27.27,27.05,27.16,27.22,27.86,27.29,26.96,26.85,26.55,26.68,26.56,26.79,27.01,26.88,26.74,26.72,26.65,26.77,26.59,26.77,26.79,26.66,26.90,26.89,26.61,26.93,26.73,26.91,26.93,26.87,27.35,26.89,27.35,27.29,26.77,28.04,27.20,28.75,27.07,27.27,26.92,27.44,27.07,26.87,27.27,26.95,26.98,27.11,26.88,26.92,26.71,26.73,26.75,27.04,26.82,26.74,26.89,26.78,27.05,26.99,26.77,26.97,26.99,27.19,26.72,27.28,28.73,28.47,29.27,28.73,28.44,28.30,28.23,27.74,27.65,27.49,27.46,27.48,26.91,26.77,27.08,26.78,26.76,26.72,26.85,26.48,26.92,26.69,26.97,26.77,26.84,26.92,26.99,26.90,27.17,26.47,27.49,27.73,29.33,29.80,29.07,30.09,28.37,28.90,28.28,28.38,27.80,27.68,27.22,27.28,26.64,26.76,26.71,27.02,26.81,26.83,26.86,27.18,26.78,26.90,26.82,26.79,26.92,26.80,26.85,26.96,26.81,27.27,26.83,27.93,'
#    waitTrans = data['sensor_value']

    
#    spc = FindMacSpc("94:B9:7E:D3:22:14")

#    print(spc['Max'])
#    data,json_df = SENSOR_Top30('sensor_data2')
#    print(data)
    
    
#    data_byNo = data[data['sensor_no']==data.head(1)['sensor_no'][0]]
#    dts,tempMaxs,tempMins,tempAvgs = Mixtemp(data_byNo)
    '''
    for nos in set(data['sensor_no']):
        data_byNo = data[data['sensor_no']==nos]
        dts = []
        tempMaxs = []
        tempMins = []
        for i in data_byNo.index:
            print(data_byNo.loc[i]['sensor_value'])
            temp = data_byNo.loc[i]['sensor_value']
            dts.append(data_byNo.loc[i]['input_time'])
            tempMaxs.append(finemax(temp.split(',')))
            tempMins.append(finemin(temp.split(',')))
    '''