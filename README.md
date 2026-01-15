# 🖥️ Sistem Integrat de Gestiune a Inventarului IT

> O aplicație web Full-Stack modernă pentru digitalizarea, administrarea și urmărirea infrastructurii IT, dezvoltată pentru **Parchetul de pe lângă Tribunalul Brașov**.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)
![Frontend](https://img.shields.io/badge/Vanilla%20JS-Dark%20Mode-yellow?style=for-the-badge&logo=javascript&logoColor=white)

## 📖 Descriere

Acest proiect transformă procesul de inventariere dintr-o sarcină manuală într-un flux digital automatizat. Aplicația permite departamentului IT să gestioneze ciclul de viață al echipamentelor, să monitorizeze intervențiile de service în timp real și să genereze documente oficiale instantaneu.

Proiectul este găzduit în cloud pe infrastructura **PythonAnywhere** și utilizează o arhitectură Client-Server optimizată.

🔗 **Demo Live:** [Acces Aplicație](https://moro2004.pythonanywhere.com/login.html)

---

## ✨ Funcționalități Cheie

### 1. 📱 Smart QR & Deep Linking
* **Scanare Inteligentă:** Fiecare echipament are o etichetă QR unică. Scanarea cu telefonul deschide instant fișa tehnică.
* **Flux de Autentificare:** Dacă utilizatorul nu este logat la scanare, aplicația îl redirecționează la Login și apoi **îl întoarce automat** la produsul scanat (nu se pierde contextul).

### 2. 📦 Gestiunea Avansată a Activelor
* **Inventar Hibrid:** Suportă atât *Echipamente IT* (PC, Laptop), cât și *Periferice* (Imprimante), cu câmpuri specifice pentru fiecare.
* **Căutare Instantă:** Filtrare în timp real după IP, Serie, Utilizator sau Etaj.

### 3. 📄 Motor de Raportare PDF Custom
* Generare vectorială a Fișelor de Inventar folosind `FPDF`.
* **Algoritm Word-Wrap:** Tabelul de intervenții își ajustează automat înălțimea rândurilor pentru a afișa descrieri lungi fără suprapunere.
* Suport complet pentru diacritice românești (font `DejaVuSans`).

### 4. 🎨 Interfață Modernă (UX/UI)
* **Dark Mode:** Comutare instantă între teme (Light/Dark) cu persistență în browser.
* **SPA Feel:** Adăugarea și editarea intervențiilor se face prin ferestre modale, fără reîncărcarea paginii.
* **Responsive:** Optimizat pentru desktop, tabletă și mobil.

---

## 🛠️ Stack Tehnologic

| Componentă | Tehnologie | Detalii |
| :--- | :--- | :--- |
| **Backend** | Python 3 + Flask | API RESTful, securitate cu `werkzeug`. |
| **Bază de Date** | MySQL (Cloud) | Model relațional, conexiuni optimizate. |
| **Frontend** | HTML5, CSS3, JS | Vanilla JS, Fetch API, CSS Variables. |
| **PDF Engine** | PyFPDF | Generare dinamică a documentelor. |
| **Deployment** | PythonAnywhere | Configurare WSGI pe server Nginx. |

---

## 📸 Capturi de Ecran

<img width="1484" height="732" alt="Screenshot 2025-12-29 at 22 39 47" src="https://github.com/user-attachments/assets/3ffb7b20-3699-482e-bd9a-21d21167781c" />
<img width="1469" height="753" alt="Screenshot 2025-12-29 at 22 39 37" src="https://github.com/user-attachments/assets/caa28f18-ca95-4991-a86c-d2725c090b63" />
<img width="1499" height="749" alt="Screenshot 2025-12-29 at 22 39 22" src="https://github.com/user-attachments/assets/e310980f-659c-4a9b-ac56-a6b5299b026b" />
<img width="1489" height="753" alt="Screenshot 2025-12-29 at 22 38 32" src="https://github.com/user-attachments/assets/e91b47d6-5239-4549-96bf-6807c5c4688c" />
<img width="444" height="768" alt="Screenshot 2025-12-29 at 22 38 19" src="https://github.com/user-attachments/assets/c47f8ec5-f257-4a0a-8b0c-954f639905e7" />
<img width="1510" height="853" alt="Screenshot 2025-12-29 at 22 31 15" src="https://github.com/user-attachments/assets/09496ffc-c8e2-47fc-ac33-1314b4dff78c" />
<img width="1512" height="853" alt="Screenshot 2025-12-29 at 22 31 05" src="https://github.com/user-attachments/assets/f560ee1b-950a-47dd-bd40-8fdef5807eef" />
<img width="1481" height="853" alt="Screenshot 2025-12-29 at 22 30 58" src="https://github.com/user-attachments/assets/8ec05e42-4736-4bb4-8b56-5857caef2d08" />
<img width="1475" height="756" alt="Screenshot 2025-12-29 at 22 29 44" src="https://github.com/user-attachments/assets/d490800e-a352-40bc-ace8-3bedb7848b68" />
<img width="1494" height="758" alt="Screenshot 2025-12-29 at 22 29 29" src="https://github.com/user-attachments/assets/b45698e2-502f-4e8f-b86f-c8bd735fef14" />

---

## 🚀 Instalare și Rulare Locală

Pentru a testa aplicația pe mașina locală (fără server cloud):

1.  **Clonează repository-ul:**
    ```bash
    git clone [https://github.com/userul-tau/nume-repo.git](https://github.com/userul-tau/nume-repo.git)
    cd nume-repo
    ```

2.  **Instalează dependențele:**
    ```bash
    pip install flask mysql-connector-python fpdf qrcode[pil] flask-cors werkzeug
    ```

3.  **Configurare Bază de Date:**
    * Modifică fișierul `main.py` pentru a folosi o bază de date locală (dacă nu ai acces la cea din cloud):
    ```python
    data_base = {
        'host': 'localhost',
        'database': 'it_inventar',
        'user': 'root',
        'password': '',
        'port': 3306
    }
    ```

4.  **Pornește serverul:**
    ```bash
    python main.py
    ```
    Accesează `http://127.0.0.1:5000` în browser.

---

## 👥 Echipa de Dezvoltare (BRSA Team)

* **Panainte Bogdan:** Backend & Security
* **Moroșanu Răzvan:** Frontend & UX Design
* **Neculcea Sabin:** Reporting Module (PDF) & Frontend
* **Pricop Andrei:** Database Architect

---

## 📝 Licență

Acest proiect a fost dezvoltat în scop educațional și operațional pentru Parchetul de pe lângă Tribunalul Brașov.
