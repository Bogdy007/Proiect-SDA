import os, datetime, tempfile, qrcode, mysql.connector, functools
from flask import Flask, jsonify, request, make_response, send_from_directory, session
from fpdf import FPDF
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. INIȚIALIZARE ȘI CONFIGURARE ---
# Creăm aplicația Flask și permitem fișierelor statice (HTML/CSS) să fie servite din folderul curent.
app = Flask(__name__, static_url_path='', static_folder='.')
app.secret_key = 'cheie_secreta'  # Cheia pentru semnarea sesiunilor (cookies)
CORS(app)  # Permitem cereri Cross-Origin (utile în dezvoltare)

# Determinăm calea absolută către fontul pentru diacritice
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, 'DejaVuSans.ttf')

# Datele de conectare la MySQL (PythonAnywhere)
baza_date = {
    'host': 'moro2004.mysql.pythonanywhere-services.com',
    'database': 'moro2004$it_inventar',
    'user': 'moro2004',
    'password': 'oB6Nwm42a333ATV'
}

# --- 2. CONSTANTE PENTRU TABELE ---
# Definim listele de coloane o singură dată pentru a nu le repeta la fiecare INSERT/UPDATE.
COLS_ECHIP = ['NR_INVENTAR', 'CATEGORIE', 'TIP_CALC', 'NUME_PC', 'UTILIZATOR', 'NR_USER', 'DATA_ACHIZITIE', 'ETAJ',
              'FUNCTIE', 'IP', 'RETEA', 'SERIE_UC', 'SERIE_MON', 'MEMORIE', 'SISTEM_OPERARE', 'LICENTA_SO', 'OFFICE',
              'LICENTA_OFFICE', 'ANTIVIRUS', 'CAMERA', 'TELEFON', 'PERIFERICE', 'PARCHET', 'PASS', 'OBS']
COLS_PERIF = ['NR_INVENTAR', 'CATEGORIE', 'TIP', 'PRODUCATOR', 'NUME_PERIFERICE', 'UTILIZATOR', 'NUME_USER',
              'DATA_ACHIZITIE', 'NUME_CALC', 'SERIE_UC', 'IP', 'RETEA', 'MEMORIE', 'FORMAT', 'CULOARE_IMPRIMARE',
              'DUPLEX', 'STARE_PARAMETRI', 'CAMERA', 'ANTIVIRUS', 'PARCHET', 'PASS', 'OBS', 'OBS2']


# --- 3. FUNCȚII HELPER (OPTIMIZARE) ---

# Funcție universală pentru interogări SQL.
# Deschide conexiunea, execută query-ul și o închide automat.
def conectare_baza_date(sql, params=(), one=False, commit=False):
    conn = mysql.connector.connect(**baza_date)
    cur = conn.cursor(dictionary=True)  # Rezultatele vin ca dicționare {cheie: valoare}
    try:
        cur.execute(sql, params)
        if commit: conn.commit(); return True  # Pentru INSERT/UPDATE/DELETE
        return cur.fetchone() if one else cur.fetchall()  # Pentru SELECT
    except Exception as e:
        raise e  # Aruncăm eroarea mai departe
    finally:
        conn.close()  # Se execută mereu, garantând închiderea conexiunii


# Decorator care prinde orice eroare din rute și returnează JSON, ca să nu pice serverul.
def gestioneaza_erori_api(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"succes": False, "eroare": str(e)}), 500

    return wrapper


# Decorator: Verifică dacă utilizatorul este logat
def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs) if 'user_id' in session else (jsonify({"eroare": "Neautorizat"}), 401)

    return decorated


# Decorator: Verifică dacă utilizatorul este Admin
def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs) if session.get('role') == 'admin' else (jsonify({"eroare": "Acces interzis"}), 403)

    return decorated


# Middleware: Dezactivează cache-ul browserului pentru date mereu proaspete
@app.after_request
def add_header(r):
    r.headers.update({"Cache-Control": "no-store", "Pragma": "no-cache", "Expires": "0"})
    return r


# --- 4. CLASA PENTRU GENERARE PDF ---
class RaportPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # Încărcăm fontul cu suport Unicode (Română) dacă există
        if os.path.exists(FONT_PATH):
            self.add_font('DejaVu', '', FONT_PATH, uni=True)
            self.add_font('DejaVu', 'B', FONT_PATH, uni=True)
        self.font_fam = 'DejaVu' if os.path.exists(FONT_PATH) else 'Arial'

    # Funcție care pune "-" dacă un câmp e gol
    def safe_text(self, txt):
        return str(txt) if txt and str(txt).lower() not in ['none', 'null', ''] else "-"

    # Header automat pe fiecare pagină (Banda Albastră)
    def header(self):
        self.set_fill_color(13, 71, 161);
        self.rect(0, 0, 210, 5, 'F');
        self.set_y(10)
        self.set_font(self.font_fam, '', 8)
        self.cell(0, 6, 'PARCHETUL DE PE LÂNGĂ TRIBUNALUL BRAȘOV | IT', 0, 1, 'R')
        self.set_draw_color(200);
        self.line(10, 18, 200, 18);
        self.ln(5)

    # Footer automat (Data și Nr. Pagină)
    def footer(self):
        self.set_y(-15);
        self.set_font(self.font_fam, '', 7);
        self.set_text_color(150)
        self.cell(0, 10, f'Generat: {datetime.datetime.now():%d.%m.%Y %H:%M} | Pag {self.page_no()}/{{nb}}', 0, 0, 'C')

    # Desenează un titlu de secțiune cu fundal gri-albastru
    def section_title(self, label):
        if self.get_y() > 250: self.add_page()  # Pagină nouă dacă nu e loc
        self.ln(5);
        self.set_font(self.font_fam, 'B', 12)
        self.set_fill_color(230, 240, 255);
        self.set_text_color(13, 71, 161)
        self.cell(0, 8, f"  {self.safe_text(label.upper())}", 'L', 1, 'L', True)
        self.ln(3);
        self.set_text_color(0)

    # Desenează un rând de informații: Etichetă (stânga) - Valoare (dreapta)
    def info_row(self, label, value):
        if self.get_y() > 275: self.add_page()
        self.set_font(self.font_fam, '', 9);
        self.set_text_color(100)
        self.cell(50, 6, label, 0, 0, 'R')  # Eticheta aliniată la dreapta
        self.set_text_color(0);
        x = self.get_x()
        self.multi_cell(140, 6, self.safe_text(value), 0, 'L')  # Valoarea pe mai multe rânduri
        self.set_draw_color(240);
        self.line(x, self.get_y(), 200, self.get_y());
        self.ln(1)


# --- 5. RUTE API: AUTHENTICARE ---
@app.route('/')
def serve_index(): return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_files(path): return send_from_directory('.', path)


@app.route('/api/login', methods=['POST'])
@gestioneaza_erori_api
def login():
    data = request.json
    # Căutăm userul în DB
    user = conectare_baza_date("SELECT * FROM users WHERE username=%s", (data.get('username'),), one=True)
    # Verificăm parola criptată (Hash)
    if user and check_password_hash(user['password'], data.get('password')):
        session.update({'user_id': user['id'], 'username': user['username'], 'role': user['role']})
        return jsonify({"succes": True, "role": user['role']})
    return jsonify({"succes": False, "eroare": "Date incorecte"}), 401


@app.route('/api/logout', methods=['POST'])
def logout(): session.clear(); return jsonify({"succes": True})


# --- 6. RUTE API: ADMINISTRARE UTILIZATORI ---
@app.route('/api/users')
@admin_required
@gestioneaza_erori_api
def lista_utilizatori():
    return jsonify(conectare_baza_date("SELECT id, username, role FROM users"))


@app.route('/api/users/add', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def add_user():
    d = request.json
    # Inserăm user nou cu parola criptată
    conectare_baza_date("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                        (d['username'], generate_password_hash(d['password']), d.get('role', 'viewer')), commit=True)
    return jsonify({"succes": True})


@app.route('/api/users/delete/<int:id>', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def del_user(id):
    # Protecție: Nu ștergem Super Adminul (ID 1) și nici pe noi înșine
    if id == 1 or id == session.get('user_id'): return jsonify({"eroare": "Interzis"}), 400
    conectare_baza_date("DELETE FROM users WHERE id=%s", (id,), commit=True)
    return jsonify({"succes": True})
# --- VERIFICARE SESIUNE (Lipsea asta!) ---
@app.route('/api/me', methods=['GET'])
def verifica_sesiune():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "username": session.get('username'),
            "role": session.get('role')
        })
    return jsonify({"logged_in": False})

# --- 7. RUTE API: INVENTAR (CĂUTARE & DETALII) ---
@app.route('/api/assets/all')
@login_required
@gestioneaza_erori_api
def search_echipaments():
    args = request.args
    # Interogare UNION pentru a uni Echipamentele cu Perifericele
    q = "SELECT * FROM (SELECT NR_INVENTAR, CATEGORIE, TIP_CALC AS TIP, NUME_PC AS NUME, UTILIZATOR, ETAJ, IP, SERIE_UC AS SERIE FROM Echipamente UNION SELECT NR_INVENTAR, CATEGORIE, TIP, NUME_PERIFERICE AS NUME, UTILIZATOR, NULL, IP, SERIE_UC FROM Periferice) AS a"

    # Construim filtrele dinamic
    filters = {'nr_inventar': 'NR_INVENTAR LIKE', 'utilizator': 'UTILIZATOR LIKE', 'etaj': 'ETAJ =',
               'nume': 'NUME LIKE', 'ip': 'IP LIKE'}
    where, params = [], []
    for k, op in filters.items():
        if v := args.get(k, '').strip():
            where.append(f"{op} %s")
            params.append(f"%{v}%" if 'LIKE' in op else v)

    if where: q += " WHERE " + " AND ".join(where)
    return jsonify(conectare_baza_date(q, tuple(params)))


@app.route('/api/<type>/<path:nr>', methods=['GET'])
@login_required
@gestioneaza_erori_api
def item_details(type, nr):
    # Selectăm tabelul corect în funcție de tip
    tbl = 'Echipamente' if type == 'echipament' else 'Periferice'
    return jsonify(conectare_baza_date(f"SELECT * FROM {tbl} WHERE NR_INVENTAR=%s", (nr.strip(),), one=True))


# --- 8. FUNCȚIE HELPER PENTRU CRUD (Magic Function) ---
# Se ocupă automat de INSERT sau UPDATE, verifică duplicatele și asociază valorile cu coloanele
def verificare_duplicitate(table, cols, data, is_update=False, pk_val=None):
    # Extragem valorile din JSON în ordinea coloanelor
    vals = [data.get(c, '').strip() if isinstance(data.get(c), str) else data.get(c) for c in cols]

    if is_update:
        # Generăm: COL1=%s, COL2=%s...
        sets = ', '.join([f"{c}=%s" for c in cols])
        vals.append(pk_val)  # Adăugăm ID-ul la final pentru WHERE
        conectare_baza_date(f"UPDATE {table} SET {sets} WHERE NR_INVENTAR=%s", vals, commit=True)
    else:
        # Verificăm dacă există deja (Duplicate check)
        if conectare_baza_date(f"SELECT 1 FROM {table} WHERE NR_INVENTAR=%s", (data.get('NR_INVENTAR'),), one=True): return False
        # Generăm: VALUES (%s, %s, %s...)
        conectare_baza_date(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s'] * len(cols))})", vals, commit=True)
    return True


# --- 9. RUTE ADĂUGARE / ACTUALIZARE / ȘTERGERE ---
# Folosesc funcția crud_save pentru a fi foarte scurte

@app.route('/api/echipamente/add', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def add_eq():
    return jsonify({"succes": True}) if verificare_duplicitate('Echipamente', COLS_ECHIP, request.json) else (
        jsonify({"eroare": "Duplicat"}), 400)


@app.route('/api/periferice/add', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def add_perif():
    return jsonify({"succes": True}) if verificare_duplicitate('Periferice', COLS_PERIF, request.json) else (
        jsonify({"eroare": "Duplicat"}), 400)


@app.route('/api/echipamente/update/<path:nr>', methods=['PUT'])
@admin_required
@gestioneaza_erori_api
def upd_eq(nr):
    # Excludem Nr Inventar din update (nu se schimbă)
    verificare_duplicitate('Echipamente', [c for c in COLS_ECHIP if c != 'NR_INVENTAR'], request.json, True, nr.strip())
    return jsonify({"succes": True})


@app.route('/api/periferice/update/<path:nr>', methods=['PUT'])
@admin_required
@gestioneaza_erori_api
def upd_perif(nr):
    verificare_duplicitate('Periferice', [c for c in COLS_PERIF if c != 'NR_INVENTAR'], request.json, True, nr.strip())
    return jsonify({"succes": True})


@app.route('/api/assets/delete/<path:nr>', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def del_art(nr):
    # Ștergem din ambele tabele pentru siguranță
    conectare_baza_date("DELETE FROM Echipamente WHERE NR_INVENTAR=%s", (nr,), commit=True)
    conectare_baza_date("DELETE FROM Periferice WHERE NR_INVENTAR=%s", (nr,), commit=True)
    return jsonify({"succes": True})


# --- 10. INTERVENȚII ---
@app.route('/api/interventii/<path:nr>')
@login_required
@gestioneaza_erori_api
def get_istoric_interventii(nr):
    return jsonify(
        conectare_baza_date("SELECT * FROM Interventii WHERE NR_INVENTAR=%s ORDER BY DATA_INTERVENTIE DESC", (nr.strip(),)))


@app.route('/api/interventii/add', methods=['POST'])
@admin_required
@gestioneaza_erori_api
def add_int():
    d = request.json
    conectare_baza_date(
        "INSERT INTO Interventii (NR_INVENTAR, TIP_ECHIPAMENT, DATA_INTERVENTIE, TIP_INTERVENTIE, TIP_OPERATIE, DESCRIERE_INTERVENTIE, componente_schimbate_adaugate, DURATA_INTERVENTIE, OPERATOR, OBSERVATII) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (d.get('NR_INVENTAR'), d.get('TIP_ECHIPAMENT'), d.get('DATA_INTERVENTIE'), d.get('TIP_INTERVENTIE'),
         d.get('TIP_OPERATIE'), d.get('DESCRIERE_INTERVENTIE'), d.get('componente_schimbate_adaugate'),
         d.get('DURATA_INTERVENTIE'), d.get('OPERATOR'), d.get('OBSERVATII')), commit=True)
    return jsonify({"succes": True})


# --- 11. GENERARE ETICHETĂ QR ---
@app.route('/api/print_label/<path:nr>', methods=['GET'])
def genereaza_qr(nr):
    try:
        # Căutăm echipamentul
        item = conectare_baza_date(
            "SELECT * FROM Echipamente WHERE NR_INVENTAR=%s UNION SELECT * FROM Periferice WHERE NR_INVENTAR=%s",
            (nr, nr), one=True)
        if not item: return jsonify({"eroare": "404"}), 404

        # Generăm QR Code cu link
        qr = qrcode.make(
            f"{request.host_url}detalii.html?id={nr}&type={'periferic' if 'NUME_PERIFERICE' in item else 'echipament'}",
            box_size=6, border=2)
        temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False);
        qr.save(temp.name)

        # Generăm PDF 60x90mm
        pdf = FPDF('L', 'mm', (60, 90));
        pdf.set_margins(2, 2, 2);
        pdf.set_auto_page_break(False);
        pdf.add_page()
        pdf.set_font('Arial', 'B', 8);
        pdf.cell(90, 4, 'PARCHETUL DE PE LANGA TRIBUNALUL BRASOV', 0, 1, 'C')
        pdf.image(temp.name, x=31, y=8, w=28)  # QR Centrat
        pdf.set_y(38);
        pdf.set_font('Arial', 'B', 14);
        pdf.cell(0, 6, str(nr), 0, 1, 'C')

        # Curățenie
        temp.close();
        os.unlink(temp.name)
        return make_response(pdf.output(dest='S'), 200,
                             {'Content-Type': 'application/pdf', 'Content-Disposition': f'inline; filename=L_{nr}.pdf'})
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


# --- 12. GENERARE FIȘĂ INVENTAR (Complexă) ---
@app.route('/api/print/<path:nr>', methods=['GET'])
def genereaza_pdf(nr):
    try:
        # Identificăm tipul și datele
        item = conectare_baza_date("SELECT * FROM Echipamente WHERE NR_INVENTAR=%s", (nr,), one=True)
        tipo, lst = ('echipament', COLS_ECHIP) if item else ('periferic', COLS_PERIF)
        if not item:
            item = conectare_baza_date("SELECT * FROM Periferice WHERE NR_INVENTAR=%s", (nr,), one=True)
            if not item: return jsonify({"eroare": "Negasit"}), 404

        interv = conectare_baza_date("SELECT * FROM Interventii WHERE NR_INVENTAR=%s ORDER BY DATA_INTERVENTIE DESC", (nr,))

        # Inițializăm PDF
        pdf = RaportPDF();
        pdf.alias_nb_pages();
        pdf.add_page();
        pdf.set_font(pdf.font_fam, 'B', 22)
        pdf.cell(0, 15, pdf.safe_text(f"FIȘĂ INVENTAR: {item['NR_INVENTAR']}"), 0, 1, 'C')

        # Scriem datele generale
        pdf.section_title("DATE ARTICOL")
        for k in lst:
            if val := item.get(k): pdf.info_row(k, val)

        # Desenăm Tabelul de Intervenții (partea complexă)
        pdf.add_page();
        pdf.section_title("ISTORIC INTERVENȚII")
        cw, headers = [25, 25, 40, 70, 30], ["Data", "Tip", "Operație", "Detalii", "Operator"]
        pdf.set_font(pdf.font_fam, 'B', 9);
        pdf.set_fill_color(220, 220, 220)
        # Header tabel
        for i, h in enumerate(headers): pdf.cell(cw[i], 8, pdf.safe_text(h), 1, 0, 'C', True)
        pdf.ln();
        pdf.set_font(pdf.font_fam, '', 8)

        if not interv: pdf.cell(0, 10, "Fără intervenții.", 0, 1, 'L')
        for r in interv:
            # Pregătim datele pentru rând
            vals = [str(r.get(k, '-')) for k in ['DATA_INTERVENTIE', 'TIP_INTERVENTIE', 'TIP_OPERATIE']]
            vals.append(
                f"{r.get('DESCRIERE_INTERVENTIE', '-')}\nComp: {r.get('componente_schimbate_adaugate', '')}\nObs: {r.get('OBSERVATII', '')}")
            vals.append(str(r.get('OPERATOR', '-')))

            # Calculăm înălțimea necesară (wrap text)
            y_s = pdf.get_y()
            pdf.set_xy(10 + sum(cw[:3]), y_s);
            pdf.multi_cell(cw[3], 5, pdf.safe_text(vals[3]), 0, 'L')
            h_row = max(pdf.get_y() - y_s, 8)

            # Page Break dacă e nevoie
            if y_s + h_row > 275: pdf.add_page(); y_s = pdf.get_y()

            # Desenăm rândul efectiv
            pdf.set_y(y_s);
            x = 10
            for i, txt in enumerate(vals):
                pdf.set_xy(x, y_s)
                # Logică pentru coloanele MultiCell vs Simple Cell
                if i == 3:
                    pdf.multi_cell(cw[i], 5, pdf.safe_text(txt), 0, 'L'); pdf.set_xy(x, y_s); pdf.cell(cw[i], h_row, "",
                                                                                                       1)
                elif i == 2:
                    pdf.multi_cell(cw[i], 5, pdf.safe_text(txt), 0, 'C'); pdf.set_xy(x, y_s); pdf.cell(cw[i], h_row, "",
                                                                                                       1)
                else:
                    pdf.cell(cw[i], h_row, pdf.safe_text(txt), 1, 0, 'C')
                x += cw[i]
            pdf.set_y(y_s + h_row)

        return make_response(pdf.output(dest='S'), 200, {'Content-Type': 'application/pdf',
                                                         'Content-Disposition': f'inline; filename=Fisa_{nr}.pdf'})
    except Exception as e:
        return jsonify({"eroare": str(e)}), 500


if __name__ == '__main__': app.run(debug=True)
