import os
import uuid
import datetime
import time
import shutil
import pickle

import cv2
import psycopg2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import starlette

# PostgreSQL configuration
DB_HOST = "attendance-system-rds.c5g22ewq4ztf.us-east-1.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "attendace_system"
DB_USER = "postgres"
DB_PASSWORD = "admin123"

# Directory paths
ATTENDANCE_LOG_DIR = './logs'
DB_PATH = './db'

# Create directories if they don't exist
for dir_ in [ATTENDANCE_LOG_DIR, DB_PATH]:
    if not os.path.exists(dir_):
        os.mkdir(dir_)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_postgres_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

def create_logs_table():
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id SERIAL PRIMARY KEY,
                user_name VARCHAR(255),
                timestamp TIMESTAMPTZ,
                status VARCHAR(50)
            )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def insert_log_into_db(user_name, timestamp, status):
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO attendance_logs (user_name, timestamp, status) 
            VALUES (%s, %s, %s)
            """, (user_name, timestamp, status))
            conn.commit()
    except Exception as e:
        print(f"Error inserting log into database: {e}")
    finally:
        conn.close()

@app.on_event("startup")
async def startup_event():
    create_logs_table()

@app.post("/login")
async def login(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    with open(file.filename, "wb") as f:
        f.write(contents)

    user_name, match_status = recognize(cv2.imread(file.filename))

    if match_status:
        timestamp = datetime.datetime.now()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        with open(os.path.join(ATTENDANCE_LOG_DIR, '{}.csv'.format(date)), 'a') as f:
            f.write('{},{},{}\n'.format(user_name, timestamp, 'IN'))
        insert_log_into_db(user_name, timestamp, 'IN')

    return {'user': user_name, 'match_status': match_status}

@app.post("/logout")
async def logout(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()


    with open(file.filename, "wb") as f:
        f.write(contents)

    user_name, match_status = recognize(cv2.imread(file.filename))

    if match_status:
        timestamp = datetime.datetime.now()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        with open(os.path.join(ATTENDANCE_LOG_DIR, '{}.csv'.format(date)), 'a') as f:
            f.write('{},{},{}\n'.format(user_name, timestamp, 'OUT'))
        insert_log_into_db(user_name, timestamp, 'OUT')

    return {'user': user_name, 'match_status': match_status}

@app.post("/register_new_user")
async def register_new_user(file: UploadFile = File(...), text=None):
    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    with open(file.filename, "wb") as f:
        f.write(contents)

    shutil.copy(file.filename, os.path.join(DB_PATH, f'{text}.png'))

    embeddings = face_recognition.face_encodings(cv2.imread(file.filename))

    with open(os.path.join(DB_PATH, f'{text}.pickle'), 'wb') as file_:
        pickle.dump(embeddings, file_)
    print(file.filename, text)

    os.remove(file.filename)

    return {'registration_status': 200}

@app.get("/get_attendance_logs")
async def get_attendance_logs():

    filename = 'out.zip'

    shutil.make_archive(filename[:-4], 'zip', ATTENDANCE_LOG_DIR)

    return starlette.responses.FileResponse(filename, media_type='application/zip', filename=filename)

def recognize(img):
    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found', False
    else:
        embeddings_unknown = embeddings_unknown[0]

    match = False
    j = 0

    db_dir = sorted([j for j in os.listdir(DB_PATH) if j.endswith('.pickle')])
    while not match and j < len(db_dir):

        path_ = os.path.join(DB_PATH, db_dir[j])

        with open(path_, 'rb') as file:
            embeddings = pickle.load(file)[0]

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]

        j += 1

    if match:
        return db_dir[j - 1][:-7], True
    else:
        return 'unknown_person', False
