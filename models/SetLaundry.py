import psycopg2
from db import Db
from db.Db import ADMIN_M, PELANGGAN_M, LAUNDRY_M, JENISLAUNDRY_T, KETLAUNDRY_T, PARFUM_T, HANDSIGN_IMG_T
# import Db


def post(json_data, table_name):
    print("IN CREATE")
    if table_name == "":
        sendback_json = {}
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: Error no param'
        return sendback_json

    TABLE_NAME = ""
    if table_name == "jenislaundry":
        TABLE_NAME = JENISLAUNDRY_T
    elif table_name == "ketlaundry":
        TABLE_NAME = KETLAUNDRY_T
    elif table_name == "parfum":
        TABLE_NAME = PARFUM_T

    sendback_json = {}
    sendback_json['response'] = ''

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json
    

def get(json_data, table_name, q):

    if table_name == "":
        sendback_json = {}
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: Error no param'
        return sendback_json

    TABLE_NAME = ""
    if table_name == "jenislaundry":
        TABLE_NAME = JENISLAUNDRY_T
    elif table_name == "ketlaundry":
        TABLE_NAME = KETLAUNDRY_T
    elif table_name == "parfum":
        TABLE_NAME = PARFUM_T

    sendback_json = {}
    sendback_json['response'] = ''
    

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json
    

def put(json_data, table_name):
    if table_name == "":
        sendback_json = {}
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: Error no param'
        return sendback_json

    TABLE_NAME = ""
    if table_name == "jenislaundry":
        TABLE_NAME = JENISLAUNDRY_T
    elif table_name == "ketlaundry":
        TABLE_NAME = KETLAUNDRY_T
    elif table_name == "parfum":
        TABLE_NAME = PARFUM_T


    sendback_json = {}
    sendback_json['response'] = ''

    updated_data_list = json_data['updated_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json

def delete(json_data, table_name):
    if table_name == "":
        sendback_json = {}
        sendback_json['response'] = 'error'
        sendback_json['why'] = f'Exception: Error no param'
        return sendback_json

    TABLE_NAME = ""
    if table_name == "jenislaundry":
        TABLE_NAME = JENISLAUNDRY_T
    elif table_name == "ketlaundry":
        TABLE_NAME = KETLAUNDRY_T
    elif table_name == "parfum":
        TABLE_NAME = PARFUM_T


    sendback_json = {}
    sendback_json['response'] = ''

    deleted_data_list = json_data['deleted_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
            
        return sendback_json
