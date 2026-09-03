from flask import Flask, jsonify
import psycopg2
import os
import random
import socket
import json
from datetime import datetime

app = Flask(__name__)

def log(message):
    print(json.dumps({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }))


db_config = {
    "host": os.getenv("DB_HOST", "inventory-db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "database": os.getenv("POSTGRES_DB", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432))
}

JOKES = [
    "There are only 10 types of people: those who understand binary and those who don't.",
    "It works on my machine ¯\\_(ツ)_/¯",
    "99 little bugs in the code, 99 little bugs. Take one down, patch it around, 127 little bugs in the code.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "I would tell you a UDP joke, but you might not get it.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "docker: 'It's not a bug, it's a container feature.'",
    "There's no place like 127.0.0.1.",
    "YAML: because your config file needed more ways to break on indentation.",
    "Kubernetes: making 'it worked on my laptop' someone else's problem since 2014.",
]

def get_connection():
    return psycopg2.connect(**db_config)

def check_db_connection():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT version()")  
    version = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return version

def bump_visit_count():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            hits INT NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM visits")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO visits (hits) VALUES (0)")
    cursor.execute("UPDATE visits SET hits = hits + 1")
    connection.commit()
    cursor.execute("SELECT hits FROM visits LIMIT 1")
    hits = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return hits

@app.route("/api/dbcheck")
def db_check():
    try:
        version = check_db_connection()
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "postgres_version": version
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/joke")
def api_joke():
    return jsonify({"joke": random.choice(JOKES)}), 200

@app.route("/api/stats")
def api_stats():
    try:
        hits = bump_visit_count()
        return jsonify({"total_visits": hits, "host": socket.gethostname()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/inventory/<int:item_id>")
def get_inventory(item_id):
    log(f"A request to /inventory/{item_id} has been received")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                item_id INTEGER UNIQUE NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                stock_quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_data = [
                (1, 'Laptop', 15, 999.99),
                (2, 'Mouse', 50, 29.99),
                (3, 'Keyboard', 30, 79.99),
                (4, 'Monitor', 10, 299.99),
                (5, 'USB Cable', 100, 9.99),
                (42, 'Special Item', 5, 199.99)
            ]
            for data in sample_data:
                cursor.execute("""
                    INSERT INTO inventory (item_id, item_name, stock_quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, data)
            conn.commit()
        
        cursor.execute("""
            SELECT item_id, item_name, stock_quantity, price
            FROM inventory
            WHERE item_id = %s
        """, (item_id,))
        
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if item:
            return jsonify({
                "status": "success",
                "item": {
                    "id": item[0],
                    "name": item[1],
                    "stock": item[2],
                    "price": float(item[3])
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Item {item_id} not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
log("A request to /inventory/42 has been received")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104 - This is required in order to listen on all network interfa
