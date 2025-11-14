from flask import Flask, jsonify, request, make_response
from fpdf import FPDF
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
from datetime import datetime

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
                cursor.execute(
                    "SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC",
                    (id,)
                )
                interventii = cursor.fetchall()

        if not date_item:
            return jsonify({"eroare": "Echipament nu a fost găsit"}), 404

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.set_margins(20, 20, 20)
        pdf.add_page()

        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)

        def clean_text(text):
            if text is None:
                return ''
            return str(text)

        pdf.set_font("DejaVu", "", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, clean_text("Fișă echipament IT"), ln=True)

        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, clean_text("Parchet - Inventar echipamente IT"), ln=True)

        pdf.set_text_color(150, 150, 150)
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        pdf.cell(0, 5, clean_text(f"Generat la: {now_str}"), ln=True)

        pdf.ln(8)

        pdf.set_draw_color(210, 210, 210)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(6)

        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, clean_text("Date echipament"), ln=True)

        pdf.ln(2)
        pdf.set_font("DejaVu", "", 10)

        label_w = 40
        line_h = 6

        def info_row(label, value):
            pdf.set_text_color(120, 120, 130)
            pdf.cell(label_w, line_h, clean_text(label), ln=0)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, line_h, clean_text(value or "N/A"), ln=True)

        info_row("Nr. inventar:", date_item.get('NR_INVENTAR'))
        info_row("Utilizator:", date_item.get('UTILIZATOR'))
        info_row("Nume PC:", date_item.get('NUME_PC'))
        info_row("Tip echipament:", date_item.get('TIP_CALC'))
        info_row("Etaj:", date_item.get('ETAJ'))
        info_row("Data achiziție:", date_item.get('DATA_ACHIZITIE'))

        pdf.ln(4)

        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, clean_text("Detalii tehnice"), ln=True)

        pdf.ln(2)
        pdf.set_font("DejaVu", "", 10)

        info_row("Adresă IP:", date_item.get('IP'))
        info_row("Sistem operare:", date_item.get('SISTEM_OPERARE'))
        info_row("Licență SO:", date_item.get('LICENTA_SO'))

        pdf.ln(4)

        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, clean_text("Observații"), ln=True)

        pdf.ln(2)
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(60, 60, 60)

        obs_text = clean_text(date_item.get('OBS', 'Nu există observații.')) or 'Nu există observații.'
        pdf.multi_cell(0, 5, obs_text)

        pdf.ln(4)

        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, clean_text("Istoric intervenții"), ln=True)

        pdf.ln(2)

        if not interventii:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 6, clean_text("Nu există intervenții înregistrate pentru acest echipament."), ln=True)
        else:
            col_widths = [28, 40, 82, 30]
            headers = ['Data', 'Tip', 'Descriere', 'Operator']

            pdf.set_font("DejaVu", "", 9)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(0, 123, 255)
            pdf.set_draw_color(210, 210, 210)

            for w, h in zip(col_widths, headers):
                pdf.cell(w, 7, clean_text(h), border=1, align='C', fill=True)
            pdf.ln()

            pdf.set_font("DejaVu", "", 8)
            pdf.set_text_color(30, 30, 30)
            odd_fill = (242, 248, 255)
            even_fill = (255, 255, 255)

            for idx, interventie in enumerate(interventii):
                fill_color = odd_fill if idx % 2 == 0 else even_fill
                pdf.set_fill_color(*fill_color)

                pdf.cell(
                    col_widths[0], 6,
                    clean_text(interventie.get('DATA_INTERVENTIE', 'N/A')),
                    border=1, fill=True
                )
                pdf.cell(
                    col_widths[1], 6,
                    clean_text(interventie.get('TIP_INTERVENTIE', 'N/A')),
                    border=1, fill=True
                )

                descr = clean_text(interventie.get('DESCRIERE_INTERVENTIE', 'N/A'))
                if len(descr) > 80:
                    descr = descr[:77] + "..."
                pdf.cell(
                    col_widths[2], 6,
                    descr,
                    border=1, fill=True
                )

                pdf.cell(
                    col_widths[3], 6,
                    clean_text(interventie.get('OPERATOR', 'N/A')),
                    border=1, fill=True
                )
                pdf.ln()

        pdf.set_auto_page_break(auto=False)

        if pdf.get_y() > pdf.h - 20:
            pdf.set_y(pdf.h - 20)
        else:
            pdf.set_y(pdf.h - 15)

        pdf.set_font("DejaVu", "", 8)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(0, 5, clean_text("Inventar IT - Parchet"), align='L')
        pdf.cell(0, 5, clean_text(f"Pagina {pdf.page_no()}"), align='R')

        result = pdf.output(dest='S')
        if isinstance(result, str):
            pdf_output = result.encode('latin-1', errors='ignore')
        else:
            pdf_output = bytes(result)

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
            f'inline; filename=fisa_{date_item.get("NR_INVENTAR")}.pdf'
        )
        return response

    except Exception as e:
        print(f"Eroare la generare PDF: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/<nr_inventar>', methods=['GET'])
def get_interventii(nr_inventar):
    try:
        with mysql.connector.connect(**data_base) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT * FROM Interventii WHERE NR_INVENTAR = %s "
                    "ORDER BY DATA_INTERVENTIE DESC",
                    (nr_inventar,)
                )
                datele = cursor.fetchall()
        return jsonify(datele)
    except Error as e:
        print(f"Eroare la citirea interventiilor: {e}")
        return jsonify({"eroare": str(e)}), 500


@app.route('/api/interventii/add', methods=['POST'])
def add_interventie():
    datele_noi = request.json
    query = """
            INSERT INTO Interventii (NR_INVENTAR, DATA_INTERVENTIE, TIP_INTERVENTIE,
                                     DESCRIERE_INTERVENTIE, OPERATOR)
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