# 🖥️ Sistem Integrat de Gestiune a Inventarului IT

> O aplicație web Full-Stack pentru digitalizarea și administrarea infrastructurii IT, dezvoltată pentru **Parchetul de pe lângă Tribunalul Brașov**.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-black?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)
![Frontend](https://img.shields.io/badge/HTML5%20%26%20CSS3-Glassmorphism-pink?style=for-the-badge)

## 📖 Descriere

Acest proiect a fost creat pentru a înlocui evidențele manuale (registre, Excel) cu o soluție digitală centralizată. Aplicația permite departamentului IT să gestioneze ciclul de viață al echipamentelor, să monitorizeze intervențiile de service și să genereze automat documente oficiale.

Proiectul este găzduit în cloud pe infrastructura **PythonAnywhere** și utilizează o arhitectură Client-Server optimizată pentru performanță. Si poate fi accesat aici: https://moro2004.pythonanywhere.com/login.html

---

## ✨ Funcționalități Cheie

### 1. 📦 Gestiunea Activelor (Asset Management)
* **Evidență Unificată:** Gestionarea a două tipuri de entități (*Echipamente IT* și *Periferice*) într-o interfață comună.
* **Formulare Dinamice:** Interfața de adăugare/editare se adaptează automat (Context-Aware) în funcție de tipul echipamentului selectat.
* **Validare:** Prevenirea duplicatelor prin validare server-side a numerelor de inventar.

### 2. 🛠️ Caiet de Service Digital
* Monitorizarea istoricului de mentenanță pentru fiecare dispozitiv.
* Înregistrarea detaliată a intervențiilor: *Dată, Operator, Tip Intervenție (Hardware/Software), Componente înlocuite*.

### 3. 📄 Generator de Rapoarte PDF Custom
* Motor propriu de generare a PDF-urilor folosind librăria `FPDF`.
* **Nu** este o simplă imprimare de ecran: documentul este desenat vectorial, pixel-perfect.
* Suport complet pentru diacritice românești (font `DejaVuSans`).
* Tabele dinamice care se ajustează automat la lungimea textului.

### 4. 🔒 Securitate și Administrare
* **RBAC (Role-Based Access Control):** Roluri de `Admin` (CRUD) și `Viewer` (Read-only).
* **Securitate:** Parole criptate folosind SHA256 (`werkzeug.security`).
* **Protecție API:** Decoratori custom `@admin_required` pentru protejarea rutelor sensibile.

---

## 🛠️ Stack Tehnologic

| Componentă | Tehnologie | Detalii |
| :--- | :--- | :--- |
| **Backend** | Python 3 + Flask | API RESTful, Server-side logic. |
| **Bază de Date** | MySQL | Stocare relațională, găzduire cloud. |
| **Frontend** | HTML5, CSS3, JS | Vanilla JS (Fetch API), Design "Glassmorphism". |
| **PDF Engine** | PyFPDF | Generare programatică a documentelor. |
| **Deployment** | PythonAnywhere | Configurare WSGI, server Nginx. |

---

## 📸 Capturi de Ecran (Screenshots)

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

Pentru a testa aplicația pe mașina locală:

1.  **Clonează repository-ul:**
    ```bash
    git clone [https://github.com/userul-tau/nume-repo.git](https://github.com/userul-tau/nume-repo.git)
    cd nume-repo
    ```

2.  **Creează un mediu virtual (opțional dar recomandat):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Pe Windows: venv\Scripts\activate
    ```

3.  **Instalează dependențele:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Notă: Asigură-te că ai instalat `flask`, `mysql-connector-python`, `fpdf`, `flask-cors`)*

4.  **Configurare Bază de Date:**
    * Importă structura bazei de date (fișier SQL) în serverul tău local MySQL.
    * Actualizează dicționarul `data_base` în fișierul `main.py`:
    ```python
    data_base = {
        'host': 'localhost',
        'database': 'nume_baza_date',
        'user': 'root',
        'password': 'parola_ta',
        'port': 3306
    }
    ```

5.  **Pornește serverul:**
    ```bash
    python main.py
    ```
    Accesează `http://127.0.0.1:5000` în browser.

---


## 📝 Licență

Acest proiect a fost dezvoltat în scop educațional și operațional pentru Parchetul de pe lângă Tribunalul Brașov.

---

**Dezvoltat de:** Morosanu Razvan, Panainte Bogdan Dumitru, Neculcea Sabin, Pricop Andrei.
