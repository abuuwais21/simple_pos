import psycopg2
from db import Db
from db.Db import ADMIN_M, PELANGGAN_M, LAUNDRY_M, JENISLAUNDRY_T, KETLAUNDRY_T, PARFUM_T, HANDSIGN_IMG_T
from werkzeug.security import safe_str_cmp
# import Db


def check_login_with_email_and_password(email, password):
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        # check_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE email = '{email}'"
        # cursor.execute(check_person_sql_query)
        cursor.execute(f"SELECT * FROM {ADMIN_M} WHERE email = %s", (email,))
        result = cursor.fetchall()
        if connDb:
            cursor.close()
            connDb.close()
            
        # print(result)
        if not result:
            return None
        else:
            real_user_password = result[0][3]
            # print()
            if safe_str_cmp(real_user_password.encode('utf-8'), password.encode('utf-8')):
                data_records_to_send = {}
                for record in result:
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
                    
                return data_records_to_send
            else:
                return None        
            
    except (Exception, psycopg2.DatabaseError) as e:
        print("Error DB: ", e)
        return None
        
        


def post(json_data):
    print("IN CREATE")
    sendback_json = {}
    sendback_json['response'] = ''
    if ('{' in json_data['username']) or ('}' in json_data['username']):
        sendback_json['response'] = 'error'
        sendback_json['why'] = '....'
        return sendback_json
    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        check_person_sql_query = f"SELECT * FROM {ADMIN_M} WHERE username = '{json_data['username']}'"
        cursor.execute(check_person_sql_query)
        result = cursor.fetchall()
        # If doesn't exist in DB, we create new data
        if not result:
            # dt_now = dt.now()
            data_insert = f"INSERT INTO public.{ADMIN_M} (username, name, password, email, created_on, last_login, uid_firebase) VALUES ('{json_data['username']}', '{json_data['name']}','{json_data['password']}','{json_data['email']}', TIMESTAMP '{json_data['created_on']}' ,TIMESTAMP '{json_data['created_on']}', '{json_data['uid_firebase']}') RETURNING *;"
            cursor.execute(data_insert)
            records = cursor.fetchall()
            connDb.commit()

            data_records_to_send = {}
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

            sendback_json['data'] = data_records_to_send
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
        return sendback_json

def get(uname, uid_firebs):
    sendback_json = {}
    sendback_json['response'] = ''

    try:
        connDb = Db.DATABASE_CONNECTION()
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
                    # in_data['password'] = record[3]
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
        #connDb.commit()
        if connDb:
           cursor.close()
           connDb.close()
        return sendback_json
    
def put(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    updated_data_list = json_data['updated_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json

def delete(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    deleted_data_list = json_data['deleted_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
            
        return sendback_json
