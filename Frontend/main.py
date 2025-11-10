from flask import Flask, jsonify, request, make_response
from fpdf import FPDF
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_base = {
    'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': 'root',
    'port': 3306
}


@app.route('/api/echipamente', methods=['GET'])
def get_echipamente():
    try:
        nr_inventar = request.args.get('nr_inventar')
        utilizator = request.args.get('utilizator')
        etaj = request.args.get('etaj')

        query = "SELECT * FROM Echipamente"
        where_clauses = []
        params = []

        if nr_inventar:
            where_clauses.append("NR_INVENTAR LIKE %s")
            params.append(f"%{nr_inventar}%")

        if utilizator:
            where_clauses.append("UTILIZATOR LIKE %s")
            params.append(f"%{utilizator}%")

        if etaj:
            where_clauses.append("ETAJ = %s")
            params.append(etaj)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                datele = cursor.fetchall()

        return jsonify(datele)

    except mysql.connector.Error as e:
        print(f"Eroare la get_echipamente: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/echipamente/add', methods=['POST'])
def add_echipament():
    datele_noi = request.json

    query = """
            INSERT INTO Echipamente (nr_inventar, nume_pc, utilizator, etaj, tip_calc, data_achizitie, ip, \
                                     sistem_operare, licenta_so, obs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

    valori = (
        datele_noi.get('NR_INVENTAR'),
        datele_noi.get('NUME_PC'),
        datele_noi.get('UTILIZATOR'),
        datele_noi.get('ETAJ'),
        datele_noi.get('TIP_CALC'),
        datele_noi.get('DATA_ACHIZITIE') or None,
        datele_noi.get('IP'),
        datele_noi.get('SISTEM_OPERARE'),
        datele_noi.get('LICENTA_SO'),
        datele_noi.get('OBS')
    )

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Echipament adăugat cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adăugare: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/echipamente/update/<id>', methods=['POST'])
def update_echipament(id):
    datele_modificate = request.json

    query = """
            UPDATE Echipamente
            SET nr_inventar    = %s,
                nume_pc        = %s,
                utilizator     = %s,
                etaj           = %s,
                tip_calc       = %s,
                data_achizitie = %s,
                ip             = %s,
                sistem_operare = %s,
                licenta_so     = %s,
                obs            = %s
            WHERE NR_INVENTAR = %s
            """

    valori = (
        datele_modificate.get('NR_INVENTAR'),
        datele_modificate.get('NUME_PC'),
        datele_modificate.get('UTILIZATOR'),
        datele_modificate.get('ETAJ'),
        datele_modificate.get('TIP_CALC'),
        datele_modificate.get('DATA_ACHIZITIE') or None,
        datele_modificate.get('IP'),
        datele_modificate.get('SISTEM_OPERARE'),
        datele_modificate.get('LICENTA_SO'),
        datele_modificate.get('OBS'),
        id
    )

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Echipament modificat cu succes!"}), 200
    except Error as e:
        print(f"Eroare la modificare: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/echipamente/delete/<id>', methods=['POST'])
def delete_echipament(id):
    query = "DELETE FROM Echipamente WHERE NR_INVENTAR = %s"
    valori = (id,)

    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Echipament șters cu succes!"}), 200
    except Error as e:
        print(f"Eroare la ștergere: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/echipamente/print/<id>', methods=['GET'])
def print_echipament_pdf(id):
    try:
        date_item = {}
        interventii = []

        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (id,))
                date_item = cursor.fetchone()

            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC", (id,))
                interventii = cursor.fetchall()

        if not date_item:
            return jsonify({"eroare": "Echipament nu a fost găsit"}), 404

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt=f"Fisa Echipament IT: {date_item.get('NR_INVENTAR', 'N/A')}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt="Date Administrative", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, txt=f"Tip Echipament: {date_item.get('TIP_CALC', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Nume PC: {date_item.get('NUME_PC', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Utilizator: {date_item.get('UTILIZATOR', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Etaj: {date_item.get('ETAJ', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Data Achizitie: {str(date_item.get('DATA_ACHIZITIE', 'N/A'))}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt="Detalii Tehnice", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, txt=f"Adresa IP: {date_item.get('IP', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Sistem Operare: {date_item.get('SISTEM_OPERARE', 'N/A')}", ln=True)
        pdf.cell(0, 8, txt=f"Licenta SO: {date_item.get('LICENTA_SO', 'N/A')}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt="Observatii", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, txt=date_item.get('OBS', 'N/A'))
        pdf.ln(10)

        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt="Istoric Interventii", ln=True)
        if not interventii:
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 8, txt="Nicio interventie inregistrata.", ln=True)
        else:
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(30, 8, 'Data', 1)
            pdf.cell(40, 8, 'Tip', 1)
            pdf.cell(90, 8, 'Descriere', 1)
            pdf.cell(30, 8, 'Operator', 1, ln=True)

            pdf.set_font("Arial", size=10)
            for interventie in interventii:
                pdf.cell(30, 8, str(interventie.get('DATA_INTERVENTIE', 'N/A')), 1)
                pdf.cell(40, 8, interventie.get('TIP_INTERVENTIE', 'N/A'), 1)
                pdf.cell(90, 8, interventie.get('DESCRIERE_INTERVENTIE', 'N/A'), 1)
                pdf.cell(30, 8, interventie.get('OPERATOR', 'N/A'), 1, ln=True)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=fisa_{date_item.get("NR_INVENTAR")}.pdf'
        return response

    except Exception as e:
        print(f"Eroare la generare PDF: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/<nr_inventar>', methods=['GET'])
def get_interventii(nr_inventar):
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC",
                               (nr_inventar,))
                datele = cursor.fetchall()
        return jsonify(datele)
    except Error as e:
        print(f"Eroare la citirea interventiilor: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/add', methods=['POST'])
def add_interventie():
    datele_noi = request.json
    query = """
            INSERT INTO Interventii (NR_INVENTAR, DATA_INTERVENTIE, TIP_INTERVENTIE, DESCRIERE_INTERVENTIE, OPERATOR)
            VALUES (%s, %s, %s, %s, %s)
            """
    valori = (
        datele_noi.get('NR_INVENTAR'),
        datele_noi.get('DATA_INTERVENTIE') or None,
        datele_noi.get('TIP_INTERVENTIE'),
        datele_noi.get('DESCRIERE_INTERVENTIE'),
        datele_noi.get('OPERATOR')
    )
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Intervenție adăugată cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adaugarea interventiei: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)