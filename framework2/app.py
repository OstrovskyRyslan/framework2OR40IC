from flask import Flask, jsonify, request
import pyodbc
import logging

# Налаштування логування
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Конфігурація підключення до бази даних
DB_CONFIG = {
    'server': 'DESKTOP-QQAOEK4',
    'database': 'Games',
    'username': '',  # Для Windows Authentication не вказуємо користувача
    'password': '',  # Для Windows Authentication не вказуємо пароль
}

# Підключення до бази даних
def get_db_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            "Trusted_Connection=yes;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        return conn
    except Exception as e:
        logging.error(f"Помилка підключення до бази даних: {e}")
        raise

# Ендпоінт для отримання списку всіх гравців
@app.route('/api/players', methods=['GET'])
def get_players():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Отримання параметрів фільтрації та сортування з запиту
        player_name = request.args.get('player_name', '')
        min_level = request.args.get('min_level', type=int)
        max_score = request.args.get('max_score', type=int)
        sort_by = request.args.get('sort_by', 'player_name')  # За замовчуванням сортування за ім'ям

        # Створення запиту
        query = "SELECT * FROM players WHERE 1=1"
        
        # Додавання фільтрації за ім'ям гравця
        if player_name:
            query += f" AND player_name LIKE '%{player_name}%'"
        
        # Додавання фільтрації за рівнем
        if min_level:
            query += f" AND level >= {min_level}"
        
        # Додавання фільтрації за кількістю очок
        if max_score:
            query += f" AND score <= {max_score}"
        
        # Додавання сортування
        query += f" ORDER BY {sort_by}"

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            logging.warning("Запит не повернув жодних даних.")

        # Формування списку гравців
        players = [{"player_id": row[0], "player_name": row[1], "level": row[2], "score": row[3], "time_spent": row[4]} for row in rows]
        conn.close()

        if not players:
            return jsonify({"error": "Немає даних для відображення"}), 404

        return jsonify(players)
    
    except Exception as e:
        logging.error(f"Помилка при отриманні даних: {e}")
        return jsonify({"error": "Помилка при отриманні даних"}), 500

# Ендпоінт для отримання даних про конкретного гравця
@app.route('/api/players/<player_name>', methods=['GET'])
def get_player(player_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM players WHERE player_name = ?"
        cursor.execute(query, (player_name,))
        row = cursor.fetchone()
        
        if row:
            player = {
                "player_id": row[0],
                "player_name": row[1],
                "level": row[2],
                "score": row[3],
                "time_spent": row[4]
            }
            conn.close()
            return jsonify(player)
        else:
            return jsonify({"error": "Гравець не знайдений"}), 404

    except Exception as e:
        logging.error(f"Помилка при отриманні даних: {e}")
        return jsonify({"error": "Помилка при отриманні даних"}), 500

# Запуск Flask додатку
if __name__ == '__main__':
    app.run(debug=True)
