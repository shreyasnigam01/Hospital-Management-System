import os
import mysql.connector

# Simple .env parser to avoid external library dependencies
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key_val = line.split('=', 1)
                    if len(key_val) == 2:
                        key = key_val[0].strip()
                        val = key_val[1].strip().strip('"').strip("'")
                        os.environ[key] = val

# Load env variables
load_env()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "@magin12345")
DB_NAME = os.environ.get("DB_NAME", "hospital")

def get_connection():
    """Returns a connection to the MySQL database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def add_column_if_not_exists(cur, table, column, definition):
    """Safely adds a column to a table if it doesn't exist already."""
    cur.execute(f"""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_schema = '{DB_NAME}' 
          AND table_name = '{table}' 
          AND column_name = '{column}'
    """)
    if cur.fetchone()[0] == 0:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Migration: Added column '{column}' to table '{table}'")

def initialize_db():
    """Initializes the database schema and performs migrations/seeding if required."""
    # Connect without a database name to verify or create it
    conn = None
    cur = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Connect to the database and create/migrate tables
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Create base users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(30) PRIMARY KEY,
                password VARCHAR(30) NOT NULL
            )
        """)
        
        # 2. Create base patients table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                city VARCHAR(100) NOT NULL
            )
        """)

        # 3. Migrate patients table (Add new columns safely)
        add_column_if_not_exists(cur, 'patients', 'phone', 'VARCHAR(20) NULL')
        add_column_if_not_exists(cur, 'patients', 'email', 'VARCHAR(100) NULL')
        add_column_if_not_exists(cur, 'patients', 'gender', 'VARCHAR(20) NULL')
        add_column_if_not_exists(cur, 'patients', 'blood_group', 'VARCHAR(10) NULL')
        add_column_if_not_exists(cur, 'patients', 'emergency_contact_name', 'VARCHAR(100) NULL')
        add_column_if_not_exists(cur, 'patients', 'emergency_contact_phone', 'VARCHAR(20) NULL')
        
        # 4. Create doctors table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                shift_timings VARCHAR(50)
            )
        """)

        # 5. Create appointments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                doctor_id INT,
                appointment_date DATETIME NOT NULL,
                status VARCHAR(20) DEFAULT 'Scheduled',
                symptoms TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            )
        """)

        # 6. Create medical records table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                diagnosis VARCHAR(255) NOT NULL,
                treatment TEXT,
                prescription TEXT,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        """)

        # 7. Create billing table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                total_amount DECIMAL(10,2) NOT NULL,
                paid_amount DECIMAL(10,2) DEFAULT 0.00,
                payment_status VARCHAR(20) DEFAULT 'Unpaid',
                payment_method VARCHAR(30),
                invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        """)
        
        # 8. Create default admin if not exists
        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO users (username, password) VALUES ('admin', '1234')")
            conn.commit()
            print("Default admin user created.")
            
    except mysql.connector.Error as err:
        print(f"Error creating/migrating tables: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Seed initial test data if database is empty
    seed_data()

def seed_data():
    """Seeds rich sample data for a beautiful initial dashboard visual experience."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Seed Doctors
        cur.execute("SELECT COUNT(*) FROM doctors")
        if cur.fetchone()[0] == 0:
            doctors_data = [
                ("Dr. Sarah Jenkins", "Cardiologist", "+15550198", "sarah.j@hospital.com", "08:00 AM - 04:00 PM"),
                ("Dr. Michael Chang", "Pediatrician", "+15550245", "m.chang@hospital.com", "10:00 AM - 06:00 PM"),
                ("Dr. Emily Ross", "Neurologist", "+15550389", "emily.ross@hospital.com", "09:00 AM - 05:00 PM"),
                ("Dr. James Carter", "General Physician", "+15550412", "j.carter@hospital.com", "12:00 PM - 08:00 PM")
            ]
            cur.executemany(
                "INSERT INTO doctors (name, specialization, phone, email, shift_timings) VALUES (%s, %s, %s, %s, %s)",
                doctors_data
            )
            conn.commit()
            print("Doctors seeded.")

        # Seed Patients
        cur.execute("SELECT COUNT(*) FROM patients")
        patient_count = cur.fetchone()[0]
        # Re-seed if only the basic 'ramu' patient from setup instructions exists
        if patient_count == 0 or (patient_count == 1 and get_patients()[0]['name'] == 'ramu'):
            cur.execute("DELETE FROM patients")  # clear patient table
            patients_data = [
                ("Ramu Prasad", 27, "Chennai", "+919876543210", "ramu.prasad@example.com", "Male", "O+", "Srinivasan Prasad", "+919876543211"),
                ("Jane Doe", 34, "New York", "+15551234", "jane.doe@example.com", "Female", "A-", "John Doe", "+15551235"),
                ("Aarav Mehta", 45, "Mumbai", "+919988776655", "aarav.m@example.com", "Male", "B+", "Pooja Mehta", "+919988776654"),
                ("Sophia Watson", 62, "London", "+447700900077", "sophia.w@example.com", "Female", "AB+", "Thomas Watson", "+447700900078"),
                ("Liam Johnson", 19, "Toronto", "+14165550199", "liam.j@example.com", "Male", "O-", "Robert Johnson", "+14165550198")
            ]
            cur.executemany(
                "INSERT INTO patients (name, age, city, phone, email, gender, blood_group, emergency_contact_name, emergency_contact_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                patients_data
            )
            conn.commit()
            print("Patients seeded.")

        # Get patient and doctor IDs to link them
        cur.execute("SELECT id FROM patients")
        patient_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id FROM doctors")
        doctor_ids = [row[0] for row in cur.fetchall()]

        if patient_ids and doctor_ids:
            # Seed Appointments
            cur.execute("SELECT COUNT(*) FROM appointments")
            if cur.fetchone()[0] == 0:
                import datetime
                now = datetime.datetime.now()
                appointments_data = [
                    (patient_ids[0], doctor_ids[0], now + datetime.timedelta(days=1, hours=2), "Scheduled", "Routine heart checkup"),
                    (patient_ids[1], doctor_ids[1], now + datetime.timedelta(days=2), "Scheduled", "Child health consultation"),
                    (patient_ids[2], doctor_ids[2], now - datetime.timedelta(days=3), "Completed", "Persistent headaches"),
                    (patient_ids[3], doctor_ids[3], now - datetime.timedelta(days=5), "Completed", "General body ache and fatigue"),
                    (patient_ids[4], doctor_ids[0], now + datetime.timedelta(days=4, hours=1), "Scheduled", "ECG follow-up")
                ]
                cur.executemany(
                    "INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, symptoms) VALUES (%s, %s, %s, %s, %s)",
                    appointments_data
                )
                conn.commit()
                print("Appointments seeded.")

            # Seed Medical Records
            cur.execute("SELECT COUNT(*) FROM medical_records")
            if cur.fetchone()[0] == 0:
                records_data = [
                    (patient_ids[2], "Chronic Migraine", "Advised dark room rest and proper sleep cycle.", "Sumatriptan 50mg, Naproxen 500mg"),
                    (patient_ids[3], "Mild Hypertension", "Recommended low sodium diet and daily 30-min walk.", "Amlodipine 5mg once daily"),
                    (patient_ids[0], "Cardiomegaly follow-up", "Echocardiogram shows stable heart size. No immediate intervention.", "Metoprolol 25mg daily")
                ]
                cur.executemany(
                    "INSERT INTO medical_records (patient_id, diagnosis, treatment, prescription) VALUES (%s, %s, %s, %s)",
                    records_data
                )
                conn.commit()
                print("Medical records seeded.")

            # Seed Billing
            cur.execute("SELECT COUNT(*) FROM billing")
            if cur.fetchone()[0] == 0:
                billing_data = [
                    (patient_ids[0], 1200.00, 1200.00, "Paid", "Card"),
                    (patient_ids[1], 450.00, 0.00, "Unpaid", None),
                    (patient_ids[2], 2500.00, 1000.00, "Partially Paid", "Cash"),
                    (patient_ids[3], 350.00, 350.00, "Paid", "Cash"),
                    (patient_ids[4], 5000.00, 0.00, "Unpaid", "Insurance")
                ]
                cur.executemany(
                    "INSERT INTO billing (patient_id, total_amount, paid_amount, payment_status, payment_method) VALUES (%s, %s, %s, %s, %s)",
                    billing_data
                )
                conn.commit()
                print("Billing records seeded.")
    except mysql.connector.Error as err:
        print(f"Error seeding initial data: {err}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def authenticate_user(username, password):
    """Checks if the user exists with matching password."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cur.fetchone()
        return result is not None
    except mysql.connector.Error as err:
        print(f"Database error during authentication: {err}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# --- PATIENT CRUD ---

def get_patients(search_query=None):
    """Fetches list of patients, optionally filtered by search text."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        if search_query:
            query = """
                SELECT * FROM patients 
                WHERE name LIKE %s OR city LIKE %s OR phone LIKE %s OR email LIKE %s OR blood_group LIKE %s
                ORDER BY id DESC
            """
            like_pattern = f"%{search_query}%"
            cur.execute(query, (like_pattern, like_pattern, like_pattern, like_pattern, like_pattern))
        else:
            cur.execute("SELECT * FROM patients ORDER BY id DESC")
        return cur.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error fetching patients: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_patient(name, age, city, phone=None, email=None, gender=None, blood_group=None, ec_name=None, ec_phone=None):
    """Inserts a new patient with optional demographical data."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO patients 
            (name, age, city, phone, email, gender, blood_group, emergency_contact_name, emergency_contact_phone) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, int(age), city, phone, email, gender, blood_group, ec_name, ec_phone)
        )
        conn.commit()
        return cur.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error adding patient: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_patient(patient_id, name, age, city, phone=None, email=None, gender=None, blood_group=None, ec_name=None, ec_phone=None):
    """Updates patient demographics in the database."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE patients 
            SET name=%s, age=%s, city=%s, phone=%s, email=%s, gender=%s, 
                blood_group=%s, emergency_contact_name=%s, emergency_contact_phone=%s 
            WHERE id=%s
            """,
            (name, int(age), city, phone, email, gender, blood_group, ec_name, ec_phone, int(patient_id))
        )
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error updating patient: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_patient(patient_id):
    """Deletes a patient record from database (cascades deletion to appointments/bills/records)."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM patients WHERE id=%s", (int(patient_id),))
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error deleting patient: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# --- DOCTOR CRUD ---

def get_doctors(search_query=None):
    """Retrieves list of doctors."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        if search_query:
            query = "SELECT * FROM doctors WHERE name LIKE %s OR specialization LIKE %s ORDER BY id DESC"
            like_pattern = f"%{search_query}%"
            cur.execute(query, (like_pattern, like_pattern))
        else:
            cur.execute("SELECT * FROM doctors ORDER BY id DESC")
        return cur.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error fetching doctors: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_doctor(name, specialization, phone=None, email=None, shift_timings=None):
    """Adds a new doctor to the registry."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO doctors (name, specialization, phone, email, shift_timings) VALUES (%s, %s, %s, %s, %s)",
            (name, specialization, phone, email, shift_timings)
        )
        conn.commit()
        return cur.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error adding doctor: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_doctor(doctor_id, name, specialization, phone=None, email=None, shift_timings=None):
    """Modifies doctor parameters."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE doctors SET name=%s, specialization=%s, phone=%s, email=%s, shift_timings=%s WHERE id=%s",
            (name, specialization, phone, email, shift_timings, int(doctor_id))
        )
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error updating doctor: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_doctor(doctor_id):
    """Removes a doctor from the system."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM doctors WHERE id=%s", (int(doctor_id),))
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error deleting doctor: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# --- APPOINTMENTS CRUD ---

def get_appointments(search_query=None):
    """Retrieves all scheduled/completed appointments with joint details."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT a.*, p.name AS patient_name, d.name AS doctor_name, d.specialization AS doctor_specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        """
        if search_query:
            query += " WHERE p.name LIKE %s OR d.name LIKE %s OR a.status LIKE %s"
            like_pattern = f"%{search_query}%"
            query += " ORDER BY a.appointment_date DESC"
            cur.execute(query, (like_pattern, like_pattern, like_pattern))
        else:
            query += " ORDER BY a.appointment_date DESC"
            cur.execute(query)
        return cur.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error fetching appointments: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_appointment(patient_id, doctor_id, appointment_date, status="Scheduled", symptoms=None):
    """Schedules a new appointment."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, symptoms) VALUES (%s, %s, %s, %s, %s)",
            (int(patient_id), int(doctor_id), appointment_date, status, symptoms)
        )
        conn.commit()
        return cur.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error scheduling appointment: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_appointment(appointment_id, patient_id, doctor_id, appointment_date, status, symptoms=None):
    """Updates an appointment record."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE appointments 
            SET patient_id=%s, doctor_id=%s, appointment_date=%s, status=%s, symptoms=%s 
            WHERE id=%s
            """,
            (int(patient_id), int(doctor_id), appointment_date, status, symptoms, int(appointment_id))
        )
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error updating appointment: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_appointment(appointment_id):
    """Deletes an appointment scheduler record."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM appointments WHERE id=%s", (int(appointment_id),))
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error deleting appointment: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# --- MEDICAL RECORDS CRUD ---

def get_medical_records(search_query=None):
    """Fetches all diagnosis logs."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT mr.*, p.name AS patient_name 
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.id
        """
        if search_query:
            query += " WHERE p.name LIKE %s OR mr.diagnosis LIKE %s"
            like_pattern = f"%{search_query}%"
            query += " ORDER BY mr.date_recorded DESC"
            cur.execute(query, (like_pattern, like_pattern))
        else:
            query += " ORDER BY mr.date_recorded DESC"
            cur.execute(query)
        return cur.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error fetching medical records: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_medical_record(patient_id, diagnosis, treatment, prescription):
    """Saves a new medical history record."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO medical_records (patient_id, diagnosis, treatment, prescription) VALUES (%s, %s, %s, %s)",
            (int(patient_id), diagnosis, treatment, prescription)
        )
        conn.commit()
        return cur.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error adding medical record: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_medical_record(record_id, patient_id, diagnosis, treatment, prescription):
    """Updates medical history log details."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE medical_records 
            SET patient_id=%s, diagnosis=%s, treatment=%s, prescription=%s 
            WHERE id=%s
            """,
            (int(patient_id), diagnosis, treatment, prescription, int(record_id))
        )
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error updating medical record: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_medical_record(record_id):
    """Removes a medical report from registry."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM medical_records WHERE id=%s", (int(record_id),))
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error deleting medical record: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# --- BILLING CRUD ---

def get_billing_records(search_query=None):
    """Retrieves all hospital invoice logs."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT b.*, p.name AS patient_name 
            FROM billing b
            JOIN patients p ON b.patient_id = p.id
        """
        if search_query:
            query += " WHERE p.name LIKE %s OR b.payment_status LIKE %s OR b.payment_method LIKE %s"
            like_pattern = f"%{search_query}%"
            query += " ORDER BY b.invoice_date DESC"
            cur.execute(query, (like_pattern, like_pattern, like_pattern))
        else:
            query += " ORDER BY b.invoice_date DESC"
            cur.execute(query)
        return cur.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error fetching billing records: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_billing(patient_id, total_amount, paid_amount=0.0, payment_status="Unpaid", payment_method=None):
    """Creates a patient invoice."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO billing (patient_id, total_amount, paid_amount, payment_status, payment_method) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (int(patient_id), float(total_amount), float(paid_amount), payment_status, payment_method)
        )
        conn.commit()
        return cur.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error adding billing: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_billing(billing_id, patient_id, total_amount, paid_amount, payment_status, payment_method=None):
    """Updates values of a patient invoice."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE billing 
            SET patient_id=%s, total_amount=%s, paid_amount=%s, payment_status=%s, payment_method=%s 
            WHERE id=%s
            """,
            (int(patient_id), float(total_amount), float(paid_amount), payment_status, payment_method, int(billing_id))
        )
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error updating billing: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_billing(billing_id):
    """Deletes an invoice statement."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM billing WHERE id=%s", (int(billing_id),))
        conn.commit()
        return cur.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Database error deleting billing record: {err}")
        raise err
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Auto-initialize database on load
try:
    initialize_db()
except Exception as e:
    print(f"Warning: Auto-initialization failed: {e}. Make sure MySQL is running.")
