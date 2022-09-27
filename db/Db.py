import os
import psycopg2
from dotenv import load_dotenv


ADMIN_M = "admin_m"
PELANGGAN_M = "pelanggan_m"
LAUNDRY_M = "laundry_m"
JENISLAUNDRY_T = "jenislaundry_t"
KETLAUNDRY_T = "keteranganlaundry_t"
PARFUM_T = "parfum_t"
HANDSIGN_IMG_T = "handsign_img_t"
ADMIN_PELANGGAN_T = "admin_pelanggan_t"


load_dotenv('.env')

DATABASE_USER = os.environ['DATABASE_USER1']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD1']
DATABASE_HOST = os.environ['DATABASE_HOST1']
DATABASE_PORT = os.environ['DATABASE_PORT1']
DATABASE_NAME = os.environ['DATABASE_NAME1']

def DATABASE_CONNECTION():
    return psycopg2.connect(user=DATABASE_USER,
                              host=DATABASE_HOST,
                              password=DATABASE_PASSWORD,
                              port=DATABASE_PORT,
                              database=DATABASE_NAME)

        
