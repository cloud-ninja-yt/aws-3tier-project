import pymysql
from flask import Flask, jsonify
import os
import ssl
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# URL to download the SSL certificate bundle
ssl_cert_url = 'https://truststore.pki.rds.amazonaws.com/us-east-1/us-east-1-bundle.pem'
ssl_cert_path = '/home/ec2-user/ssl/us-east-1-bundle.pem'

# Ensure the directory exists
os.makedirs(os.path.dirname(ssl_cert_path), exist_ok=True)

# Download the SSL certificate bundle
response = requests.get(ssl_cert_url)
if response.status_code == 200:
    with open(ssl_cert_path, 'wb') as cert_file:
        cert_file.write(response.content)
    print(f"SSL certificate downloaded successfully to {ssl_cert_path}")
else:
    raise Exception(f"Failed to download SSL certificate bundle: {response.status_code}")

def get_db_connection(database=None):
    connection = pymysql.connect(host='database-1.cluster-c96ms4weicsz.us-east-1.rds.amazonaws.com',
                                 user='admin',
                                 password='_ycvZZV4gNt#R(?BB[T>-fob21w4',  # Your provided password
                                 database=database,
                                 ssl={'ca': ssl_cert_path})
    return connection

def create_database_and_tables():
    try:
        # Connect to the RDS instance without specifying a database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS corn_db')
        cursor.close()
        connection.close()
        print("Database 'corn_db' created successfully")

        # Connect to the newly created database
        connection = get_db_connection(database='corn_db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corn (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                characteristics TEXT NOT NULL,
                uses TEXT NOT NULL
            )
        ''')
        cursor.close()
        connection.close()
        print("Table 'corn' created successfully")
    except Exception as e:
        print(f"Error creating database or table: {e}")

def seed_database():
    try:
        connection = get_db_connection(database='corn_db')
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM corn')
        count = cursor.fetchone()[0]
        if count == 0:
            corn_types = [
                ("Dent Corn (Field Corn)", "Known for the dent that forms on the top of each kernel as it dries. It's primarily used for animal feed, ethanol production, and processed foods like corn syrup and cornmeal."),
                ("Sweet Corn", "This type has a higher sugar content, making it sweeter and more tender. It's the type we commonly eat as corn on the cob, or find canned and frozen."),
                ("Popcorn", "Popcorn has a hard outer shell and a starchy interior that 'pops' when heated. It's different from the corn we eat on the cob."),
                ("Flint Corn", "Known for its hard, glassy outer layer. It's often used for decorative purposes and in some traditional dishes."),
                ("Flour Corn", "This type has a soft, starchy kernel that's easy to grind into flour. It's commonly used in baking and for making corn tortillas."),
                ("Pod Corn", "An ancient variety where each kernel is enclosed in a husk. It's not commonly grown commercially.")
            ]
            cursor.executemany('''
                INSERT INTO corn (name, characteristics, uses)
                VALUES (%s, %s, %s)
            ''', [(name, characteristics, "") for name, characteristics in corn_types])
            connection.commit()
            print("Database seeded with initial corn types")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error seeding database: {e}")

@app.route('/corn', methods=['GET'])
def get_corn_entries():
    try:
        connection = get_db_connection(database='corn_db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM corn')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        corn_entries = []
        for row in rows:
            corn_entries.append({
                'id': row[0],
                'name': row[1],
                'characteristics': row[2],
                'uses': row[3]
            })

        return jsonify({'corn_entries': corn_entries})
    except Exception as e:
        print(f"Error retrieving corn entries: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        create_database_and_tables()
        seed_database()
    app.run(debug=True, host='0.0.0.0')