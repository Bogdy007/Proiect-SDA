import os
import datetime
import traceback
import tempfile
import qrcode
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
        if 'user_id' not in session: return jsonify({"eroare": "Neautorizat"}), 401
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
        timp_ro = datetime.datetime.now() + datetime.timedelta(hours=2)
        data_azi = timp_ro.strftime("%d.%m.%Y %H:%M")

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

# --- SISTEM NOTIFICĂRI ---
@app.route('/api/request_reset', methods=['POST'])
def request_reset_password():
    username = request.json.get('username')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            conn.close(); return jsonify({"succes": False, "eroare": "Utilizatorul nu există!"}), 404
        if user['role'] == 'admin' or user['id'] == 1:
            conn.close(); return jsonify({"succes": False, "eroare": "Administratorii nu pot folosi această funcție."}), 403
        cursor.execute("SELECT id FROM reset_requests WHERE user_id = %s", (user['id'],))
        if cursor.fetchone():
            conn.close(); return jsonify({"succes": False, "eroare": "Ai trimis deja o cerere!"}), 400
        cursor.execute("INSERT INTO reset_requests (user_id, request_date) VALUES (%s, NOW())", (user['id'],))
        conn.commit(); conn.close()
        return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

@app.route('/api/admin/notifications', methods=['GET'])
@admin_required
def get_notifications():
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        query = "SELECT r.id, u.username, r.request_date FROM reset_requests r JOIN users u ON r.user_id = u.id ORDER BY r.request_date DESC"
        cursor.execute(query); reqs = cursor.fetchall(); conn.close()
        return jsonify(reqs)
    except Exception as e: return jsonify({"eroare": str(e)}), 500

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

@app.route('/api/users/reset_password', methods=['POST'])
@admin_required
def reset_user_password():
    d = request.json
    user_id = d.get('user_id')
    new_pass = d.get('new_password')
    if not user_id or not new_pass: return jsonify({"succes": False, "eroare": "Date incomplete"}), 400
    if user_id == 1 and session.get('user_id') != 1: return jsonify({"succes": False, "eroare": "Nu poți modifica parola Super Adminului"}), 403
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        pwd_hash = generate_password_hash(new_pass)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (pwd_hash, user_id))
        cursor.execute("DELETE FROM reset_requests WHERE user_id = %s", (user_id,))
        conn.commit(); conn.close()
        return jsonify({"succes": True})
    except Exception as e: return jsonify({"succes": False, "eroare": str(e)}), 500

# --- INVENTAR & CĂUTARE AVANSATĂ ---
@app.route('/api/assets/all', methods=['GET'])
@login_required
def get_all_assets():
    try:
        nr_inv = request.args.get('nr_inventar', '').strip()
        user = request.args.get('utilizator', '').strip()
        locatie = request.args.get('etaj', '').strip()
        nume = request.args.get('nume', '').strip(); serie = request.args.get('serie', '').strip()
        ip = request.args.get('ip', '').strip(); tip = request.args.get('tip', '').strip()

        q1 = "SELECT NR_INVENTAR, CATEGORIE, TIP_CALC AS TIP, NUME_PC AS NUME, UTILIZATOR, ETAJ, IP, SERIE_UC AS SERIE FROM Echipamente"
        q2 = "SELECT NR_INVENTAR, CATEGORIE, TIP, NUME_PERIFERICE AS NUME, UTILIZATOR, NULL AS ETAJ, IP, SERIE_UC AS SERIE FROM Periferice"
        query = f"SELECT * FROM ({q1} UNION {q2}) AS assets"
        where, params = [], []
        if nr_inv: where.append("NR_INVENTAR LIKE %s"); params.append(f"%{nr_inv}%")
        if user: where.append("UTILIZATOR LIKE %s"); params.append(f"%{user}%")
        if locatie: where.append("ETAJ = %s"); params.append(locatie)
        if nume: where.append("NUME LIKE %s"); params.append(f"%{nume}%")
        if serie: where.append("SERIE LIKE %s"); params.append(f"%{serie}%")
        if ip: where.append("IP LIKE %s"); params.append(f"%{ip}%")
        if tip: where.append("TIP LIKE %s"); params.append(f"%{tip}%")
        if where: query += " WHERE " + " AND ".join(where)

        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params)); data = cursor.fetchall(); conn.close()
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

# --- ADAUGARE / EDITARE / STERGERE (MODIFICAT) ---
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
@login_required
@admin_required
def delete_asset(nr_inventar):
    try:
        conn = get_db_connection(); cursor = conn.cursor(); nr = nr_inventar.strip()

        cursor.execute("DELETE FROM Interventii WHERE NR_INVENTAR = %s", (nr,))
        # ------------------------------------------------------------------

        cursor.execute("DELETE FROM Echipamente WHERE NR_INVENTAR = %s", (nr,))
        cursor.execute("DELETE FROM Periferice WHERE NR_INVENTAR = %s", (nr,))

        conn.commit(); conn.close()
        return jsonify({"succes": True})
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

# --- GENERARE ETICHETA QR ---
@app.route('/api/print_label/<path:nr_inventar>', methods=['GET'])
def print_qr_label(nr_inventar):
    try:
        nr = nr_inventar.strip()
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Echipamente WHERE NR_INVENTAR = %s", (nr,))
        item = cursor.fetchone()
        if not item:
            cursor.execute("SELECT * FROM Periferice WHERE NR_INVENTAR = %s", (nr,))
            item = cursor.fetchone()
        conn.close()

        if not item: return jsonify({"eroare": "Nu s-a găsit echipamentul"}), 404

        # 1. Link (URL-ul paginii)
        tip_url = 'periferic' if 'NUME_PERIFERICE' in item else 'echipament'
        full_url = f"{request.host_url}detalii.html?id={nr}&type={tip_url}"

        # 2. Generare QR (Micșorat box_size)
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_qr.name)

        # 3. Generare PDF Mic (Etichetă 60x90mm Landscape)
        pdf = FPDF('L', 'mm', (60, 90))
        pdf.set_margins(2, 2, 2)
        pdf.set_auto_page_break(False)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 8)
        pdf.set_xy(0, 3)
        pdf.cell(90, 4, 'PARCHETUL DE PE LANGA TRIBUNALUL BRASOV', 0, 0, 'C')

        # Calcul pozitie X QR: (90 - 28) / 2 = 31
        pdf.image(temp_qr.name, x=31, y=8, w=28)

        # Text Principal (Jos - Nr Inventar)
        pdf.set_y(38)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 6, str(nr), 0, 1, 'C')

        # Nume Echipament (Sub numar)
        pdf.set_font('Arial', '', 7)
        nume_display = item.get('NUME_PC') or item.get('NUME_PERIFERICE') or '-'
        try:
            nume_display = nume_display.encode('latin-1', 'replace').decode('latin-1')
        except: pass
        pdf.cell(0, 4, str(nume_display)[:30], 0, 1, 'C')

        temp_qr.close(); os.unlink(temp_qr.name)

        out = pdf.output(dest='S')
        if isinstance(out, str): out = out.encode('latin-1')
        res = make_response(out)
        res.headers['Content-Type'] = 'application/pdf'
        res.headers['Content-Disposition'] = f'inline; filename=Label_{nr}.pdf'
        return res

    except Exception as e: return jsonify({"eroare": str(e)}), 500

# --- GENERARE PDF FIȘĂ (CU WRAP LA TEXT) ---
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

        # --- TABEL ISTORIC INTERVENȚII ---
        pdf.add_page(); pdf.section_title("ISTORIC INTERVENȚII")
        if interventii:
            cw = [25, 25, 40, 70, 30]
            headers = ["Data", "Tip", "Operație", "Detalii (Descriere, Obs)", "Operator"]

            pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", 'B', 9)
            pdf.set_fill_color(220, 220, 220)

            for i, h in enumerate(headers):
                pdf.cell(cw[i], 8, pdf.safe_text(h), 1, 0, 'C', True)
            pdf.ln()

            pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", '', 8)

            for r in interventii:
                data_str = str(r.get('DATA_INTERVENTIE','-'))
                tip_str = str(r.get('TIP_INTERVENTIE','-'))
                op_str = str(r.get('TIP_OPERATIE','-'))
                desc_str = f"{r.get('DESCRIERE_INTERVENTIE','-')}\nComp: {r.get('componente_schimbate_adaugate','')}\nDurata: {r.get('DURATA_INTERVENTIE','-')} | Obs: {r.get('OBSERVATII','')}"
                user_str = str(r.get('OPERATOR','-'))

                y_start = pdf.get_y()

                pdf.set_xy(10 + cw[0] + cw[1], y_start)
                pdf.multi_cell(cw[2], 5, pdf.safe_text(op_str), 0, 'C')
                h_op = pdf.get_y() - y_start

                pdf.set_xy(10 + cw[0] + cw[1] + cw[2], y_start)
                pdf.multi_cell(cw[3], 5, pdf.safe_text(desc_str), 0, 'L')
                h_det = pdf.get_y() - y_start

                h_row = max(h_op, h_det, 8)

                if (y_start + h_row) > 275:
                    pdf.add_page()
                    pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", 'B', 9)
                    pdf.set_fill_color(220, 220, 220)
                    for i, h in enumerate(headers):
                        pdf.cell(cw[i], 8, pdf.safe_text(h), 1, 0, 'C', True)
                    pdf.ln()
                    pdf.set_font("DejaVu" if pdf.font_loaded else "Arial", '', 8)
                    y_start = pdf.get_y()

                pdf.set_y(y_start)
                x_curr = 10

                pdf.set_xy(x_curr, y_start)
                pdf.cell(cw[0], h_row, pdf.safe_text(data_str), 1, 0, 'C')

                x_curr += cw[0]
                pdf.set_xy(x_curr, y_start)
                pdf.cell(cw[1], h_row, pdf.safe_text(tip_str), 1, 0, 'C')

                x_curr += cw[1]
                pdf.set_xy(x_curr, y_start)
                pdf.multi_cell(cw[2], 5, pdf.safe_text(op_str), 0, 'C')
                pdf.set_xy(x_curr, y_start)
                pdf.cell(cw[2], h_row, "", 1, 0)

                x_curr += cw[2]
                pdf.set_xy(x_curr, y_start)
                pdf.multi_cell(cw[3], 5, pdf.safe_text(desc_str), 0, 'L')
                pdf.set_xy(x_curr, y_start)
                pdf.cell(cw[3], h_row, "", 1, 0)

                x_curr += cw[3]
                pdf.set_xy(x_curr, y_start)
                pdf.cell(cw[4], h_row, pdf.safe_text(user_str), 1, 0, 'C')

                pdf.set_y(y_start + h_row)

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
