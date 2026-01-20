#  Sistem Integrat de Gestiune a Inventarului IT

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

##  Funcționalități Cheie

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
<details>
  <summary><strong>🔍 Apasă aici pentru a vedea capturile de ecran</strong></summary>
  <br>
📸 Capturi de Ecran
<img width="1508" height="771" alt="Screenshot 2026-01-15 at 22 06 46" src="https://github.com/user-attachments/assets/d3349a61-2a96-4072-b789-4456fa2ac330" />
<img width="1267" height="623" alt="Screenshot 2026-01-15 at 22 06 54" src="https://github.com/user-attachments/assets/b9167809-4a70-4d3f-8f02-12e7c15208d7" />
<img width="1512" height="779" alt="Screenshot 2026-01-15 at 22 07 08" src="https://github.com/user-attachments/assets/df6a058c-8b34-4c2e-8824-f9df66241674" />
<img width="1512" height="771" alt="Screenshot 2026-01-15 at 22 07 17" src="https://github.com/user-attachments/assets/e0dcc6e1-cc3d-4fed-868e-5462737230a1" />
<img width="1512" height="770" alt="Screenshot 2026-01-15 at 22 07 53" src="https://github.com/user-attachments/assets/03eca0bd-5fe4-4689-8552-7533d98f8932" />
<img width="1512" height="774" alt="Screenshot 2026-01-15 at 22 08 09" src="https://github.com/user-attachments/assets/8064efa3-b94e-4dea-8a74-a1ce1fabf072" />
<img width="1512" height="755" alt="Screenshot 2026-01-15 at 22 08 17" src="https://github.com/user-attachments/assets/9f1e4d84-ef09-47f4-8464-c34bef40add6" />
<img width="1512" height="766" alt="Screenshot 2026-01-15 at 22 08 24" src="https://github.com/user-attachments/assets/a4aa6e3b-a1cc-4ead-b8b8-3899b6419232" />
<img width="1512" height="767" alt="Screenshot 2026-01-15 at 22 08 41" src="https://github.com/user-attachments/assets/f2cb4704-2125-47b8-97d3-47aa012f6a0e" />
<img width="1512" height="770" alt="Screenshot 2026-01-15 at 22 08 49" src="https://github.com/user-attachments/assets/9baf4527-ac8e-4ec5-a6ae-81db3545bdb8" />
<img width="1150" height="325" alt="Screenshot 2026-01-15 at 22 09 06" src="https://github.com/user-attachments/assets/b2d5d94c-3f8b-49be-a94e-e689ebffe630" />
<img width="1512" height="774" alt="Screenshot 2026-01-15 at 22 09 13" src="https://github.com/user-attachments/assets/810fb4b8-2f38-43e6-ab99-3d29e69c59bf" />
<img width="1510" height="780" alt="Screenshot 2026-01-15 at 22 09 43" src="https://github.com/user-attachments/assets/9940e303-7252-4e16-814f-a77ee234db48" />
<img width="1512" height="778" alt="Screenshot 2026-01-15 at 22 09 50" src="https://github.com/user-attachments/assets/742b8e9d-8efd-4c3d-86aa-40ac2b381101" />

<br>
</details>



---

##  Instalare și Rulare Locală

Pentru a testa aplicația pe mașina locală (fără server cloud):

1.  **Clonează repository-ul:**
    ```bash
    git clone [https://github.com/Bogdy007/Proiect-SDA.git](https://github.com/Bogdy007/Proiect-SDA.git)
    cd Proiect-SDA
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
