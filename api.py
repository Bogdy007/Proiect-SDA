from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

data_base = {
    'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': '',
    'port': 3306
}

@app.route('/api/echipamente', methods=['GET'])
def get_echipamente():
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente")
                datele = cursor.fetchall()

        response = jsonify(datele)
        response.headers.add('Access-Control-Allow-Origin', '*')  # Permite accesul din browser
        return response

    except mysql.connector.Error as e:
        return jsonify({"eroare": str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' permite acces din rețea
    # port=5000 este portul Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
