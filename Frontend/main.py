import os
import datetime
import traceback
from flask import Flask, jsonify, request, make_response, send_from_directory, session
from fpdf import FPDF
import mysql.connector
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import functools

# --- INITIALIZARE FLASK ---
app = Flask(__name__, static_url_path='', static_folder='.')
app.secret_key = 'cheie_secreta_foarte_complexa_aici'
CORS(app)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- CONFIGURARE CALE FONT ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, 'DejaVuSans.ttf')

# --- CONFIGURARE BAZA DE DATE ---
data_base = {
    'host': 'moro2004.mysql.pythonanywhere-services.com',
    'database': 'moro2004$it_inventar',
    'user': 'moro2004',
    'password': 'oB6Nwm42a333ATV',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**data_base)

# --- DECORATORI ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"eroare": "Neautorizat"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({"eroare": "Doar adminii au acces"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- CLASA PDF ---
class ModernPDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.font_loaded = False
        if os.path.exists(FONT_PATH):
            try:
                self.add_font('DejaVu', '', FONT_PATH, uni=True)
                self.add_font('DejaVu', 'B', FONT_PATH, uni=True)
                self.font_loaded = True
            except: pass

    def safe_text(self, txt):
        if not txt or str(txt) == 'None' or str(txt) == 'null' or str(txt).strip() == '': return "-"
        txt = str(txt)
        if self.font_loaded: return txt
        return txt.encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        self.set_fill_color(13, 71, 161)
        self.rect(0, 0, 210, 5, 'F')
        self.set_y(10)
        self.set_font('DejaVu' if self.font_loaded else 'Arial', '', 8)
        self.set_text_color(100)
        self.cell(0, 6, self.safe_text('PARCHETUL DE PE LÂNGĂ TRIBUNALUL BRAȘOV | DEPARTAMENT IT'), 0, 1, 'R')
        self.set_draw_color(200)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu' if self.font_loaded else 'Arial', '', 7)
        self.set_text_color(150)
        data_azi = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.cell(0, 10, self.safe_text(f'Generat la: {data_azi} | Pagina {self.page_no()}/{{nb}}'), 0, 0, 'C')

    def section_title(self, label):
        if self.get_y() > 250: self.add_page()
        self.ln(5)
        self.set_font('DejaVu' if self.font_loaded else 'Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.set_text_color(13, 71, 161)
        self.cell(0, 8, f"  {self.safe_text(label.upper())}", 'L', 1, 'L', True)
        self.ln(3)

    def info_row(self, label, value):
        if self.get_y() > 275: self.add_page()
        self.set_font('DejaVu' if self.font_loaded else 'Arial', '', 9)
        self.set_text_color(100)
        self.cell(50, 6, self.safe_text(label), 0, 0, 'R')
        self.set_text_color(0)
        x = self.get_x(); y = self.get_y()
        self.multi_cell(140, 6, self.safe_text(value), 0, 'L')
        self.set_draw_color(240); self.line(x, self.get_y(), 200, self.get_y()); self.ln(1)

# --- RUTE PENTRU FIȘIERE STATICE ---
@app.route('/')
def serve_index(): return send_from_directory('.', 'index.html')
@app.route('/<path:path>')
def serve_static_files(path): return send_from_directory('.', path)

# --- AUTENTIFICARE ---
@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (d.get('username'),))
        user = cursor.fetchone(); conn.close()
        if user and user['username'] == d.get('username') and check_password_hash(user['password'], d.get('password')):
            session['user_id'] = user['id']; session['username'] = user['username']; session['role'] = user['role']
            return jsonify({"succes": True, "role": user['role']})
        else: return jsonify({"succes": False, "eroare": "Utilizator sau parolă incorectă"}), 401
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout(): session.clear(); return jsonify({"succes": True})

@app.route('/api/me', methods=['GET'])
def current_user():
    if 'user_id' in session: return jsonify({"logged_in": True, "username": session['username'], "role": session['role']})
    return jsonify({"logged_in": False})

# --- ADMIN USERS ---
@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role FROM users"); users = cursor.fetchall(); conn.close()
        return jsonify(users)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

@app.route('/api/users/add', methods=['POST'])
@admin_required
def add_user():
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        pwd = generate_password_hash(d.get('password'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (d.get('username'), pwd, d.get('role', 'viewer')))
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/users/update_role/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    if user_id == 1: return jsonify({"succes": False, "eroare": "Nu poți modifica Super Admin"}), 400
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (request.json.get('role'), user_id))
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    if id == 1 or id == session.get('user_id'): return jsonify({"succes": False, "eroare": "Acțiune interzisă"}), 400
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

# --- INVENTAR & CĂUTARE AVANSATĂ (FIXAT!) ---
@app.route('/api/assets/all', methods=['GET'])
@login_required
def get_all_assets():
    try:
        # Preluăm parametrii și curățăm spațiile
        nr_inv = request.args.get('nr_inventar', '').strip()
        user = request.args.get('utilizator', '').strip()
        locatie = request.args.get('etaj', '').strip()

        # --- Parametri noi pentru căutare avansată ---
        nume = request.args.get('nume', '').strip()
        serie = request.args.get('serie', '').strip()
        ip = request.args.get('ip', '').strip()
        tip = request.args.get('tip', '').strip()

        # Query de bază
        q1 = "SELECT NR_INVENTAR, CATEGORIE, TIP_CALC AS TIP, NUME_PC AS NUME, UTILIZATOR, ETAJ, IP, SERIE_UC AS SERIE FROM Echipamente"
        q2 = "SELECT NR_INVENTAR, CATEGORIE, TIP, NUME_PERIFERICE AS NUME, UTILIZATOR, NULL AS ETAJ, IP, SERIE_UC AS SERIE FROM Periferice"
        query = f"SELECT * FROM ({q1} UNION {q2}) AS assets"

        where = []
        params = []

        # 1. Filtre Standard
        if nr_inv:
            where.append("NR_INVENTAR LIKE %s")
            params.append(f"%{nr_inv}%")

        if user:
            where.append("UTILIZATOR LIKE %s")
            params.append(f"%{user}%")

        if locatie: # Căutare EXACTĂ pentru etaj
            where.append("ETAJ = %s")
            params.append(locatie)

        # 2. Filtre Avansate (NOU)
        if nume:
            where.append("NUME LIKE %s")
            params.append(f"%{nume}%")

        if serie:
            where.append("SERIE LIKE %s")
            params.append(f"%{serie}%")

        if ip:
            where.append("IP LIKE %s")
            params.append(f"%{ip}%")

        if tip:
            where.append("TIP LIKE %s")
            params.append(f"%{tip}%")

        # Asamblare query
        if where:
            query += " WHERE " + " AND ".join(where)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

@app.route('/api/echipament/<path:nr_inventar>', methods=['GET'])
@login_required
def get_echipament_details(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr_inventar.strip(),)); data = cursor.fetchone(); conn.close()
        return jsonify(data)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

@app.route('/api/periferic/<path:nr_inventar>', methods=['GET'])
@login_required
def get_periferic_details(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr_inventar.strip(),)); data = cursor.fetchone(); conn.close()
        return jsonify(data)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

# --- ADAUGARE / EDITARE ---
@app.route('/api/echipamente/add', methods=['POST'])
@admin_required
def add_echipament():
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT NR_INVENTAR FROM Echipamente WHERE NR_INVENTAR = %s", (d.get('NR_INVENTAR','').strip(),))
        if cursor.fetchone(): conn.close(); return jsonify({"succes": False, "eroare": "Nr. Inventar există deja!"}), 400
        cols = ['NR_INVENTAR','CATEGORIE','TIP_CALC','NUME_PC','UTILIZATOR','NR_USER','DATA_ACHIZITIE','ETAJ','FUNCTIE','IP','RETEA','SERIE_UC','SERIE_MON','MEMORIE','SISTEM_OPERARE','LICENTA_SO','OFFICE','LICENTA_OFFICE','ANTIVIRUS','CAMERA','TELEFON','PERIFERICE','PARCHET','PASS','OBS']
        vals = [d.get(c, '').strip() if isinstance(d.get(c), str) else d.get(c) for c in cols]
        placeholders = ','.join(['%s']*len(cols))
        cursor.execute(f"INSERT INTO Echipamente ({','.join(cols)}) VALUES ({placeholders})", vals)
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/periferice/add', methods=['POST'])
@admin_required
def add_periferic():
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT NR_INVENTAR FROM Periferice WHERE NR_INVENTAR = %s", (d.get('NR_INVENTAR','').strip(),))
        if cursor.fetchone(): conn.close(); return jsonify({"succes": False, "eroare": "Nr. Inventar există deja!"}), 400
        cols = ['NR_INVENTAR','CATEGORIE','TIP','PRODUCATOR','NUME_PERIFERICE','UTILIZATOR','NUME_USER','DATA_ACHIZITIE','NUME_CALC','SERIE_UC','IP','RETEA','MEMORIE','FORMAT','CULOARE_IMPRIMARE','DUPLEX','STARE_PARAMETRI','CAMERA','ANTIVIRUS','PARCHET','PASS','OBS','OBS2']
        vals = [d.get(c, '').strip() if isinstance(d.get(c), str) else d.get(c) for c in cols]
        placeholders = ','.join(['%s']*len(cols))
        cursor.execute(f"INSERT INTO Periferice ({','.join(cols)}) VALUES ({placeholders})", vals)
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/echipamente/update/<path:nr_inv>', methods=['PUT'])
@admin_required
def update_echipament(nr_inv):
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cols = ['CATEGORIE','TIP_CALC','NUME_PC','UTILIZATOR','NR_USER','DATA_ACHIZITIE','ETAJ','FUNCTIE','IP','RETEA','SERIE_UC','SERIE_MON','MEMORIE','SISTEM_OPERARE','LICENTA_SO','OFFICE','LICENTA_OFFICE','ANTIVIRUS','CAMERA','TELEFON','PERIFERICE','PARCHET','PASS','OBS']
        sets = ', '.join([f"{c}=%s" for c in cols]); vals = [d.get(c) for c in cols]; vals.append(nr_inv.strip())
        cursor.execute(f"UPDATE Echipamente SET {sets} WHERE NR_INVENTAR=%s", vals)
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/periferice/update/<path:nr_inv>', methods=['PUT'])
@admin_required
def update_periferic(nr_inv):
    d = request.json
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cols = ['CATEGORIE','TIP','PRODUCATOR','NUME_PERIFERICE','UTILIZATOR','NUME_USER','DATA_ACHIZITIE','NUME_CALC','SERIE_UC','IP','RETEA','MEMORIE','FORMAT','CULOARE_IMPRIMARE','DUPLEX','STARE_PARAMETRI','CAMERA','ANTIVIRUS','PARCHET','PASS','OBS','OBS2']
        sets = ', '.join([f"{c}=%s" for c in cols]); vals = [d.get(c) for c in cols]; vals.append(nr_inv.strip())
        cursor.execute(f"UPDATE Periferice SET {sets} WHERE NR_INVENTAR=%s", vals)
        conn.commit(); conn.close(); return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/assets/delete/<path:nr_inventar>', methods=['POST'])
@admin_required
def delete_asset(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(); nr = nr_inventar.strip()
        cursor.execute("DELETE FROM Echipamente WHERE NR_INVENTAR = %s", (nr,))
        r1 = cursor.rowcount
        cursor.execute("DELETE FROM Periferice WHERE NR_INVENTAR = %s", (nr,))
        r2 = cursor.rowcount
        conn.commit(); conn.close()
        return jsonify({"succes": True}) if r1 or r2 else (jsonify({"eroare": "Negăsit"}), 404)
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

# --- INTERVENTII ---
@app.route('/api/interventii/<path:nr_inventar>', methods=['GET'])
@login_required
def get_interventii(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC", (nr_inventar.strip(),))
        data = cursor.fetchall(); conn.close(); return jsonify(data)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

@app.route('/api/interventii/add', methods=['POST'])
@admin_required
def add_interventie():
    d = request.json
    try:
        sql = """INSERT INTO Interventii (NR_INVENTAR, TIP_ECHIPAMENT, DATA_INTERVENTIE, TIP_INTERVENTIE, TIP_OPERATIE, DESCRIERE_INTERVENTIE, componente_schimbate_adaugate, DURATA_INTERVENTIE, OPERATOR, OBSERVATII) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        val = (d.get('NR_INVENTAR','').strip(), d.get('TIP_ECHIPAMENT'), d.get('DATA_INTERVENTIE'), d.get('TIP_INTERVENTIE'), d.get('TIP_OPERATIE'), d.get('DESCRIERE_INTERVENTIE'), d.get('componente_schimbate_adaugate'), d.get('DURATA_INTERVENTIE'), d.get('OPERATOR'), d.get('OBSERVATII'))
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(sql, val); conn.commit(); conn.close()
        return jsonify({"succes": True}), 201
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/interventii/update/<int:id_int>', methods=['PUT'])
@admin_required
def update_interventie(id_int):
    d = request.json
    try:
        sql = """UPDATE Interventii SET NR_INVENTAR=%s, DATA_INTERVENTIE=%s, TIP_INTERVENTIE=%s, TIP_OPERATIE=%s, DESCRIERE_INTERVENTIE=%s, componente_schimbate_adaugate=%s, DURATA_INTERVENTIE=%s, OPERATOR=%s, OBSERVATII=%s WHERE ID_INTERVENTIE=%s"""
        val = (d.get('NR_INVENTAR'), d.get('DATA_INTERVENTIE'), d.get('TIP_INTERVENTIE'), d.get('TIP_OPERATIE'), d.get('DESCRIERE_INTERVENTIE'), d.get('componente_schimbate_adaugate'), d.get('DURATA_INTERVENTIE'), d.get('OPERATOR'), d.get('OBSERVATII'), id_int)
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(sql, val); conn.commit(); conn.close()
        return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/interventii/delete/<int:id_int>', methods=['POST'])
@admin_required
def delete_interventie(id_int):
    try:
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("DELETE FROM Interventii WHERE ID_INTERVENTIE=%s", (id_int,)); conn.commit(); conn.close()
        return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

# --- GENERARE PDF ---
@app.route('/api/print/<path:nr_inventar>', methods=['GET'])
def print_pdf(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        nr = nr_inventar.strip()
        cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr,))
        item = cursor.fetchone(); tip_articol = 'echipament'
        if not item:
            cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr,))
            item = cursor.fetchone(); tip_articol = 'periferic'
        if not item: return jsonify({"eroare": "Negăsit"}), 404

        cursor.execute("SELECT * FROM Interventii WHERE NR_INVENTAR = %s ORDER BY DATA_INTERVENTIE DESC", (nr,))
        interventii = cursor.fetchall(); conn.close()

        campuri_echipament = [
            ("Nr. Inventar", "NR_INVENTAR"), ("Categorie", "CATEGORIE"), ("Tip Calc", "TIP_CALC"),
            ("Nume PC", "NUME_PC"), ("Utilizator", "UTILIZATOR"), ("Nr. User", "NR_USER"),
            ("Data Achiziție", "DATA_ACHIZITIE"), ("Etaj", "ETAJ"), ("Funcție", "FUNCTIE"),
            ("IP", "IP"), ("Rețea", "RETEA"), ("Serie UC", "SERIE_UC"), ("Serie Monitor", "SERIE_MON"),
            ("Memorie", "MEMORIE"), ("Sistem Operare", "SISTEM_OPERARE"), ("Licență SO", "LICENTA_SO"),
            ("Office", "OFFICE"), ("Licență Office", "LICENTA_OFFICE"), ("Antivirus", "ANTIVIRUS"),
            ("Cameră", "CAMERA"), ("Telefon", "TELEFON"), ("Periferice", "PERIFERICE"),
            ("Parchet", "PARCHET"), ("Pass", "PASS"), ("Obs", "OBS")
        ]

        campuri_periferic = [
            ("Nr. Inventar", "NR_INVENTAR"), ("Categorie", "CATEGORIE"), ("Tip", "TIP"),
            ("Producător", "PRODUCATOR"), ("Nume Periferice", "NUME_PERIFERICE"),
            ("Nume Calc", "NUME_CALC"), ("Utilizator", "UTILIZATOR"), ("Nume User", "NUME_USER"),
            ("Data Achiziție", "DATA_ACHIZITIE"), ("Serie UC", "SERIE_UC"), ("IP", "IP"),
            ("Rețea", "RETEA"), ("Memorie", "MEMORIE"), ("Format", "FORMAT"),
            ("Culoare Impr.", "CULOARE_IMPRIMARE"), ("Duplex", "DUPLEX"),
            ("Stare Parametri", "STARE_PARAMETRI"), ("Cameră", "CAMERA"), ("Antivirus", "ANTIVIRUS"),
            ("Parchet", "PARCHET"), ("Pass", "PASS"), ("Obs", "OBS"), ("Obs2", "OBS2")
        ]

        lista = campuri_echipament if tip_articol == 'echipament' else campuri_periferic
        pdf = ModernPDF(); pdf.alias_nb_pages(); pdf.add_page()
        pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", 'B', 22)
        pdf.cell(0, 15, pdf.safe_text(f"FIȘĂ INVENTAR: {item['NR_INVENTAR']}"), 0, 1, 'C')

        pdf.section_title("DATE ARTICOL")
        for et, k in lista:
            val = item.get(k)
            if val and str(val).strip() != '' and str(val) != 'None': pdf.info_row(et, val)

        pdf.add_page(); pdf.section_title("ISTORIC INTERVENȚII")
        if interventii:
            pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", 'B', 8); pdf.set_fill_color(220, 220, 220)
            col_w = [25, 20, 25, 80, 40]; headers = ["Data", "Tip", "Op.", "Detalii (Descriere, Durată, Obs)", "Operator"]
            for i, h in enumerate(headers): pdf.cell(col_w[i], 8, pdf.safe_text(h), 1, 0, 'C', True)
            pdf.ln(); pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", '', 8)
            for r in interventii:
                desc = f"{r.get('DESCRIERE_INTERVENTIE','-')}\nComp: {r.get('componente_schimbate_adaugate','')}\nDurata: {r.get('DURATA_INTERVENTIE','-')} | Obs: {r.get('OBSERVATII','')}"
                x_s = pdf.get_x(); y_s = pdf.get_y()
                pdf.set_xy(x_s + sum(col_w[:3]), y_s); pdf.multi_cell(col_w[3], 5, pdf.safe_text(desc), 1, 'L')
                h_row = pdf.get_y() - y_s
                pdf.set_xy(x_s, y_s)
                pdf.cell(col_w[0], h_row, pdf.safe_text(str(r.get('DATA_INTERVENTIE','-'))), 1, 0, 'C')
                pdf.cell(col_w[1], h_row, pdf.safe_text(str(r.get('TIP_INTERVENTIE','-'))), 1, 0, 'C')
                pdf.cell(col_w[2], h_row, pdf.safe_text(str(r.get('TIP_OPERATIE','-'))), 1, 0, 'C')
                pdf.set_xy(x_s + sum(col_w[:3]), y_s); pdf.multi_cell(col_w[3], 5, pdf.safe_text(desc), 1, 'L')
                pdf.set_xy(x_s + sum(col_w[:4]), y_s)
                pdf.cell(col_w[4], h_row, pdf.safe_text(str(r.get('OPERATOR','-'))), 1, 1, 'C')
        else:
            pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", '', 10)
            pdf.cell(0, 10, pdf.safe_text("Nu există intervenții înregistrate."), 0, 1, 'L')

        out = pdf.output(dest='S');
        if isinstance(out, str): out = out.encode('latin-1')
        res = make_response(out)
        res.headers['Content-Type'] = 'application/pdf'
        res.headers['Content-Disposition'] = f'inline; filename=Fisa_{nr_inventar}.pdf'
        return res
    except Exception as e: return jsonify({"eroare": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
