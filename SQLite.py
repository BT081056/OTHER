import sqlite3
import json
import os.path
import pandas as pd

#sqldb_path = 'sensor.db'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = BASE_DIR.replace('Lib','SQLiteDB')
db_path = os.path.join(BASE_DIR,"sensor.db")

print(db_path)



def InsertDataTabel(Tabel,InsertDataObj):
	
    print(Tabel)
    print(InsertDataObj)
    mydb=sqlite3.connect(db_path)
    cursor = mydb.cursor()
    # try:
    sql = f"INSERT INTO '{Tabel}' ("
    i=1
    for key,value in InsertDataObj.items():
        sql+=f"'{key}'"
        if len(InsertDataObj) != i:
            sql += f","
        else:
            sql +=f")"
        i+=1
    sql += " VALUES ("
    i=1
    for key,value in InsertDataObj.items():
        sql+=f"'{value}'"
        if len(InsertDataObj) != i:
            sql += f","
        else:
            sql +=f")"
        i+=1
    sql += ";"

    print(sql)
    cursor.execute(sql)
    mydb.commit()
    mydb.close()
    return sql
    # except:
    #     return False

	
	
def PDSelectWhereTabel(Table,WhereObj):
    mydb=sqlite3.connect(db_path)
    print(Table)
#    print(WhereObj)
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
#            print(sql)
#        print(sql)
        qdf = pd.read_sql_query(f"{sql}", mydb)

        mydb.close()
        qdf = json.loads(qdf.to_json(orient='records'))
        return qdf
    except:
        return False



def SENSOR_Top2(Table):
    mydb=sqlite3.connect(db_path)
    print(Table)
    try:
        sql = f"SELECT * from(SELECT * ,ROW_NUMBER() OVER (PARTITION BY sensor_no ORDER BY sensor_id desc) sn from %s)R where (R.sn=1 or R.sn=2 or R.sn=3) and sensor_type =4"%Table

        
        qdf = pd.read_sql_query(f"{sql}", mydb)
        print(qdf)
        mydb.close()
        qdf = json.loads(qdf.to_json(orient='records'))
        return qdf
    except:
        return False

if __name__ == '__main__':
    
#    Js = { "mac":"no1" ,"parameter":"Max", "value" : "10"}
#    print(Js['mac'])
#    InsertDataTabel('MacSpc',Js)### save to db
    BASE_DIR = BASE_DIR.replace('Lib','SQLiteDB')
    db_path = os.path.join(BASE_DIR,"sensor_sun.db")
    mydb=sqlite3.connect(db_path)
    cursor = mydb.cursor()
    Table = 'sensor_data2'
    #### Clear >10000
    sql = f"DELETE FROM sensor_data2 WHERE ((SELECT COUNT(sensor_id) AS rank FROM sensor_data2 AS temp WHERE  (temp.sensor_id > sensor_data2.sensor_id)) > 10000)"
    cursor.execute(sql)
    mydb.commit()
    mydb.close()