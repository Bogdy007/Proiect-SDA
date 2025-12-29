import mysql.connector
from werkzeug.security import generate_password_hash

# --- CONFIGURARE BAZA DE DATE (Aceleași date ca în main.py) ---
data_base = {
    'host': 'moro2004.mysql.pythonanywhere-services.com',
    'database': 'moro2004$it_inventar',
    'user': 'moro2004',
    'password': 'oB6Nwm42a333ATV',
    'port': 3306
}

def reset_users():
    conn = None
    try:
        print("🔄 Se conectează la baza de date...")
        conn = mysql.connector.connect(**data_base)
        cursor = conn.cursor()

        # 1. ȘTERGEM TOȚI UTILIZATORII EXISTENȚI
        print("🗑️  Se șterg utilizatorii vechi...")
        cursor.execute("DELETE FROM users")

        # Încercăm să resetăm contorul de ID la 1 (ca adminul să fie mereu ID 1)
        try:
            cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1")
        except:
            pass # Dacă dă eroare, nu e critic, continuăm

        # 2. CREĂM UTILIZATORII DEFAULT

        # --- CONT ADMIN ---
        # Username: admin
        # Parola: admin
        pass_admin = generate_password_hash("admin")
        sql_admin = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql_admin, ('admin', pass_admin, 'admin'))
        print("✅ Creat cont ADMIN -> User: admin | Parola: admin")

        # --- CONT VIEWER (Utilizator simplu) ---
        # Username: user
        # Parola: user
        pass_user = generate_password_hash("user")
        sql_user = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql_user, ('user', pass_user, 'viewer'))
        print("✅ Creat cont USER  -> User: user  | Parola: user")

        # 3. SALVĂM MODIFICĂRILE
        conn.commit()
        print("\n🎉 RESETARE COMPLETĂ! Acum te poți loga pe site.")

    except Exception as e:
        print(f"\n❌ EROARE: {str(e)}")

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    reset_users()