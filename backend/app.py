import os
import sys
import json
import requests
import boto3
import pymysql
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

CORS(app, resources={r"*": {"origins": "*"}}, expose_headers="*", allow_headers="*")

# Configure logging
logging.basicConfig(filename='/var/log/backend.log', level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

# Function to retrieve the secret from AWS Secrets Manager
def get_secret(region_name):
    secret_name = os.getenv('SECRET_NAME')  # The name of your secret in AWS Secrets Manager

    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        
        # Parse the secret value
        secret = json.loads(get_secret_value_response['SecretString'])
        
        db_user = secret['username']  # Ensure the keys match the secret structure
        db_password = secret['password']
        
        return db_user, db_password

    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None, None

# Function to retrieve the region from EC2 instance metadata
def get_region():
    try:
        # Obtain a token
        token_response = requests.put(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
        )
        if token_response.status_code != 200:
            print(f"Error obtaining token: HTTP {token_response.status_code}")
            return None

        token = token_response.text

        # Use the token to get metadata
        response = requests.get(
            'http://169.254.169.254/latest/dynamic/instance-identity/document',
            headers={'X-aws-ec2-metadata-token': token}
        )
        if response.status_code == 200:
            metadata = response.json()
            return metadata['region']
        else:
            print(f"Error retrieving region: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print(f"Response content: {response.content}")
        return None

# Function to download the SSL certificate bundle
def download_ssl_cert(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as cert_file:
            cert_file.write(response.content)
        print(f"SSL certificate downloaded successfully to {path}")
    else:
        raise Exception(f"Failed to download SSL certificate bundle: {response.status_code}")

# Function to get a database connection
def get_db_connection(database=None):
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=database,
            ssl={'ca': ssl_cert_path}
        )
        logging.info("Database connection successful")
        return connection
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Function to create the database and tables
def create_database_and_tables():
    try:
        # Connect to the RDS instance without specifying a database
        connection = get_db_connection()
        if connection is None:
            logging.error("Failed to connect to database for seeding")
            return
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
                characteristics TEXT NOT NULL
            )
        ''')
        cursor.close()
        connection.close()
        print("Table 'corn' created successfully")
    except Exception as e:
        print(f"Error creating database or table: {e}")

# Function to seed the database with initial data
def seed_database():
    logging.info("Seeding database...")
    try:
        connection = get_db_connection(database='corn_db')
        if connection is None:
            logging.error("Failed to connect to database for seeding")
            return
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
                INSERT INTO corn (name, characteristics)
                VALUES (%s, %s)
            ''', corn_types)
            connection.commit()
            logging.info("Database seeded with initial corn types")
        else:
            logging.info("Database already seeded")
        cursor.close()
        connection.close()
    except Exception as e:
        logging.error(f"Error seeding database: {e}")

# Route to get corn entries
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
                'characteristics': row[2]
            })

        return jsonify({'corn_entries': corn_entries})
    except Exception as e:
        print(f"Error retrieving corn entries: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Retrieve the region from EC2 metadata
    region_name = get_region()
    if not region_name:
        print("Error retrieving region")
        sys.exit(1)

    # Retrieve secret values
    db_user, db_password = get_secret(region_name)

    # Database connection variables
    db_host = os.getenv('DB_HOST')
    ssl_cert_url = f'https://truststore.pki.rds.amazonaws.com/{region_name}/{region_name}-bundle.pem'
    ssl_cert_path = f'/home/ec2-user/ssl/{region_name}-bundle.pem'

    # Download SSL certificate bundle
    download_ssl_cert(ssl_cert_url, ssl_cert_path)

    # Create database and tables, and seed the database
    with app.app_context():
        create_database_and_tables()
        seed_database()

    # Route to handle POST request to add a new corn entry
    @app.route('/corn', methods=['POST'])
    def add_corn():
        data = request.get_json()
        name = data.get('name')
        characteristics = data.get('characteristics')
        try:
            connection = get_db_connection(database='corn_db')
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO corn (name, characteristics)
                VALUES (%s, %s)
            ''', (name, characteristics))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Corn entry added successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Route to handle DELETE request to delete a corn entry by id
    @app.route('/corn/<int:id>', methods=['DELETE'])
    def delete_corn(id):
        try:
            connection = get_db_connection(database='corn_db')
            cursor = connection.cursor()
            cursor.execute('DELETE FROM corn WHERE id = %s', (id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Corn entry deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    app.run(debug=True, host='0.0.0.0')