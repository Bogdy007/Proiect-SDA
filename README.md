# 🖥️ Sistem Integrat de Gestiune a Inventarului IT

> O aplicație web Full-Stack pentru digitalizarea și administrarea infrastructurii IT, dezvoltată pentru **Parchetul de pe lângă Tribunalul Brașov**.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-black?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)
![Frontend](https://img.shields.io/badge/HTML5%20%26%20CSS3-Glassmorphism-pink?style=for-the-badge)

## 📖 Descriere

Acest proiect a fost creat pentru a înlocui evidențele manuale (registre, Excel) cu o soluție digitală centralizată. Aplicația permite departamentului IT să gestioneze ciclul de viață al echipamentelor, să monitorizeze intervențiile de service și să genereze automat documente oficiale.

Proiectul este găzduit în cloud pe infrastructura **PythonAnywhere** și utilizează o arhitectură Client-Server optimizată pentru performanță.

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

*(Aici poți încărca imagini cu aplicația ta în folderul repository-ului și să pui link-uri către ele)*

| Dashboard Principal | Detalii & Istoric Service |
|:---:|:---:|
| *[Imagine Dashboard]* | *[Imagine Detalii]* |

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

## 🧩 Structura Proiectului
