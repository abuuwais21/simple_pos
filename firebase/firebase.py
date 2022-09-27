import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import os
from dotenv import load_dotenv

load_dotenv('../.env')

cred = credentials.Certificate(os.environ['LAUNDRYPOS_FIREBASE_KEY'])

firebase_admin.initialize_app(cred)

def createUserFirebase(json_data):
    email = json_data['email']
    phone_number = json_data['phone_number']
    password = json_data['password']
    newUser = auth.create_user(email=email, phone_number=phone_number, password=password)
    if(newUser):
        return newUser.uid, True
    else:
        return "Error", False
