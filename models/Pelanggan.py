import psycopg2
from db import Db
from db.Db import ADMIN_M, PELANGGAN_M, LAUNDRY_M, JENISLAUNDRY_T, KETLAUNDRY_T, PARFUM_T, HANDSIGN_IMG_T, ADMIN_PELANGGAN_T
from werkzeug.security import safe_str_cmp

def check_exist_with_email_and_admin_id(email, admin_id):
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE email = '{email}'"
        cursor.execute(check_person_sql_query)
        result = cursor.fetchall()
        
        if result:
            pelanggan_id = result[0][0]
            check_person_sql_query = f"SELECT * FROM {ADMIN_PELANGGAN_T} WHERE pelanggan_id = {pelanggan_id} AND admin_id = {admin_id}"
            # check_person_sql_query = f"SELECT * FROM {ADMIN_PELANGGAN_T} WHERE pelanggan_id = {pelanggan_id}"
            cursor.execute(check_person_sql_query)
            result_admin_pelanggan = cursor.fetchall()
            
            if not result_admin_pelanggan:
                if connDb:
                    cursor.close()
                    connDb.close()
                return 2 # means email exist, but admin_id not exist
            
        if connDb:
            cursor.close()
            connDb.close()
            
        # print(result)
        if not result:
            return 0 # means email doesnt exist
        else:
            real_user_password = result[0][3]
            return 1 # emans email exist and admin_id        
            
    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        if connDb:
            cursor.close()
            connDb.close()
        return 0 # Errors
    
    

def check_login_with_email_and_password(email, password):
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE email = '{email}'"
        cursor.execute(check_person_sql_query)
        result = cursor.fetchall()
        
        if connDb:
            cursor.close()
            connDb.close()
            
        # print(result)
        if not result:
            return False # means email doesnt exist
        else:
            real_user_password = result[0][3]
            print()
            if safe_str_cmp(real_user_password.encode('utf-8'), password.encode('utf-8')):
                data_records_to_send = {}
                for record in result:
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
                return data_records_to_send
            else:
                return None        
            
    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        return False

def add_to_admin_pelanggan(json_data):
    sendback_json = {}
    sendback_json['response'] = ''
    ret = 200
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        
       
        check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE email = '{json_data['email']}'"
        cursor.execute(check_person_sql_query)
        result = cursor.fetchall()
        # If exist in DB, we create new data with different admin_id in admin_pelanggan_t
        if result:
            # dt_now = dt.now()
        
            data_insert = f"INSERT INTO public.{ADMIN_PELANGGAN_T} (admin_id, pelanggan_id) VALUES ({json_data['admin_id']}, {result[0][0]});"
            cursor.execute(data_insert)
            connDb.commit()


            # sendback_json['data'] = data_records_to_send
            sendback_json['response'] = 'success'
            sendback_json['why'] = 'success'
            ret = 200
        else:
            sendback_json['response'] = 'error'
            sendback_json['why'] = "email doesn't exist. Please choose other email."
            ret = 401

    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: {e}'
        ret = 401

    finally:
        if connDb:
            cursor.close()
            connDb.close()
        return sendback_json, ret
    
def post(json_data):
    # print("IN CREATE")
    sendback_json = {}
    sendback_json['response'] = ''
    ret = 200
    if ('{' in json_data['name']) or ('}' in json_data['name']):
        sendback_json['response'] = 'error'
        sendback_json['why'] = '.... {'
        return sendback_json, 401
    
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        
       
        # check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE email = '{json_data['email']}'"
        # cursor.execute(check_person_sql_query)
        # result = cursor.fetchall()
        # If doesn't exist in DB, we create new data
        # if not result:
            # dt_now = dt.now()
        data_insert = f"with data as (\
            INSERT INTO public.{PELANGGAN_M} (username, name, password, email, phone_number, created_on, last_login, uid_firebase) VALUES ('{json_data['username']}', '{json_data['name']}','{json_data['password']}','{json_data['email']}', '{json_data['phone_number']}', TIMESTAMP 'NOW()', TIMESTAMP 'NOW()', '{json_data['uid_firebase']}') returning pelanggan_id as id\
            ) \
            INSERT INTO public.{ADMIN_PELANGGAN_T} (admin_id, pelanggan_id) SELECT {json_data['admin_id']}, id \
            FROM data \
            RETURNING id"
        cursor.execute(data_insert)
        # records = cursor.fetchall()
        connDb.commit()
        
        # print(records)
        
        check_person_sql_query = f"SELECT * FROM {PELANGGAN_M} WHERE email = '{json_data['email']}'"
        cursor.execute(check_person_sql_query)
        records = cursor.fetchall()
        
        
        # data_insert = f"INSERT INTO public.{ADMIN_PELANGGAN_T} (admin_id, pelanggan_id) VALUES ({json_data['admin_id']}, {records[0][0]});"
        # cursor.execute(data_insert)
        # connDb.commit()

        data_records_to_send = {}
        for record in records:
            in_data = {}
            in_data['pelanggan_id'] = record[0]
            in_data['username'] = record[1]
            in_data['name'] = record[2]
            in_data['password'] = record[3]
            in_data['email'] = record[4]
            # in_data['created_on'] = record[5]
            # in_data['last_login'] = record[6]
            # in_data['uid_firebase'] = record[7]
            in_data['phone_number'] = record[8]
            data_records_to_send = in_data


        sendback_json['data'] = data_records_to_send
        sendback_json['response'] = 'success'
        sendback_json['why'] = 'success'
        ret = 200
        # else:
        #     sendback_json['response'] = 'error'
        #     sendback_json['why'] = 'username is already created. Please choose other username.'
        #     ret = 401

    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: {e}'
        ret = 401

    finally:
        if connDb:
            cursor.close()
            connDb.close()
        return sendback_json, ret

def get(uname, uid_firebs):
    sendback_json = {}
    sendback_json['response'] = ''
    
    ret = 200
    try:
        connDb = Db.DATABASE_CONNECTION()
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
                    # in_data['password'] = record[3]
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
                    # in_data['password'] = record[3]
                    in_data['email'] = record[4]
                    in_data['created_on'] = record[5]
                    in_data['last_login'] = record[6]
                    in_data['uid_firebase'] = record[7]
                    data_records_to_send.append(in_data)

            sendback_json['data'] = data_records_to_send
            sendback_json['response'] = 'success'
            sendback_json['why'] = 'success'
            ret = 200
        else:
            sendback_json['data'] = records
            sendback_json['response'] = 'error'
            sendback_json['why'] = "Can't find a record in DB."
            ret = 401

    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        sendback_json['data'] = []
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: {e}'
        ret = 401

    finally:
        connDb.commit()
        if connDb:
            cursor.close()
            connDb.close()
        return sendback_json, ret
    
def put(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    updated_data_list = json_data['updated_data']
    ret = 200
    try:
        connDb = Db.DATABASE_CONNECTION()
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
            ret = 200
        else:
            sendback_json['data'] = records
            sendback_json['response'] = 'error'
            sendback_json['why'] = "Can't updated record(s) in DB."
            ret = 401

    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        sendback_json['data'] = []
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: {e}'
        ret = 401

    finally:
        connDb.commit()
        if connDb:
            cursor.close()
            connDb.close()
        return sendback_json, ret

def delete(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    deleted_data_list = json_data['deleted_data']
    ret = 200
    try:
        connDb = Db.DATABASE_CONNECTION()
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
            ret = 200
        else:
            sendback_json['data'] = []
            sendback_json['response'] = 'error'
            sendback_json['why'] = "Can't updated record(s) in DB."
            ret = 401

    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        sendback_json['data'] = []
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: {e}'
        ret = 401

    finally:
        connDb.commit()
        if connDb:
            cursor.close()
            connDb.close()
            
        return sendback_json, ret
