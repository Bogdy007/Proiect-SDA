from flask import Flask, jsonify, request, make_response
from fpdf import FPDF
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
import datetime
import traceback
import os

app = Flask(__name__)
CORS(app)

data_base = {
    'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': 'root',
    'port': 3306
}


def get_db_connection():
    return mysql.connector.connect(**data_base)


class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(13, 71, 161)
        self.rect(0, 0, 210, 5, 'F')
        self.set_y(10)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, 'PARCHETUL DE PE LÂNGĂ TRIBUNALUL BRAȘOV | DEPARTAMENT IT', 0, 1, 'R')
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(150)
        data_azi = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.cell(0, 10, f'Generat automat la: {data_azi} | Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

    def section_title(self, label, icon_char=None):
        if self.get_y() > 250:
            self.add_page()
        self.ln(5)
        self.set_font('DejaVu', '', 11)
        self.set_fill_color(240, 245, 255)
        self.set_text_color(13, 71, 161)
        self.set_draw_color(13, 71, 161)
        self.set_line_width(0.3)
        self.cell(0, 8, f"  {label.upper()}", 'L', 1, 'L', True)
        self.ln(2)

    def info_row(self, label, value):
        if self.get_y() > 275:
            self.add_page()
        col_label_w = 50
        col_value_w = 140
        line_height = 6
        val_str = str(value) if value is not None and str(value).lower() != 'none' and str(value) != '' else '-'
        x_start = self.get_x()
        y_start = self.get_y()
        self.set_font('DejaVu', '', 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(col_label_w, line_height, label, 0, 'R')
        y_end_label = self.get_y()
        self.set_xy(x_start + col_label_w + 2, y_start)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(col_value_w, line_height, val_str, 0, 'L')
        y_end_value = self.get_y()
        new_y = max(y_end_label, y_end_value)
        self.set_draw_color(240, 240, 240)
        self.set_line_width(0.1)
        self.line(x_start, new_y, x_start + 190, new_y)
        self.set_xy(x_start, new_y + 1)


@app.route('/api/assets/all', methods=['GET'])
def get_all_assets():
    try:
        nr_inventar = request.args.get('nr_inventar')
        utilizator = request.args.get('utilizator')
        etaj = request.args.get('etaj')
        nume = request.args.get('nume')
        serie = request.args.get('serie')
        ip = request.args.get('ip')
        tip = request.args.get('tip')

        query_echipamente = """
                            SELECT NR_INVENTAR, \
                                   CATEGORIE, \
                                   TIP_CALC AS TIP, \
                                   NUME_PC  AS NUME, \
                                   UTILIZATOR, \
                                   ETAJ, \
                                   IP, \
                                   SERIE_UC AS SERIE
                            FROM Echipamente \
                            """
        query_periferice = """
                           SELECT NR_INVENTAR, \
                                  CATEGORIE, \
                                  TIP, \
                                  NUME_PERIFERICE AS NUME, \
                                  UTILIZATOR, \
                                  NULL            AS ETAJ, \
                                  IP, \
                                  SERIE_UC        AS SERIE
                           FROM Periferice \
                           """

        base_query = f"SELECT * FROM ({query_echipamente} UNION {query_periferice}) AS assets"

        where_clauses = []
        params = []

        if nr_inventar:
            where_clauses.append("NR_INVENTAR LIKE %s")
            params.append(f"%{nr_inventar}%")
        if utilizator:
            where_clauses.append("UTILIZATOR LIKE %s")
            params.append(f"%{utilizator}%")
        if etaj:
            where_clauses.append("ETAJ LIKE %s")
            params.append(f"%{etaj}%")
        if nume:
            where_clauses.append("NUME LIKE %s")
            params.append(f"%{nume}%")
        if serie:
            where_clauses.append("SERIE LIKE %s")
            params.append(f"%{serie}%")
        if ip:
            where_clauses.append("IP LIKE %s")
            params.append(f"%{ip}%")
        if tip:
            where_clauses.append("TIP LIKE %s")
            params.append(f"%{tip}%")

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(base_query, tuple(params))
                datele = cursor.fetchall()
        return jsonify(datele)
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/echipament/<nr_inventar>', methods=['GET'])
def get_echipament_details(nr_inventar):
    try:
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar,))
                data = cursor.fetchone()
        return jsonify(data)
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/periferic/<nr_inventar>', methods=['GET'])
def get_periferic_details(nr_inventar):
    try:
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar,))
                data = cursor.fetchone()
        return jsonify(data)
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/echipamente/add', methods=['POST'])
def add_echipament():
    d = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = """INSERT INTO Echipamente (NR_INVENTAR, CATEGORIE, TIP_CALC, NUME_PC, UTILIZATOR, NR_USER, \
                                                  DATA_ACHIZITIE, ETAJ, FUNCTIE, IP, RETEA, SERIE_UC, SERIE_MON, \
                                                  MEMORIE, SISTEM_OPERARE, LICENTA_SO, OFFICE, LICENTA_OFFICE, \
                                                  ANTIVIRUS, CAMERA, TELEFON, PERIFERICE, PARCHET, PASS, OBS) \
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
                                 %s, %s, %s)"""
                val = (d.get('NR_INVENTAR'), d.get('CATEGORIE'), d.get('TIP_CALC'), d.get('NUME_PC'),
                       d.get('UTILIZATOR'), d.get('NR_USER'), d.get('DATA_ACHIZITIE') or None, d.get('ETAJ'),
                       d.get('FUNCTIE'), d.get('IP'), d.get('RETEA'), d.get('SERIE_UC'), d.get('SERIE_MON'),
                       d.get('MEMORIE'), d.get('SISTEM_OPERARE'), d.get('LICENTA_SO'), d.get('OFFICE'),
                       d.get('LICENTA_OFFICE'), d.get('ANTIVIRUS'), d.get('CAMERA'), d.get('TELEFON'),
                       d.get('PERIFERICE'), d.get('PARCHET'), d.get('PASS'), d.get('OBS'))
                cursor.execute(sql, val)
                conn.commit()
        return jsonify({"succes": True, "mesaj": "Echipament adăugat!"}), 201
    except Exception as e:
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/periferice/add', methods=['POST'])
def add_periferic():
    d = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = """INSERT INTO Periferice (NR_INVENTAR, CATEGORIE, TIP, PRODUCATOR, NUME_PERIFERICE, UTILIZATOR, \
                                                 NUME_USER, DATA_ACHIZITIE, NUME_CALC, SERIE_UC, IP, RETEA, MEMORIE, \
                                                 FORMAT, CULOARE_IMPRIMARE, DUPLEX, STARE_PARAMETRI, CAMERA, ANTIVIRUS, \
                                                 PARCHET, PASS, OBS, OBS2) \
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
                                 %s)"""
                val = (d.get('NR_INVENTAR'), d.get('CATEGORIE'), d.get('TIP'), d.get('PRODUCATOR'),
                       d.get('NUME_PERIFERICE'), d.get('UTILIZATOR'), d.get('NUME_USER'),
                       d.get('DATA_ACHIZITIE') or None, d.get('NUME_CALC'), d.get('SERIE_UC'), d.get('IP'),
                       d.get('RETEA'), d.get('MEMORIE'), d.get('FORMAT'), d.get('CULOARE_IMPRIMARE'), d.get('DUPLEX'),
                       d.get('STARE_PARAMETRI'), d.get('CAMERA'), d.get('ANTIVIRUS'), d.get('PARCHET'), d.get('PASS'),
                       d.get('OBS'), d.get('OBS2'))
                cursor.execute(sql, val)
                conn.commit()
        return jsonify({"succes": True, "mesaj": "Periferic adăugat!"}), 201
    except Exception as e:
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/echipamente/update/<id_vechi>', methods=['PUT'])
def update_echipament(id_vechi):
    d = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if d.get('NR_INVENTAR') != id_vechi:
                    cursor.execute("SELECT NR_INVENTAR FROM Echipamente WHERE NR_INVENTAR = %s",
                                   (d.get('NR_INVENTAR'),))
                    if cursor.fetchone():
                        return jsonify({"succes": False, "eroare": "Noul număr de inventar există deja!"}), 400

                sql = """UPDATE Echipamente \
                         SET NR_INVENTAR=%s, \
                             CATEGORIE=%s, \
                             TIP_CALC=%s, \
                             NUME_PC=%s, \
                             UTILIZATOR=%s, \
                             NR_USER=%s, \
                             DATA_ACHIZITIE=%s, \
                             ETAJ=%s, \
                             FUNCTIE=%s, \
                             IP=%s, \
                             RETEA=%s, \
                             SERIE_UC=%s, \
                             SERIE_MON=%s, \
                             MEMORIE=%s, \
                             SISTEM_OPERARE=%s, \
                             LICENTA_SO=%s, \
                             OFFICE=%s, \
                             LICENTA_OFFICE=%s, \
                             ANTIVIRUS=%s, \
                             CAMERA=%s, \
                             TELEFON=%s, \
                             PERIFERICE=%s, \
                             PARCHET=%s, \
                             PASS=%s, \
                             OBS=%s
                         WHERE NR_INVENTAR = %s"""

                val = (d.get('NR_INVENTAR'), d.get('CATEGORIE'), d.get('TIP_CALC'), d.get('NUME_PC'),
                       d.get('UTILIZATOR'), d.get('NR_USER'), d.get('DATA_ACHIZITIE') or None, d.get('ETAJ'),
                       d.get('FUNCTIE'), d.get('IP'), d.get('RETEA'), d.get('SERIE_UC'), d.get('SERIE_MON'),
                       d.get('MEMORIE'), d.get('SISTEM_OPERARE'), d.get('LICENTA_SO'), d.get('OFFICE'),
                       d.get('LICENTA_OFFICE'), d.get('ANTIVIRUS'), d.get('CAMERA'), d.get('TELEFON'),
                       d.get('PERIFERICE'), d.get('PARCHET'), d.get('PASS'), d.get('OBS'),
                       id_vechi)
                cursor.execute(sql, val)
                conn.commit()
        return jsonify({"succes": True, "mesaj": "Echipament actualizat cu succes!"}), 200
    except Exception as e:
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/periferice/update/<id_vechi>', methods=['PUT'])
def update_periferic(id_vechi):
    d = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if d.get('NR_INVENTAR') != id_vechi:
                    cursor.execute("SELECT NR_INVENTAR FROM Periferice WHERE NR_INVENTAR = %s", (d.get('NR_INVENTAR'),))
                    if cursor.fetchone():
                        return jsonify({"succes": False, "eroare": "Noul număr de inventar există deja!"}), 400

                sql = """UPDATE Periferice \
                         SET NR_INVENTAR=%s, \
                             CATEGORIE=%s, \
                             TIP=%s, \
                             PRODUCATOR=%s, \
                             NUME_PERIFERICE=%s, \
                             UTILIZATOR=%s, \
                             NUME_USER=%s, \
                             DATA_ACHIZITIE=%s, \
                             NUME_CALC=%s, \
                             SERIE_UC=%s, \
                             IP=%s, \
                             RETEA=%s, \
                             MEMORIE=%s, \
                             FORMAT=%s, \
                             CULOARE_IMPRIMARE=%s, \
                             DUPLEX=%s, \
                             STARE_PARAMETRI=%s, \
                             CAMERA=%s, \
                             ANTIVIRUS=%s, \
                             PARCHET=%s, \
                             PASS=%s, \
                             OBS=%s, \
                             OBS2=%s
                         WHERE NR_INVENTAR = %s"""

                val = (d.get('NR_INVENTAR'), d.get('CATEGORIE'), d.get('TIP'), d.get('PRODUCATOR'),
                       d.get('NUME_PERIFERICE'), d.get('UTILIZATOR'), d.get('NUME_USER'),
                       d.get('DATA_ACHIZITIE') or None, d.get('NUME_CALC'), d.get('SERIE_UC'), d.get('IP'),
                       d.get('RETEA'), d.get('MEMORIE'), d.get('FORMAT'), d.get('CULOARE_IMPRIMARE'), d.get('DUPLEX'),
                       d.get('STARE_PARAMETRI'), d.get('CAMERA'), d.get('ANTIVIRUS'), d.get('PARCHET'), d.get('PASS'),
                       d.get('OBS'), d.get('OBS2'),
                       id_vechi)
                cursor.execute(sql, val)
                conn.commit()
        return jsonify({"succes": True, "mesaj": "Periferic actualizat cu succes!"}), 200
    except Exception as e:
        return jsonify({"succes": False, "eroare": str(e)}), 500


@app.route('/api/assets/delete/<nr_inventar>', methods=['POST'])
def delete_asset(nr_inventar):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar,))
                rows1 = cursor.rowcount
                cursor.execute("DELETE FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar,))
                rows2 = cursor.rowcount
                conn.commit()
        if rows1 > 0 or rows2 > 0:
            return jsonify({"succes": True}), 200
        return jsonify({"succes": False, "eroare": "Nu a fost găsit"}), 404
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/<nr_inventar>', methods=['GET'])
def get_interventii(nr_inventar):
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC",
                               (nr_inventar,))
                data = cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/add', methods=['POST'])
def add_interventie():
    d = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO Interventii (NR_INVENTAR, TIP_ECHIPAMENT, DATA_INTERVENTIE, TIP_INTERVENTIE, TIP_OPERATIE, DESCRIERE_INTERVENTIE, componente_schimbate_adaugate, DURATA_INTERVENTIE, OPERATOR, OBSERVATII) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (d.get('NR_INVENTAR'), d.get('TIP_ECHIPAMENT'), d.get('DATA_INTERVENTIE') or None,
                       d.get('TIP_INTERVENTIE'), d.get('TIP_OPERATIE'), d.get('DESCRIERE_INTERVENTIE'),
                       d.get('componente_schimbate_adaugate'), d.get('DURATA_INTERVENTIE'), d.get('OPERATOR'),
                       d.get('OBSERVATII'))
                cursor.execute(sql, val)
                conn.commit()
        return jsonify({"succes": True}), 201
    except Exception as e:
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

        pdf = ModernPDF()
        pdf.alias_nb_pages()

        try:
            pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        except:
            return jsonify({"eroare": "Lipseste DejaVuSans.ttf"}), 500

        pdf.add_page()

        pdf.set_font("DejaVu", '', 22)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 15, f"FIȘĂ INVENTAR: {date_item.get('NR_INVENTAR')}", 0, 1, 'C')
        pdf.ln(5)

        if item_type == 'echipament':
            pdf.section_title("Identificare & Locație")
            pdf.info_row("Categorie", date_item.get('CATEGORIE'))
            pdf.info_row("Tip Echipament", date_item.get('TIP_CALC'))
            pdf.info_row("Nume PC", date_item.get('NUME_PC'))
            pdf.info_row("Utilizator", f"{date_item.get('UTILIZATOR')} (ID: {date_item.get('NR_USER')})")
            pdf.info_row("Locație", f"{date_item.get('ETAJ')} / {date_item.get('FUNCTIE')}")
            pdf.info_row("Data Achiziție", str(date_item.get('DATA_ACHIZITIE')))

            pdf.section_title("Configurație Tehnică")
            pdf.info_row("IP / Rețea", f"{date_item.get('IP')} / {date_item.get('RETEA')}")
            pdf.info_row("Serie UC", date_item.get('SERIE_UC'))
            pdf.info_row("Serie Monitor", date_item.get('SERIE_MON'))
            pdf.info_row("Specificații", date_item.get('MEMORIE'))

            pdf.section_title("Software & Licențe")
            pdf.info_row("Sistem Operare", f"{date_item.get('SISTEM_OPERARE')} (Lic: {date_item.get('LICENTA_SO')})")
            pdf.info_row("Microsoft Office", f"{date_item.get('OFFICE')} (Lic: {date_item.get('LICENTA_OFFICE')})")
            pdf.info_row("Antivirus", date_item.get('ANTIVIRUS'))

            pdf.section_title("Alte Informații")
            pdf.info_row("Cameră Web", date_item.get('CAMERA'))
            pdf.info_row("Telefon", date_item.get('TELEFON'))
            pdf.info_row("Pass / Credențiale", date_item.get('PASS'))
            pdf.info_row("Periferice Atașate", date_item.get('PERIFERICE'))
            pdf.info_row("Observații", date_item.get('OBS'))

        elif item_type == 'periferic':
            pdf.section_title("Identificare")
            pdf.info_row("Categorie", date_item.get('CATEGORIE'))
            pdf.info_row("Tip", date_item.get('TIP'))
            pdf.info_row("Producător", date_item.get('PRODUCATOR'))
            pdf.info_row("Model / Nume", date_item.get('NUME_PERIFERICE'))
            pdf.info_row("Nr. Inventar", date_item.get('NR_INVENTAR'))

            pdf.section_title("Alocare & Conectivitate")
            pdf.info_row("Utilizator", f"{date_item.get('UTILIZATOR')} ({date_item.get('NUME_USER')})")
            pdf.info_row("Conectat la PC", date_item.get('NUME_CALC'))
            pdf.info_row("Adresă IP", date_item.get('IP'))
            pdf.info_row("Rețea", date_item.get('RETEA'))

            pdf.section_title("Detalii Tehnice")
            pdf.info_row("Data Achiziție", str(date_item.get('DATA_ACHIZITIE')))
            pdf.info_row("Serie UC (S/N)", date_item.get('SERIE_UC'))
            pdf.info_row("Memorie", date_item.get('MEMORIE'))
            pdf.info_row("Format", date_item.get('FORMAT'))
            pdf.info_row("Culoare", date_item.get('CULOARE_IMPRIMARE'))
            pdf.info_row("Duplex", date_item.get('DUPLEX'))
            pdf.info_row("Stare Parametri", date_item.get('STARE_PARAMETRI'))

            pdf.section_title("Securitate & Altele")
            pdf.info_row("Cameră", date_item.get('CAMERA'))
            pdf.info_row("Antivirus", date_item.get('ANTIVIRUS'))
            pdf.info_row("Parchet", date_item.get('PARCHET'))
            pdf.info_row("Pass", date_item.get('PASS'))
            pdf.info_row("Observații", date_item.get('OBS'))
            pdf.info_row("Alte Observații", date_item.get('OBS2'))

        if pdf.get_y() > 200:
            pdf.add_page()
        else:
            pdf.ln(10)

        pdf.section_title("Istoric Intervenții & Mentenanță")

        w_cols = [25, 35, 70, 35, 25]
        headers = ['Dată', 'Tip', 'Detalii Operațiune', 'Componente', 'Operator']

        pdf.set_font("DejaVu", '', 9)
        pdf.set_fill_color(13, 71, 161)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(13, 71, 161)

        for i, h in enumerate(headers):
            pdf.cell(w_cols[i], 8, h, 1, 0, 'C', True)
        pdf.ln()

        pdf.set_font("DejaVu", '', 8)
        pdf.set_text_color(0)
        pdf.set_draw_color(220)

        if not interventii:
            pdf.cell(190, 10, 'Nu au fost înregistrate intervenții.', 1, 1, 'C')
        else:
            fill = False
            for row in interventii:
                if fill:
                    pdf.set_fill_color(240, 245, 255)
                else:
                    pdf.set_fill_color(255, 255, 255)

                data = str(row.get('DATA_INTERVENTIE') or '-')
                tip = str(row.get('TIP_INTERVENTIE') or '-')
                desc = f"{row.get('TIP_OPERATIE') or ''} {row.get('DESCRIERE_INTERVENTIE') or ''}".strip()
                comp = str(row.get('componente_schimbate_adaugate') or '-')
                op = str(row.get('OPERATOR') or '-')

                pdf.cell(w_cols[0], 8, data, 1, 0, 'C', fill)
                pdf.cell(w_cols[1], 8, tip[:18], 1, 0, 'L', fill)
                pdf.cell(w_cols[2], 8, desc[:45], 1, 0, 'L', fill)
                pdf.cell(w_cols[3], 8, comp[:18], 1, 0, 'L', fill)
                pdf.cell(w_cols[4], 8, op[:13], 1, 1, 'C', fill)

                fill = not fill

        pdf_bytes = pdf.output(dest='S')
        response = make_response(bytes(pdf_bytes))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=Fisa_{nr_inventar}.pdf'
        return response

    except Exception as e:
        print(f"Eroare PDF: {e}")
        traceback.print_exc()
        return jsonify({"eroare": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)