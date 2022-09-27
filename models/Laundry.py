import psycopg2
from db import Db
from db.Db import ADMIN_M, PELANGGAN_M, LAUNDRY_M, JENISLAUNDRY_T, KETLAUNDRY_T, PARFUM_T, HANDSIGN_IMG_T
# import Db


def post(json_data):
    print("IN CREATE")
    sendback_json = {}
    sendback_json['response'] = ''

    try:
        connDb = Db.DATABASE_CONNECTION()
        cursor = connDb.cursor()
        
        # dt_now = dt.now()
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
        return sendback_json

def get(q):
    sendback_json = {}
    sendback_json['response'] = ''
    

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json
    
def put(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    updated_data_list = json_data['updated_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
        return sendback_json

def delete(json_data):
    sendback_json = {}
    sendback_json['response'] = ''

    deleted_data_list = json_data['deleted_data']

    try:
        connDb = Db.DATABASE_CONNECTION()
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
            
        return sendback_json
