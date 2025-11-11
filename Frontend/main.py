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


@app.route('/api/assets/all', methods=['GET'])
def get_all_assets():
    try:
        nr_inventar = request.args.get('nr_inventar')
        utilizator = request.args.get('utilizator')
        etaj = request.args.get('etaj')

        query_echipamente = "(SELECT NR_INVENTAR, CATEGORIE, TIP_CALC AS TIP, NUME_PC AS NUME, UTILIZATOR, ETAJ FROM Echipamente)"
        query_periferice = "(SELECT NR_INVENTAR, CATEGORIE, TIP, NUME_PERIFERICE AS NUME, UTILIZATOR, NULL AS ETAJ FROM Periferice)"

        base_query = f"{query_echipamente} UNION {query_periferice}"

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
            base_query = f"SELECT * FROM ({base_query}) AS assets WHERE " + " AND ".join(where_clauses)

        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(base_query, tuple(params))
                datele = cursor.fetchall()

        return jsonify(datele)

    except mysql.connector.Error as e:
        print(f"Eroare la get_all_assets: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/echipament/<nr_inventar>', methods=['GET'])
def get_echipament_details(nr_inventar):
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar,))
                datele = cursor.fetchone()
        return jsonify(datele)
    except mysql.connector.Error as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/periferic/<nr_inventar>', methods=['GET'])
def get_periferic_details(nr_inventar):
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar,))
                datele = cursor.fetchone()
        return jsonify(datele)
    except mysql.connector.Error as e:
        return jsonify({"eroare": str(e)}), 500


def get_db_connection():
    return mysql.connector.connect(**data_base)


@app.route('/api/echipamente/add', methods=['POST'])
def add_echipament():
    datele_noi = request.json
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = """INSERT INTO Echipamente (NR_INVENTAR, CATEGORIE, TIP_CALC, NUME_PC, UTILIZATOR, NR_USER, \
                                                    DATA_ACHIZITIE, ETAJ, FUNCTIE, IP, RETEA, SERIE_UC, SERIE_MON, \
                                                    MEMORIE, SISTEM_OPERARE, LICENTA_SO, OFFICE, LICENTA_OFFICE, \
                                                    ANTIVIRUS, CAMERA, TELEFON, PERIFERICE, PARCHET, PASS, OBS)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
                                   %s, %s, %s, %s)"""
                valori = (
                    datele_noi.get('NR_INVENTAR'), datele_noi.get('CATEGORIE'), datele_noi.get('TIP_CALC'),
                    datele_noi.get('NUME_PC'), datele_noi.get('UTILIZATOR'), datele_noi.get('NR_USER'),
                    datele_noi.get('DATA_ACHIZITIE') or None, datele_noi.get('ETAJ'), datele_noi.get('FUNCTIE'),
                    datele_noi.get('IP'), datele_noi.get('RETEA'), datele_noi.get('SERIE_UC'),
                    datele_noi.get('SERIE_MON'), datele_noi.get('MEMORIE'), datele_noi.get('SISTEM_OPERARE'),
                    datele_noi.get('LICENTA_SO'), datele_noi.get('OFFICE'), datele_noi.get('LICENTA_OFFICE'),
                    datele_noi.get('ANTIVIRUS'), datele_noi.get('CAMERA'), datele_noi.get('TELEFON'),
                    datele_noi.get('PERIFERICE'), datele_noi.get('PARCHET'), datele_noi.get('PASS'),
                    datele_noi.get('OBS')
                )
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Echipament adăugat cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adăugare Echipament: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/periferice/add', methods=['POST'])
def add_periferic():
    datele_noi = request.json
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = """INSERT INTO Periferice (NR_INVENTAR, CATEGORIE, TIP, PRODUCATOR, NUME_PERIFERICE, UTILIZATOR, \
                                                   NUME_USER, DATA_ACHIZITIE, NUME_CALC, SERIE_UC, IP, RETEA, MEMORIE, \
                                                   FORMAT, CULOARE_IMPRIMARE, DUPLEX, STARE_PARAMETRI, CAMERA, \
                                                   ANTIVIRUS, PARCHET, PASS, OBS, OBS2)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
                                   %s, %s)"""
                valori = (
                    datele_noi.get('NR_INVENTAR'), datele_noi.get('CATEGORIE'), datele_noi.get('TIP'),
                    datele_noi.get('PRODUCATOR'), datele_noi.get('NUME_PERIFERICE'), datele_noi.get('UTILIZATOR'),
                    datele_noi.get('NUME_USER'), datele_noi.get('DATA_ACHIZITIE') or None, datele_noi.get('NUME_CALC'),
                    datele_noi.get('SERIE_UC'), datele_noi.get('IP'), datele_noi.get('RETEA'),
                    datele_noi.get('MEMORIE'), datele_noi.get('FORMAT'), datele_noi.get('CULOARE_IMPRIMARE'),
                    datele_noi.get('DUPLEX'), datele_noi.get('STARE_PARAMETRI'), datele_noi.get('CAMERA'),
                    datele_noi.get('ANTIVIRUS'), datele_noi.get('PARCHET'), datele_noi.get('PASS'),
                    datele_noi.get('OBS'), datele_noi.get('OBS2')
                )
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Periferic adăugat cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adăugare Periferic: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/assets/delete/<nr_inventar>', methods=['POST'])
def delete_asset(nr_inventar):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar,))
                rows_deleted_echip = cursor.rowcount
                cursor.execute("DELETE FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar,))
                rows_deleted_perif = cursor.rowcount
                connection.commit()

        if rows_deleted_echip > 0 or rows_deleted_perif > 0:
            return jsonify({"succes": True, "mesaj": "Articol șters cu succes!"}), 200
        else:
            return jsonify({"succes": False, "eroare": "Articolul nu a fost găsit"}), 404
    except Error as e:
        print(f"Eroare la ștergere: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/print/<nr_inventar>', methods=['GET'])
def print_pdf(nr_inventar):
    try:
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar,))
                date_item = cursor.fetchone()
                item_type = 'echipament'
                if not date_item:
                    cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar,))
                    date_item = cursor.fetchone()
                    item_type = 'periferic'

            if not date_item:
                return jsonify({"eroare": "Articol nu a fost găsit"}), 404

            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC",
                               (nr_inventar,))
                interventii = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt=f"Fisa Articol Inventar: {date_item.get('NR_INVENTAR', 'N/A')}", ln=True, align='C')
        pdf.ln(5)

        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt=f"Categorie: {date_item.get('CATEGORIE', 'N/A')}", ln=True)
        pdf.ln(5)

        if item_type == 'echipament':
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(0, 8, txt="Date Administrative", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, txt=f"Tip: {date_item.get('TIP_CALC', 'N/A')}", ln=True)
            pdf.cell(0, 7, txt=f"Nume PC: {date_item.get('NUME_PC', 'N/A')}", ln=True)
            pdf.cell(0, 7,
                     txt=f"Utilizator: {date_item.get('UTILIZATOR', 'N/A')} (User ID: {date_item.get('NR_USER', 'N/A')})",
                     ln=True)
            pdf.cell(0, 7, txt=f"Locatie: {date_item.get('ETAJ', 'N/A')} / {date_item.get('FUNCTIE', 'N/A')}", ln=True)
            pdf.cell(0, 7, txt=f"Data Achizitie: {str(date_item.get('DATA_ACHIZITIE', 'N/A'))}", ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(0, 8, txt="Detalii Tehnice & Software", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, txt=f"IP: {date_item.get('IP', 'N/A')} (Retea: {date_item.get('RETEA', 'N/A')})", ln=True)
            pdf.cell(0, 7,
                     txt=f"Serie UC: {date_item.get('SERIE_UC', 'N/A')} / Serie Monitor: {date_item.get('SERIE_MON', 'N/A')}",
                     ln=True)
            pdf.cell(0, 7, txt=f"Memorie: {date_item.get('MEMORIE', 'N/A')}", ln=True)
            pdf.cell(0, 7,
                     txt=f"Sistem Operare: {date_item.get('SISTEM_OPERARE', 'N/A')} (Licenta: {date_item.get('LICENTA_SO', 'N/A')})",
                     ln=True)
            pdf.cell(0, 7,
                     txt=f"Office: {date_item.get('OFFICE', 'N/A')} (Licenta: {date_item.get('LICENTA_OFFICE', 'N/A')})",
                     ln=True)
            pdf.cell(0, 7, txt=f"Antivirus: {date_item.get('ANTIVIRUS', 'N/A')}", ln=True)
            pdf.cell(0, 7, txt=f"Camera: {date_item.get('CAMERA', 'N/A')} / Telefon: {date_item.get('TELEFON', 'N/A')}",
                     ln=True)
            pdf.cell(0, 7, txt=f"Periferice atasate: {date_item.get('PERIFERICE', 'N/A')}", ln=True)

        elif item_type == 'periferic':
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(0, 8, txt="Date Administrative", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, txt=f"Tip: {date_item.get('TIP', 'N/A')} / Producator: {date_item.get('PRODUCATOR', 'N/A')}",
                     ln=True)
            pdf.cell(0, 7, txt=f"Nume Periferic: {date_item.get('NUME_PERIFERICE', 'N/A')}", ln=True)
            pdf.cell(0, 7,
                     txt=f"Utilizator: {date_item.get('UTILIZATOR', 'N/A')} (User ID: {date_item.get('NUME_USER', 'N/A')})",
                     ln=True)
            pdf.cell(0, 7, txt=f"Data Achizitie: {str(date_item.get('DATA_ACHIZITIE', 'N/A'))}", ln=True)
            pdf.cell(0, 7,
                     txt=f"Conectat la: {date_item.get('NUME_CALC', 'N/A')} (Serie UC: {date_item.get('SERIE_UC', 'N/A')})",
                     ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(0, 8, txt="Detalii Tehnice", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, txt=f"IP: {date_item.get('IP', 'N/A')} (Retea: {date_item.get('RETEA', 'N/A')})", ln=True)
            pdf.cell(0, 7, txt=f"Format: {date_item.get('FORMAT', 'N/A')}", ln=True)
            pdf.cell(0, 7,
                     txt=f"Culoare: {date_item.get('CULOARE_IMPRIMARE', 'N/A')} / Duplex: {date_item.get('DUPLEX', 'N/A')}",
                     ln=True)
            pdf.cell(0, 7, txt=f"Memorie: {date_item.get('MEMORIE', 'N/A')}", ln=True)
            pdf.cell(0, 7, txt=f"Stare: {date_item.get('STARE_PARAMETRI', 'N/A')}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 8, txt="Istoric Interventii", ln=True)

        if not interventii:
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 8, txt="Nicio interventie inregistrata.", ln=True)
        else:
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(25, 8, 'Data', 1)
            pdf.cell(35, 8, 'Tip Interventie', 1)
            pdf.cell(70, 8, 'Descriere', 1)
            pdf.cell(30, 8, 'Componente', 1)
            pdf.cell(30, 8, 'Operator', 1, ln=True)

            pdf.set_font("Arial", size=9)
            for interventie in interventii:
                pdf.cell(25, 8, str(interventie.get('DATA_INTERVENTIE', 'N/A')), 1)
                pdf.cell(35, 8, interventie.get('TIP_INTERVENTIE', 'N/A'), 1)
                pdf.cell(70, 8, interventie.get('DESCRIERE_INTERVENTIE', 'N/A'), 1)
                pdf.cell(30, 8, interventie.get('componente_schimbate_adaugate', 'N/A'), 1)
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
        with get_db_connection() as connection:
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
            INSERT INTO Interventii (NR_INVENTAR, TIP_ECHIPAMENT, DATA_INTERVENTIE, TIP_INTERVENTIE, TIP_OPERATIE, \
                                     DESCRIERE_INTERVENTIE, componente_schimbate_adaugate, DURATA_INTERVENTIE, OPERATOR, \
                                     OBSERVATII)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    valori = (
        datele_noi.get('NR_INVENTAR'),
        datele_noi.get('TIP_ECHIPAMENT'),
        datele_noi.get('DATA_INTERVENTIE') or None,
        datele_noi.get('TIP_INTERVENTIE'),
        datele_noi.get('TIP_OPERATIE'),
        datele_noi.get('DESCRIERE_INTERVENTIE'),
        datele_noi.get('componente_schimbate_adaugate'),
        datele_noi.get('DURATA_INTERVENTIE'),
        datele_noi.get('OPERATOR'),
        datele_noi.get('OBSERVATII')
    )
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, valori)
                connection.commit()
        return jsonify({"succes": True, "mesaj": "Intervenție adăugată cu succes!"}), 201
    except Error as e:
        print(f"Eroare la adaugarea interventiei: {e}")
        return jsonify({"succes": False, "eroare": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)