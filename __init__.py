# * ---------- IMPORTS --------- *

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import psycopg2
import cv2
import numpy as np
import re
import base64
from datetime import datetime as dt
import time
from dotenv import load_dotenv
import json
from configdb import ADMIN_M, PELANGGAN_M, LAUNDRY_M, JENISLAUNDRY_T, KETLAUNDRY_T, PARFUM_T, HANDSIGN_IMG_T
import configdb



load_dotenv('.env')

# Get the relativ path to this file (we will use it later)
#FILE_PATH = os.path.dirname(os.path.realpath(__file__))

# * ---------- Create App --------- *
app = Flask(__name__)
#CORS(app, support_credentials=True)
CORS(app)



# * ---------- DATABASE CONFIG --------- *
DATABASE_USER = os.environ['DATABASE_USER1']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD1']
DATABASE_HOST = os.environ['DATABASE_HOST1']
DATABASE_PORT = os.environ['DATABASE_PORT1']
DATABASE_NAME = os.environ['DATABASE_NAME1']

#print('DATABASE: ' + DATABASE_PASSWORD)

#DATABASE_USER ='itlaundrypos'
#DATABASE_PASSWORD = '160720' 
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '5432'
#DATABASE_NAME = 'laundrypos1'
def DATABASE_CONNECTION():
    return psycopg2.connect(user=DATABASE_USER,
                              host=DATABASE_HOST,
                              password=DATABASE_PASSWORD,
                              port=DATABASE_PORT,
                              database=DATABASE_NAME)


def get_img_np_jpgstr(image_str):
    jpg_or = base64.b64decode(image_str)
    jpg_np = np.frombuffer(jpg_or, dtype=np.uint8)
    img = cv2.imdecode(jpg_np, flags=1) 
    return img

def html(content):
    return '<html><head>Hi there...</head><body>' + content + '</body></html>'

@app.route('/api', methods=['GET'])
def test_root_api():
    return html('If you can see this, your server is running. Congrats')
        
        

@app.route("/api/v1/admins", methods=['POST','GET','PUT','DELETE'])
def admin_data():
    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = {}
        sendback_json['response'] = ''
        if ('{' in json_data['username']) or ('}' in json_data['username']):
            sendback_json['response'] = 'error'
            sendback_json['why'] = '....'
            return jsonify(sendback_json)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            check_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE username = '{json_data['username']}'"
            cursor.execute(check_person_sql_query)
            result = cursor.fetchall()
            # If doesn't exist in DB, we create new data
            if not result:
                # dt_now = dt.now()
                data_insert = f"INSERT INTO public.{ADMIN_M} (username, name, password, email, created_on, last_login, uid_firebase) VALUES ('{json_data['username']}', '{json_data['name']}','{json_data['password']}','{json_data['email']}', TIMESTAMP '{json_data['created_on']}' ,TIMESTAMP '{json_data['created_on']}', '{json_data['uid_firebase']}');"
                cursor.execute(data_insert)
                connDb.commit()

                sendback_json['data'] = json_data
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['response'] = 'error'
                sendback_json['why'] = 'username is already created. Please choose other username.'

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'GET':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''
        uname = request.args.get('username', default="", type=str)
        uid_firebs = request.args.get('uid_firebase', default="", type=str)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            get_person_sql_query = ""
            if(uname != ""):
                get_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE username = '{uname}' ORDER BY admin_id ASC"
            elif(uid_firebs != ""):
                get_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE uid_firebase = '{uid_firebs}' ORDER BY admin_id ASC"
            else:
                get_person_sql_query = f"SELECT * FROM {ADMIN_M} ORDER BY admin_id ASC"

            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()

            # If there are some records
            if records:
                # list_data = []
                data_records_to_send = []
                if uname!= "" or uid_firebs != "":
                    for record in records:
                        in_data = {}
                        in_data['admin_id'] = record[0]
                        in_data['username'] = record[1]
                        in_data['name'] = record[2]
                        in_data['password'] = record[3]
                        in_data['email'] = record[4]
                        in_data['created_on'] = record[5]
                        in_data['last_login'] = record[6]
                        in_data['uid_firebase'] = record[7]
                        data_records_to_send = in_data
                else:
                    for record in records:
                        in_data = {}
                        in_data['admin_id'] = record[0]
                        in_data['username'] = record[1]
                        in_data['name'] = record[2]
                        in_data['password'] = record[3]
                        in_data['email'] = record[4]
                        in_data['created_on'] = record[5]
                        in_data['last_login'] = record[6]
                        in_data['uid_firebase'] = record[7]
                        data_records_to_send.append(in_data)

                sendback_json['data'] = data_records_to_send
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't find a record in DB."
                
            if connDb:
                cursor.close()
                connDb.close()


        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            #connDb.commit()
            #if connDb:
            #    cursor.close()
            #    connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        updated_data_list = json_data['updated_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            admin_id_list = []
            for data in updated_data_list:
                admin_id_list.append(data['admin_id'])


            admin_id_tuple = tuple(admin_id_list)
            str_sql = ""
            if len(updated_data_list) == 1:
                str_sql = f"= {admin_id_tuple[0]}"
            elif len(updated_data_list) > 1:
                str_sql = f"IN {admin_id_tuple}"

            
            get_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE admin_id {str_sql}"
            # print(get_person_sql_query)
            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()



            # If there are some records
            if records:
                # print(records)
                
                str_sql = ""
                faces_str_sql = ""
                sql_query = ""
                
                if len(updated_data_list) == 1:
                    data1 = updated_data_list[0]
                    #print(f"facedata: {data1['facedata']}")
                    # data1['facedata'] 
                    str_sql = f"UPDATE {ADMIN_M} SET \
                                    username = '{data1['username']}', \
                                    name = '{data1['name']}', \
                                    password = '{data1['password']}', \
                                    email = '{data1['email']}', \
                                    last_login = now() \
                                WHERE admin_id = {data1['admin_id']};"
                    sql_query = f"{str_sql}"
                # elif len(updated_data_list) > 1:
                else:
                    users_list = []
                    res1 = ""
                    for data in updated_data_list:

                        user_list = []
                        user_list.append(data['admin_id'])
                        user_list.append(data['username'])
                        user_list.append(data['name'])
                        user_list.append(data['password'])
                        user_list.append(data['email'])
                        # user_list.append(configdb.format_date(data['created_on']))
                        # user_list.append(data['last_login'])
                        users_list.append(tuple(user_list))
                    
                    res = str(users_list)[1:-1]
                    str_sql = f"as u SET username = c.username, \
                                                name = c.name, \
                                                password = c.password, \
                                                email = c.email, \
                                                last_login = now() \
                            FROM (values \
                                    {res} ) as c(user_id, username, name, password, email) \
                            WHERE c.admin_id = u.admin_id"

                
                    # list_data = []
                    sql_query = f"UPDATE {ADMIN_M} {str_sql}"
                    # print(sql_query)

                cursor.execute(sql_query)
                records_updated_row = cursor.rowcount
                connDb.commit()


                sendback_json['data'] = f"Updated Row(s): {records_updated_row}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            #connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        deleted_data_list = json_data['deleted_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            admin_id_list = []
            for data in deleted_data_list:
                admin_id_list.append(data['admin_id'])


            admin_id_tuple = tuple(admin_id_list)
            str_sql = ""
            if len(deleted_data_list) == 1:
                str_sql = f" = {admin_id_tuple[0]}"
            elif len(deleted_data_list) > 1:
                str_sql = f"IN {admin_id_tuple}"

            get_person_sql_query = f"DELETE FROM {ADMIN_M} WHERE admin_id {str_sql}"
            cursor.execute(get_person_sql_query)
            # records_deleted_rows = cursor.rowcount
            connDb.commit()


            records_deleted_rows = len(deleted_data_list)
            # If there are some records
            if records_deleted_rows:
                print(records_deleted_rows)

                sendback_json['data'] = f"Deleted Row(s): {records_deleted_rows}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = []
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)


@app.route("/api/v1/pelanggans", methods=['POST','GET','PUT','DELETE'])
def pelanggan_data():
    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = {}
        sendback_json['response'] = ''
        if ('{' in json_data['username']) or ('}' in json_data['username']):
            sendback_json['response'] = 'error'
            sendback_json['why'] = '....'
            return jsonify(sendback_json)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE username = '{json_data['username']}'"
            cursor.execute(check_person_sql_query)
            result = cursor.fetchall()
            # If doesn't exist in DB, we create new data
            if not result:
                # dt_now = dt.now()
                data_insert = f"INSERT INTO public.{PELANGGAN_M} (username, name, password, email, created_on, last_login, uid_firebase) VALUES ('{json_data['username']}', '{json_data['name']}','{json_data['password']}','{json_data['email']}', TIMESTAMP '{json_data['created_on']}' ,TIMESTAMP '{json_data['created_on']}', '{json_data['uid_firebase']}');"
                cursor.execute(data_insert)
                connDb.commit()

                sendback_json['data'] = json_data
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['response'] = 'error'
                sendback_json['why'] = 'username is already created. Please choose other username.'

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'GET':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''
        uname = request.args.get('username', default="", type=str)
        uid_firebs = request.args.get('uid_firebase', default="", type=str)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            get_person_sql_query = ""
            if(uname != ""):
                get_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE username = '{uname}' ORDER BY pelanggan_id ASC"
            elif(uid_firebs != ""):
                get_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE uid_firebase = '{uid_firebs}' ORDER BY pelanggan_id ASC"
            else:
                get_person_sql_query = f"SELECT * FROM {PELANGGAN_M} ORDER BY pelanggan_id ASC"

            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()

            # If there are some records
            if records:
                # list_data = []
                data_records_to_send = []
                if uname!= "" or uid_firebs != "":
                    for record in records:
                        in_data = {}
                        in_data['pelanggan_id'] = record[0]
                        in_data['username'] = record[1]
                        in_data['name'] = record[2]
                        in_data['password'] = record[3]
                        in_data['email'] = record[4]
                        in_data['created_on'] = record[5]
                        in_data['last_login'] = record[6]
                        in_data['uid_firebase'] = record[7]
                        data_records_to_send = in_data
                else:
                    for record in records:
                        in_data = {}
                        in_data['pelanggan_id'] = record[0]
                        in_data['username'] = record[1]
                        in_data['name'] = record[2]
                        in_data['password'] = record[3]
                        in_data['email'] = record[4]
                        in_data['created_on'] = record[5]
                        in_data['last_login'] = record[6]
                        in_data['uid_firebase'] = record[7]
                        data_records_to_send.append(in_data)

                sendback_json['data'] = data_records_to_send
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't find a record in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        updated_data_list = json_data['updated_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            pelanggan_id_list = []
            for data in updated_data_list:
                pelanggan_id_list.append(data['pelanggan_id'])


            pelanggan_id_tuple = tuple(pelanggan_id_list)
            str_sql = ""
            if len(updated_data_list) == 1:
                str_sql = f"= {pelanggan_id_tuple[0]}"
            elif len(updated_data_list) > 1:
                str_sql = f"IN {pelanggan_id_tuple}"

            
            get_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE pelanggan_id {str_sql}"
            # print(get_person_sql_query)
            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()



            # If there are some records
            if records:
                # print(records)
                
                str_sql = ""
                faces_str_sql = ""
                sql_query = ""
                
                if len(updated_data_list) == 1:
                    data1 = updated_data_list[0]
                    #print(f"facedata: {data1['facedata']}")
                    # data1['facedata'] 
                    str_sql = f"UPDATE {PELANGGAN_M} SET \
                                    username = '{data1['username']}', \
                                    name = '{data1['name']}', \
                                    password = '{data1['password']}', \
                                    email = '{data1['email']}', \
                                    last_login = now() \
                                WHERE pelanggan_id = {data1['pelanggan_id']};"
                    sql_query = f"{str_sql}"
                # elif len(updated_data_list) > 1:
                else:
                    users_list = []
                    res1 = ""
                    for data in updated_data_list:

                        user_list = []
                        user_list.append(data['pelanggan_id'])
                        user_list.append(data['username'])
                        user_list.append(data['name'])
                        user_list.append(data['password'])
                        user_list.append(data['email'])
                        # user_list.append(configdb.format_date(data['created_on']))
                        # user_list.append(data['last_login'])
                        users_list.append(tuple(user_list))
                    
                    res = str(users_list)[1:-1]
                    str_sql = f"as u SET username = c.username, \
                                                name = c.name, \
                                                password = c.password, \
                                                email = c.email, \
                                                last_login = now() \
                            FROM (values \
                                    {res} ) as c(user_id, username, name, password, email) \
                            WHERE c.pelanggan_id = u.pelanggan_id"

                
                    # list_data = []
                    sql_query = f"UPDATE {PELANGGAN_M} {str_sql}"
                    # print(sql_query)

                cursor.execute(sql_query)
                records_updated_row = cursor.rowcount
                connDb.commit()


                sendback_json['data'] = f"Updated Row(s): {records_updated_row}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        deleted_data_list = json_data['deleted_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            pelanggan_id_list = []
            for data in deleted_data_list:
                pelanggan_id_list.append(data['pelanggan_id'])


            pelanggan_id_tuple = tuple(pelanggan_id_list)
            str_sql = ""
            if len(deleted_data_list) == 1:
                str_sql = f" = {pelanggan_id_tuple[0]}"
            elif len(deleted_data_list) > 1:
                str_sql = f"IN {pelanggan_id_tuple}"

            get_person_sql_query = f"DELETE FROM {PELANGGAN_M} WHERE pelanggan_id {str_sql}"
            cursor.execute(get_person_sql_query)
            # records_deleted_rows = cursor.rowcount
            connDb.commit()


            records_deleted_rows = len(deleted_data_list)
            # If there are some records
            if records_deleted_rows:
                print(records_deleted_rows)

                sendback_json['data'] = f"Deleted Row(s): {records_deleted_rows}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = []
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)


@app.route("/api/v1/laundries", methods=['POST','GET','PUT','DELETE'])
def laundries_data():
    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = {}
        sendback_json['response'] = ''

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            
            # dt_now = dt.now()
            # data_insert = f"INSERT INTO public.{LAUNDRY_M} (pelanggan_id, jenis_id, keterangan_id, handsign_img_id) VALUES ('{json_data['username']}', '{json_data['name']}','{json_data['password']}','{json_data['email']}', TIMESTAMP '{json_data['created_on']}' ,TIMESTAMP '{json_data['created_on']}', '{json_data['uid_firebase']}');"
            data_insert = f"with databaru as ( \
                INSERT INTO public.{HANDSIGN_IMG_T} DEFAULT VALUES RETURNING id\
            ) \
                INSERT INTO public.{LAUNDRY_M} (pelanggan_id, \
                    jenis_id, \
                    keterangan_id, \
                    total_rp, \
                    berat_kg, \
                    parfum_id, \
                    terima_date, \
                    selesai_date, \
                    handsign_img_id \
                )  SELECT \
                    {json_data['pelanggan_id']}, \
                        {json_data['jenis_id']},\
                        {json_data['keterangan_id']},\
                        {json_data['total_rp']}, \
                        {json_data['berat_kg']}, \
                        {json_data['parfum_id']},\
                        TIMESTAMP '{json_data['terima_date']}',\
                        TIMESTAMP '{json_data['selesai_date']}',\
                        databaru.id \
                 FROM databaru RETURNING *"
            cursor.execute(data_insert)
            results = cursor.fetchall()
            connDb.commit()

            data_records_to_send = {}
            for record in results:
                in_data = {}
                in_data['laundry_id'] = record[0]
                in_data['pelanggan_id'] = record[1]
                in_data['jenis_id'] = record[2]
                in_data['keterangan_id'] = record[3]
                in_data['total_rp'] = record[4]
                in_data['berat_kg'] = record[5]
                in_data['parfum_id'] = record[6]
                in_data['terima_date'] = record[7]
                in_data['selesai_date'] = record[8]
                in_data['created_on'] = record[9]
                in_data['handsign_img_id'] = record[10]
                in_data['is_active'] = record[11]
                data_records_to_send = in_data

            # json_data['handsign_img_id'] = results[0][0]
            sendback_json['data'] = data_records_to_send
            sendback_json['response'] = 'success'
            sendback_json['why'] = 'success'
            
        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'GET':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''
        q = request.args.get('q', default="", type=str)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            get_person_sql_query = ""
            if(q != ""):
                get_person_sql_query = f"SELECT * FROM {LAUNDRY_M} WHERE laundry_id = {q}"
            else:
                get_person_sql_query = f"SELECT * FROM {LAUNDRY_M} ORDER BY laundry_id ASC"

            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()

            # If there are some records
            if records:
                # list_data = []
                data_records_to_send = []
                if q!= "":
                    for record in records:
                        in_data = {}
                        in_data['laundry_id'] = record[0]
                        in_data['pelanggan_id'] = record[1]
                        in_data['jenis_id'] = record[2]
                        in_data['keterangan_id'] = record[3]
                        in_data['total_rp'] = record[4]
                        in_data['berat_kg'] = record[5]
                        in_data['parfum_id'] = record[6]
                        in_data['terima_date'] = record[7]
                        in_data['selesai_date'] = record[8]
                        in_data['created_on'] = record[9]
                        in_data['handsign_img_id'] = record[10]
                        in_data['is_active'] = record[11]
                        data_records_to_send = in_data
                else:
                    for record in records:
                        in_data = {}
                        in_data['laundry_id'] = record[0]
                        in_data['pelanggan_id'] = record[1]
                        in_data['jenis_id'] = record[2]
                        in_data['keterangan_id'] = record[3]
                        in_data['total_rp'] = record[4]
                        in_data['berat_kg'] = record[5]
                        in_data['parfum_id'] = record[6]
                        in_data['terima_date'] = record[7]
                        in_data['selesai_date'] = record[8]
                        in_data['created_on'] = record[9]
                        in_data['handsign_img_id'] = record[10]
                        in_data['is_active'] = record[11]
                        data_records_to_send.append(in_data)

                sendback_json['data'] = data_records_to_send
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't find a record in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        updated_data_list = json_data['updated_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            laundry_id_list = []
            for data in updated_data_list:
                laundry_id_list.append(data['laundry_id'])


            laundry_id_tuple = tuple(laundry_id_list)
            str_sql = ""
            if len(updated_data_list) == 1:
                str_sql = f"= {laundry_id_tuple[0]}"
            elif len(updated_data_list) > 1:
                str_sql = f"IN {laundry_id_tuple}"

            
            get_person_sql_query = f"SELECT * FROM {LAUNDRY_M} WHERE laundry_id {str_sql}"
            # print(get_person_sql_query)
            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()



            # If there are some records
            if records:
                # print(records)
                
                str_sql = ""
                faces_str_sql = ""
                sql_query = ""
                records_updated_row = 0
                if len(updated_data_list) == 1:
                    data1 = updated_data_list[0]
                    #print(f"facedata: {data1['facedata']}")
                    # data1['facedata'] 
                    str_sql = f"UPDATE {LAUNDRY_M} SET \
                                    pelanggan_id = {data1['pelanggan_id']}, \
                                    jenis_id = {data1['jenis_id']},\
                                    keterangan_id = {data1['keterangan_id']},\
                                    total_rp = {data1['total_rp']}, \
                                    berat_kg = {data1['berat_kg']}, \
                                    parfum_id = {data1['parfum_id']},\
                                    terima_date = TIMESTAMP '{data1['terima_date']}',\
                                    selesai_date = TIMESTAMP '{data1['selesai_date']}', \
                                    is_active = {data1['is_active']} \
                                WHERE laundry_id = {data1['laundry_id']};"
                    sql_query = f"{str_sql}"
                    cursor.execute(sql_query)
                    records_updated_row = cursor.rowcount
                    connDb.commit()
                # elif len(updated_data_list) > 1:
                    sendback_json['data'] = f"Updated Row(s): {records_updated_row}"
                else:
                    sendback_json['data'] = f"Not yet supported multiple PUT"    


                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        deleted_data_list = json_data['deleted_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            laundry_id_list = []
            for data in deleted_data_list:
                laundry_id_list.append(data['laundry_id'])


            laundry_id_tuple = tuple(laundry_id_list)
            str_sql = ""
            if len(deleted_data_list) == 1:
                str_sql = f" = {laundry_id_tuple[0]}"
            elif len(deleted_data_list) > 1:
                str_sql = f"IN {laundry_id_tuple}"

            get_person_sql_query = f"DELETE FROM {LAUNDRY_M} WHERE laundry_id {str_sql}"
            cursor.execute(get_person_sql_query)
            # records_deleted_rows = cursor.rowcount
            connDb.commit()


            records_deleted_rows = len(deleted_data_list)
            # If there are some records
            if records_deleted_rows:
                print(records_deleted_rows)

                sendback_json['data'] = f"Deleted Row(s): {records_deleted_rows}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = []
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)



@app.route("/api/v1/handsign", methods=['GET','PUT','DELETE'])
def handsign_data():
    #For POST METHOD, see def laundries_data():
    if request.method == 'GET':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''
        q = request.args.get('q', default="", type=str)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            sql_query = ""
            if(q != ""):
                sql_query = f"SELECT * FROM {HANDSIGN_IMG_T} WHERE id = {json_data['handsign_img_id']}"
            else:
                sql_query = f"SELECT * FROM {HANDSIGN_IMG_T} ORDER BY id ASC"

            cursor.execute(sql_query)
            records = cursor.fetchall()
            # connDb.commit()

            # If there are some records
            if records:
                # list_data = []
                data_records_to_send = []
                if q!= "":
                    for record in records:
                        in_data = {}
                        in_data['id'] = record[0]
                        in_data['tanda_terima_img'] = record[1]
                        in_data['tanda_selesai_img'] = record[2]
                        data_records_to_send = in_data
                else:
                    for record in records:
                        in_data = {}
                        in_data['id'] = record[0]
                        in_data['tanda_terima_img'] = record[1]
                        in_data['tanda_selesai_img'] = record[2]
                        data_records_to_send.append(in_data)

                sendback_json['data'] = data_records_to_send
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't find a record in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        updated_data_list = json_data['updated_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            handsign_img_id_list = []
            for data in updated_data_list:
                handsign_img_id_list.append(data['handsign_img_id'])


            handsign_img_id_tuple = tuple(handsign_img_id_list)
            str_sql = ""
            if len(updated_data_list) == 1:
                str_sql = f"= {handsign_img_id_tuple[0]}"
            elif len(updated_data_list) > 1:
                str_sql = f"IN {handsign_img_id_tuple}"

            
            get_person_sql_query = f"SELECT * FROM {HANDSIGN_IMG_T} WHERE id {str_sql}"
            # print(get_person_sql_query)
            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()



            # If there are some records
            if records:
                # print(records)
                
                str_sql = ""
                faces_str_sql = ""
                sql_query = ""
                records_updated_row = 0
                if len(updated_data_list) == 1:
                    data1 = updated_data_list[0]
                    #print(f"facedata: {data1['facedata']}")
                    # data1['facedata'] 
                    str_sql = f"UPDATE {HANDSIGN_IMG_T} SET \
                                    tanda_terima_img = '{data1['tanda_terima_img']}', \
                                    tanda_selesai_img = '{data1['tanda_selesai_img']}'\
                                WHERE id = {data1['handsign_img_id']};"
                    sql_query = f"{str_sql}"
                    cursor.execute(sql_query)
                    records_updated_row = cursor.rowcount
                    connDb.commit()
                # elif len(updated_data_list) > 1:
                    sendback_json['data'] = f"Updated Row(s): {records_updated_row}"
                else:
                    sendback_json['data'] = f"Not yet supported multiple PUT"    


                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        deleted_data_list = json_data['deleted_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            handsign_img_id_list = []
            for data in deleted_data_list:
                handsign_img_id_list.append(data['handsign_img_id'])


            handsign_img_id_tuple = tuple(handsign_img_id_list)
            str_sql = ""
            if len(deleted_data_list) == 1:
                str_sql = f" = {handsign_img_id_tuple[0]}"
            elif len(deleted_data_list) > 1:
                str_sql = f"IN {handsign_img_id_tuple}"

            get_person_sql_query = f"DELETE FROM {HANDSIGN_IMG_T} WHERE id {str_sql}"
            cursor.execute(get_person_sql_query)
            # records_deleted_rows = cursor.rowcount
            connDb.commit()


            records_deleted_rows = len(deleted_data_list)
            # If there are some records
            if records_deleted_rows:
                print(records_deleted_rows)

                sendback_json['data'] = f"Deleted Row(s): {records_deleted_rows}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = []
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)


@app.route("/api/v1/laundryset", methods=['POST','GET','PUT','DELETE'])
def laundries_setting_data():

    table_name = request.args.get('t', default="", type=str)
    if table_name == "":
        sendback_json = {}
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: Error no param'
        return jsonify(sendback_json)

    TABLE_NAME = ""
    if table_name == "jenislaundry":
        TABLE_NAME = JENISLAUNDRY_T
    elif table_name == "ketlaundry":
        TABLE_NAME = KETLAUNDRY_T
    elif table_name == "parfum":
        TABLE_NAME = PARFUM_T

    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = {}
        sendback_json['response'] = ''

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            data_insert = ""
            if (table_name == "jenislaundry") or (table_name == "ketlaundry"):
                data_insert = f" \
                    INSERT INTO public.{TABLE_NAME} (name, \
                        price, \
                        notes \
                    ) VALUES ('{json_data['name']}', \
                            {json_data['price']},\
                            '{json_data['notes']}') \
                            RETURNING *"

            elif table_name == "parfum":
                data_insert = f" \
                    INSERT INTO public.{TABLE_NAME} (name, \
                        notes \
                    ) VALUES ('{json_data['name']}', \
                            '{json_data['notes']}') \
                        RETURNING *"

            cursor.execute(data_insert)
            results = cursor.fetchall()
            connDb.commit()

            data_records_to_send = {}
            for record in results:
                in_data = {}
                in_data['id'] = record[0]
                in_data['name'] = record[1]
                in_data['notes'] = record[2]
                in_data['created_on'] = record[3]
                if table_name == "jenislaundry" or table_name == "ketlaundry":
                    in_data['price'] = record[4]
                data_records_to_send = in_data
            
            sendback_json['data'] = data_records_to_send
            sendback_json['response'] = 'success'
            sendback_json['why'] = 'success'
            
        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)


    elif request.method == 'GET':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''
        q = request.args.get('q', default="", type=str)

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()
            sql_query = ""
            if(q != ""):
                sql_query = f"SELECT * FROM {TABLE_NAME} WHERE id = {json_data['id']}"
            else:
                sql_query = f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC"

            cursor.execute(sql_query)
            records = cursor.fetchall()
            # connDb.commit()

            # If there are some records
            if records:
                # list_data = []
                data_records_to_send = []
                if q!= "":
                    for record in records:
                        in_data = {}
                        in_data['id'] = record[0]
                        in_data['name'] = record[1]
                        in_data['notes'] = record[2]
                        in_data['created_on'] = record[3]
                        if (table_name == "jenislaundry") or (table_name == "ketlaundry"):
                            in_data['price'] = record[4]
                        
                        data_records_to_send = in_data
                else:
                    for record in records:
                        in_data = {}
                        in_data['id'] = record[0]
                        in_data['name'] = record[1]
                        in_data['notes'] = record[2]
                        in_data['created_on'] = record[3]
                        if (table_name == "jenislaundry") or (table_name == "ketlaundry"):
                            in_data['price'] = record[4]
                        data_records_to_send.append(in_data)

                sendback_json['data'] = data_records_to_send
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't find a record in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        updated_data_list = json_data['updated_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            id_list = []
            for data in updated_data_list:
                id_list.append(data['id'])


            id_tuple = tuple(id_list)
            str_sql = ""
            if len(updated_data_list) == 1:
                str_sql = f"= {id_tuple[0]}"
            elif len(updated_data_list) > 1:
                str_sql = f"IN {id_tuple}"

            
            get_person_sql_query = f"SELECT * FROM {TABLE_NAME} WHERE id {str_sql}"
            # print(get_person_sql_query)
            cursor.execute(get_person_sql_query)
            records = cursor.fetchall()
            # connDb.commit()



            # If there are some records
            if records:
                # print(records)
                
                str_sql = ""
                faces_str_sql = ""
                sql_query = ""
                records_updated_row = 0
                if len(updated_data_list) == 1:
                    data1 = updated_data_list[0]
                    #print(f"facedata: {data1['facedata']}")
                    # data1['facedata'] 
                    if (table_name == "jenislaundry") or (table_name == "ketlaundry"):
                        str_sql = f"UPDATE {TABLE_NAME} SET \
                                    name = '{data1['name']}', \
                                    notes = '{data1['notes']}',\
                                    price = {data1['price']}\
                                WHERE id = {data1['id']};"

                    elif table_name == "parfum":
                        str_sql = f"UPDATE {TABLE_NAME} SET \
                                    name = '{data1['name']}', \
                                    notes = '{data1['notes']}'\
                                WHERE id = {data1['id']};"
                    
                    sql_query = f"{str_sql}"
                    cursor.execute(sql_query)
                    records_updated_row = cursor.rowcount
                    connDb.commit()
                # elif len(updated_data_list) > 1:
                    sendback_json['data'] = f"Updated Row(s): {records_updated_row}"
                else:
                    sendback_json['data'] = f"Not yet supported multiple PUT"    


                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = records
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = {}
        sendback_json['response'] = ''

        deleted_data_list = json_data['deleted_data']

        try:
            connDb = DATABASE_CONNECTION()
            cursor = connDb.cursor()

            id_list = []
            for data in deleted_data_list:
                id_list.append(data['id'])


            id_tuple = tuple(id_list)
            str_sql = ""
            if len(deleted_data_list) == 1:
                str_sql = f" = {id_tuple[0]}"
            elif len(deleted_data_list) > 1:
                str_sql = f"IN {id_tuple}"

            get_person_sql_query = f"DELETE FROM {TABLE_NAME} WHERE id {str_sql}"
            cursor.execute(get_person_sql_query)
            # records_deleted_rows = cursor.rowcount
            connDb.commit()


            records_deleted_rows = len(deleted_data_list)
            # If there are some records
            if records_deleted_rows:
                print(records_deleted_rows)

                sendback_json['data'] = f"Deleted Row(s): {records_deleted_rows}"
                sendback_json['response'] = 'success'
                sendback_json['why'] = 'success'
            else:
                sendback_json['data'] = []
                sendback_json['response'] = 'error'
                sendback_json['why'] = "Can't updated record(s) in DB."

        except (Exception, psycopg2.DatabaseError) as e:
            print("Error DB: ", e)
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = f'Exception: {e}'

        finally:
            connDb.commit()
            if connDb:
                cursor.close()
                connDb.close()

            return jsonify(sendback_json)

                                 
# * -------------------- RUN SERVER -------------------- *
if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    #app.run(host='127.0.0.1', port=5000, debug=True)
    #app.run(host='157.230.47.183',port=5023)

    #  * --- DOCKER PRODUCTION MODE: --- *
    # app.run(host='0.0.0.0', port=os.environ['PORT']) -> DOCKER
     app.run(port=os.environ['PORT1'],threaded=True)
