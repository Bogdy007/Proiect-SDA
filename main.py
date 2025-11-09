from flask import Flask, jsonify, request, make_response
from fpdf import FPDF
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

data_base = {
    'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': '',
    'port': 3306
}


# Functia de citire
@app.route('/api/echipamente', methods=['GET'])
def get_echipamente():
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente")
                datele = cursor.fetchall()

        response = jsonify(datele)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except mysql.connector.Error as e:
        return jsonify({"eroare": str(e)}), 500


# Functia de adaugare
@app.route('/api/echipamente/add', methods=['POST'])
def add_echipament():
    datele_noi = request.json
    query = """
            INSERT INTO Echipamente (nr_inventar, nume_pc, utilizator) 
            VALUES (%s, %s, %s)
        """

    valori = (
        datele_noi['nr_inventar'],
        datele_noi['nume_pc'],
        datele_noi['utilizator']
    )

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()

        return jsonify({"mesaj": "Echipament adăugat cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adăugare: {e}")
        return jsonify({"eroare": str(e)}), 500

#Functia de modificare

@app.route('/api/echipamente/update/<int:id>', methods=['POST'])
def update_echipament(id):
    datele_modificate = request.json

    query = """
        UPDATE Echipamente 
        SET nr_inventar = %s, nume_pc = %s, utilizator = %s
        WHERE id = %s
    """
    valori = (
        datele_modificate['nr_inventar'],
        datele_modificate['nume_pc'],
        datele_modificate['utilizator'],
        id
    )

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()

        return jsonify({"mesaj": "Echipament modificat cu succes!"}), 200
    except Error as e:
        print(f"Eroare la modificare: {e}")
        return jsonify({"eroare": str(e)}), 500


#Functia de stergere
@app.route('/api/echipamente/delete/<int:id>', methods=['POST'])
def delete_echipament(id):
    query = "DELETE FROM Echipamente WHERE id = %s"
    valori = (id,)

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()

        return jsonify({"mesaj": "Echipament șters cu succes!"}), 200
    except Error as e:
        print(f"Eroare la ștergere: {e}")
        return jsonify({"eroare": str(e)}), 500


#Functia de pdf
@app.route('/api/echipamente/print/<int:id>', methods=['GET'])
def print_echipament_pdf(id):
    try:

        date_item = {}
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente WHERE id = %s", (id,))
                date_item = cursor.fetchone()

        if not date_item:
            return jsonify({"eroare": "Echipament nu a fost găsit"}), 404


        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt="Fisa Echipament IT", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, txt=f"Numar Inventar: {date_item.get('nr_inventar', 'N/A')}", ln=True)
        pdf.cell(0, 10, txt=f"Nume PC: {date_item.get('nume_pc', 'N/A')}", ln=True)
        pdf.cell(0, 10, txt=f"Utilizator: {date_item.get('utilizator', 'N/A')}", ln=True)



        pdf_output = pdf.output(dest='S').encode('latin-1')
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'

        response.headers['Content-Disposition'] = f'attachment; filename=fisa_{date_item.get("nr_inventar")}.pdf'
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    except Exception as e:
        print(f"Eroare la generare PDF: {e}")
        return jsonify({"eroare": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
