from flask import Flask,jsonify
import mysql.connector


app=Flask(__name__)

data_base={
'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': 'parola_ta_aici'
}


@app.route('/api/echipamente', methods=['GET'])
def get_echipamente():

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente")
                datele = cursor.fetchall()

        response=jsonify(datele)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(f"Eroare: {e}")
        return jsonify({"eroare": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
