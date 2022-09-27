# * ---------- IMPORTS --------- *

from flask import Flask, request, jsonify, escape, make_response
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
    get_csrf_token
)
from requests import get
import datetime
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
from models import Admin, Pelanggan, Laundry, Handsign, SetLaundry
from firebase import firebase
from utils import utilrandom



load_dotenv('.env')

# Get the relativ path to this file (we will use it later)
#FILE_PATH = os.path.dirname(os.path.realpath(__file__))

# * ---------- Create App --------- *
app = Flask(__name__)
# CORS(app, support_credentials=True, origins=["*"], methods=["GET", "POST", "PUT", "DELETE"])
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}},
            # headers="Content-Type")
CORS(app, support_credentials=True, origins=["*"])
# CORS(app)

# CONFIG FOR FLASK-JWT-EXTENDED
# Configure application to store JWTs in cookies
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# Only allow JWT cookies to be sent over https. In production, this
# should likely be True
app.config['JWT_COOKIE_SECURE'] = False  

# Set the cookie paths, so that you are only sending your access token
# cookie to the access endpoints, and only sending your refresh token
# to the refresh endpoint. Technically this is optional, but it is in
# your best interest to not send additional cookies in the request if
# they aren't needed.
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

# Enable csrf double submit protection. See this for a thorough
# explanation: http://www.redotheweb.com/2015/11/09/api-security.html
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

# If the cookies should be session cookies (deleted when the browser 
# is closed) or persistent cookies (never expire). Defaults to True (session cookies).
app.config['JWT_SESSION_COOKIE'] = False
timedelta = datetime.timedelta(days=1)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta

# app.config['JWT_COOKIE_DOMAIN'] = "127.0.0.1 localhost dev.localhost localhost"

# Set the secret key to sign the JWTs with
# HOW TO GET SECRET KEY
# >>> import os
# >>> os.urandom(12).hex()
# 'f3cfe9ed8fae309f02079dbf'
app.config['JWT_SECRET_KEY'] = '7da35721eb85992ea79fcc2bd794c4a0'  # Change this!

jwt = JWTManager(app)


def get_img_np_jpgstr(image_str):
    jpg_or = base64.b64decode(image_str)
    jpg_np = np.frombuffer(jpg_or, dtype=np.uint8)
    img = cv2.imdecode(jpg_np, flags=1) 
    return img

def html(content):
    return '<html><head>Hi there...</head><body>' + content + '</body></html>'

SITE_NAME = "http://localhost:3000"

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def proxy(path):
#     return get(f'{SITE_NAME}{path}')


@app.route('/api', methods=['GET'])
def test_root_api():
    return html('If you can see this, your server is running. Congrats')
        
        
@app.route("/token/auth/admin/signup", methods=['POST'])
def signup_admin():
    if request.method == 'POST':
        # email = request.json.get('email', None)
        email = escape(request.json.get('email', None))
        password = escape(request.json.get('password', None))
        
        if not Admin.check_login_with_email_and_password(email, password):
            json_data = request.get_json()
            sendback_json = Admin.post(json_data)
            

            # timedelta = datetime.timedelta(minutes=1)
            # Create the tokens we will be sending back to the user
            # access_token = create_access_token(identity=email, expires_delta=timedelta)
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            
            # Set the JWTs and the CSRF double submit protection cookies
            # in this response
            signup = {}
            if sendback_json['response'] == 'error':
                signup['stat'] = False
            else:
                signup['stat'] = True
                signup['access_ct'] = get_csrf_token(access_token)
                signup['refresh_ct'] = get_csrf_token(refresh_token)
            
            response = jsonify({'signup': signup, 'data': sendback_json})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
            
            
        else:
            msg = {}
            msg['response'] = "Error"
            msg['why'] = "Failed signup with email and password"
            return jsonify({'signup': False, 'msg': msg}), 401
            
        
        
@app.route("/token/auth/admin/login", methods=['POST'])
def login_admin():
    if request.method == 'POST':
        # email = request.json.get('email', None)
        email = escape(request.json.get('email', None))
        password = escape(request.json.get('password', None))
        q_data = Admin.check_login_with_email_and_password(email, password)
        if not q_data:
            msg = {}
            msg['response'] = "Error"
            msg['why'] = "Failed login with email and password"
            return jsonify({'login': False, 'msg': msg}), 401
        else:
            # timedelta = datetime.timedelta(minutes=1)
            # Create the tokens we will be sending back to the user
            # access_token = create_access_token(identity=email, expires_delta=timedelta)
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            
            # Set the JWTs and the CSRF double submit protection cookies
            # in this response
            login = {}
            login['stat'] = True
            login['data'] = q_data
            login['access_ct'] = get_csrf_token(access_token)
            login['refresh_ct'] = get_csrf_token(refresh_token)
            response = jsonify({'login': login})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200



@app.route("/token/auth/pelanggan/signup", methods=['POST'])
def signup_pelanggan():
    if request.method == 'POST':
        # email = request.json.get('email', None)
        email = escape(request.json.get('email', None))
        password = escape(request.json.get('password', None))
        
        if not Pelanggan.check_login_with_email_and_password(email, password):
            json_data = request.get_json()
            sendback_json, ret = Pelanggan.post(json_data)
            # timedelta = datetime.timedelta(minutes=1)
            # Create the tokens we will be sending back to the user
            # access_token = create_access_token(identity=email, expires_delta=timedelta)
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            
            # Set the JWTs and the CSRF double submit protection cookies
            # in this response
            signup = {}
            if sendback_json['response'] == 'error':
                signup['stat'] = False
            else:
                signup['stat'] = True
                signup['access_ct'] = get_csrf_token(access_token)
                signup['refresh_ct'] = get_csrf_token(refresh_token)
            response = jsonify({'signup': signup, 'data': sendback_json})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, ret
            
            
        else:
            msg = {}
            msg['response'] = "Error"
            msg['why'] = "Failed signup with email and password"
            return jsonify({'signup': False, 'msg': msg}), 401
        
                
@app.route("/token/auth/pelanggan/login", methods=['POST'])
def login_pelanggan():
    if request.method == 'POST':
        # email = request.json.get('email', None)
        email = escape(request.json.get('email', None))
        password = escape(request.json.get('password', None))
        q_data = Admin.check_login_with_email_and_password(email, password)
        if not q_data:
            msg = {}
            msg['response'] = "Error"
            msg['why'] = "Failed login with email and password"
            return jsonify({'login': False, 'msg': msg}), 401
        else:
            # timedelta = datetime.timedelta(minutes=1)
            # Create the tokens we will be sending back to the user
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            
            # Set the JWTs and the CSRF double submit protection cookies
            # in this response
            login = {}
            login['stat'] = True
            login['data'] = q_data
            login['access_ct'] = get_csrf_token(access_token)
            login['refresh_ct'] = get_csrf_token(refresh_token)
            response = jsonify({'login': login})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
        
        
@app.route("/token/refresh", methods=['POST'])
@jwt_refresh_token_required
def refresh_admin():
    current_user = get_jwt_identity()
    # timedelta =datetime.timedelta(minutes=1)
    access_token = create_access_token(identity=current_user)
    
    #Set the access JWT and CSRF double submit protection cookies in this reponse
    response = jsonify({'refresh': True})
    set_access_cookies(response, access_token)
    return response, 200

@app.route("/token/remove", methods=['POST'])
def logout_admin():
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    return response, 200

@app.route("/api/example", methods=['GET'])
@jwt_required
def protected():
    email = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(email)}), 200

@app.after_request
def add_headers(resp):
    # resp.headers['Access-Control-Allow-Credentials']  = 'true'
    # resp.headers["Origin"] = "http://127.0.0.1:5000"
    # resp.headers["Referer"] = "http://127.0.0.1:5000"
#     resp.headers['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept, Access-Control-Allow-Origin, x-csrf_token,access-control-allow-credentials, xsrfHeaderName,xsrfCookieName,responseType, access_token_cookie"
    # resp.headers['Access-Control-Allow-Headers'] = "Content-Type, *"
    # resp.headers['Content-Type'] = 'application/json'
    # resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    # resp.headers['Access-Control-Allow-Methods'] = 'GET, POST,OPTIONS'
#     resp.headers['xsrfHeaderName'] = "XCSRF-TOKEN"
#     resp.headers['responseType'] = "json"
    return resp

@app.route("/api/v1/admins", methods=['POST','GET','PUT','DELETE'])
@jwt_required
def admin_data():
    if request.method == 'POST':
        json_data = request.get_json()
        sendback_json = Admin.post(json_data)
        return jsonify(sendback_json), 200
    
    elif request.method == 'GET':
        json_data = request.get_json()
        uname = escape(request.args.get('username', default="", type=str))
        uid_firebs = escape(request.args.get('uid_firebase', default="", type=str))
        sendback_json = Admin.get(uname, uid_firebs)
        
        return jsonify(sendback_json), 200
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = Admin.put(json_data)
        return jsonify(sendback_json), 200
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = Admin.delete(json_data)
        return jsonify(sendback_json), 200


@app.route("/api/v1/pelanggans", methods=['POST','GET','PUT','DELETE'])
@jwt_required
def pelanggan_data():
    if request.method == 'POST':
        json_data = request.get_json()
        res = Pelanggan.check_exist_with_email_and_admin_id(json_data['email'], json_data['admin_id'])
        if res == 0:
            json_data['username'] = utilrandom.generateUsername(json_data['name'])
            json_data['password'] = utilrandom.generatePassword()
            uid, ret = firebase.createUserFirebase(json_data)
            if(ret):
                json_data['uid_firebase'] = uid
                
                sendback_json, ret = Pelanggan.post(json_data)
                return jsonify(sendback_json), ret 
            else:
                resp = {}
                resp['error'] = "Fbase Error"
                return jsonify(resp), 401
        elif res == 2:
            sendback_json, ret = Pelanggan.add_to_admin_pelanggan(json_data)
            return jsonify(sendback_json), ret
        elif res == 1:
            resp = {}
            resp['error'] = "Error"
            return jsonify(resp), 401
    
    elif request.method == 'GET':
        json_data = request.get_json()
        uname = escape(request.args.get('username', default="", type=str))
        uid_firebs = escape(request.args.get('uid_firebase', default="", type=str))
        sendback_json, ret = Pelanggan.get(uname, uid_firebs)
        return jsonify(sendback_json), ret
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json, ret = Pelanggan.put(json_data)
        return jsonify(sendback_json), ret
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = Pelanggan.delete(json_data)
        return jsonify(sendback_json), ret


@app.route("/api/v1/laundries", methods=['POST','GET','PUT','DELETE'])
@jwt_required
def laundries_data():
    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = Laundry.post(json_data)
        return jsonify(sendback_json)
    
    elif request.method == 'GET':
        json_data = request.get_json()
        q = request.args.get('q', default="", type=str)
        sendback_json = Laundry.get(q)
        return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = Laundry.put(json_data)
        return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = Laundry.delete(json_data)
        return jsonify(sendback_json)



@app.route("/api/v1/handsign", methods=['GET','PUT','DELETE'])
@jwt_required
def handsign_data():
    #For POST METHOD, see def laundries_data():
    if request.method == 'GET':
        json_data = request.get_json()
        q = request.args.get('q', default="", type=str)
        sendback_json = Handsign.get(json_data, q)
        return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = Handsign.put(json_data)
        return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = Handsign.delete(json_data)
        return jsonify(sendback_json)


@app.route("/api/v1/laundryset", methods=['POST','GET','PUT','DELETE'])
@jwt_required
def laundries_setting_data():

    table_name = request.args.get('t', default="", type=str)
    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        sendback_json = SetLaundry.post(json_data, table_name)
        return jsonify(sendback_json)


    elif request.method == 'GET':
        json_data = request.get_json()
        q = request.args.get('q', default="", type=str)
        sendback_json = SetLaundry.get(json_data, table_name, q)
        return jsonify(sendback_json)
    
    elif request.method == 'PUT':
        json_data = request.get_json()
        sendback_json = SetLaundry.put(json_data, table_name)
        return jsonify(sendback_json)
    
    elif request.method == 'DELETE':
        json_data = request.get_json()
        sendback_json = SetLaundry.delete(json_data, table_name)
        return jsonify(sendback_json)

                                 
# * -------------------- RUN SERVER -------------------- *
if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    app.run(host='localhost', port=5000, debug=True)
    #app.run(host='157.230.47.183',port=5023)

    #  * --- DOCKER PRODUCTION MODE: --- *
    # app.run(host='0.0.0.0', port=os.environ['PORT']) -> DOCKER
    #  app.run(port=os.environ['PORT1'],threaded=True)
