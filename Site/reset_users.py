import mysql.connector

# --- CONFIGURARE BAZA DE DATE (Aceleași ca în main.py) ---
data_base = {
    'host': 'moro2004.mysql.pythonanywhere-services.com',
    'database': 'moro2004$it_inventar',
    'user': 'moro2004',
    'password': 'oB6Nwm42a333ATV',
    'port': 3306
}

def reset_users():
    try:
        print("Conectare la baza de date...")
        conn = mysql.connector.connect(**data_base)
        cursor = conn.cursor()

        # 1. Ștergem cererile de resetare parolă pentru utilizatorii pe care îi vom șterge
        # (Ca să nu avem erori de Foreign Key)
        print("Ștergere notificări vechi...")
        cursor.execute("DELETE FROM reset_requests WHERE user_id > 1")

        # 2. Ștergem toți utilizatorii în afară de ID 1 (Super Admin)
        print("Ștergere utilizatori secundari (ID > 1)...")
        cursor.execute("DELETE FROM users WHERE id > 1")
        deleted_count = cursor.rowcount
        print(f"Au fost șterși {deleted_count} utilizatori.")

        # 3. Resetăm contorul ID să înceapă de la următorul număr liber (adică 2)
        print("Resetare contor ID la 2...")
        cursor.execute("ALTER TABLE users AUTO_INCREMENT = 2")

        conn.commit()
        print("\nSUCCES! Baza de date a utilizatorilor a fost curățată.")
        print("Următorul utilizator creat va avea ID-ul 2.")

    except mysql.connector.Error as err:
        print(f"Eroare SQL: {err}")
    except Exception as e:
        print(f"Eroare generală: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexiune închisă.")

if __name__ == "__main__":
    confirmare = input("Ești sigur că vrei să ștergi toți utilizatorii în afară de Admin? (scrie 'da'): ")
    if confirmare.lower() == 'da':
        reset_users()
    else:
        print("Operațiune anulată.")