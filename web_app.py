from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import db

app = Flask(__name__)
app.secret_key = "hospital_management_secret_key_change_me_in_prod"

# Ensure DB is initialized when Flask starts
try:
    db.initialize_db()
except Exception as e:
    print(f"Warning: Database setup error on startup: {e}")

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Please enter both username and password.", "danger")
        elif db.authenticate_user(username, password):
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    search_query = request.args.get('search', '').strip()
    
    # Fetch lists for dashboard views
    patients = db.get_patients(search_query if search_query else None)
    doctors = db.get_doctors(search_query if search_query else None)
    appointments = db.get_appointments(search_query if search_query else None)
    records = db.get_medical_records(search_query if search_query else None)
    billings = db.get_billing_records(search_query if search_query else None)
    
    # Calculate Finance Stats
    total_billing = 0.0
    total_paid = 0.0
    total_unpaid = 0.0
    
    status_counts = {"Paid": 0, "Unpaid": 0, "Partially Paid": 0}
    status_revenue = {"Paid": 0.0, "Unpaid": 0.0, "Partially Paid": 0.0}
    method_revenue = {}
    
    for b in billings:
        tot = float(b['total_amount'])
        paid = float(b['paid_amount'])
        unpaid = tot - paid
        
        total_billing += tot
        total_paid += paid
        total_unpaid += unpaid
        
        status = b['payment_status']
        if status in status_counts:
            status_counts[status] += 1
            status_revenue[status] += tot
            
        method = b['payment_method'] or "Unassigned"
        method_revenue[method] = method_revenue.get(method, 0.0) + tot

    # Format values for template javascript ingestion
    finance_stats = {
        "total_billing": round(total_billing, 2),
        "total_paid": round(total_paid, 2),
        "total_unpaid": round(total_unpaid, 2),
        "status_counts": status_counts,
        "status_revenue": status_revenue,
        "method_revenue": method_revenue
    }
    
    # Dashboard summary numbers
    counts = {
        "patients": len(db.get_patients()),
        "doctors": len(db.get_doctors()),
        "appointments": len(db.get_appointments()),
        "billing": len(billings)
    }

    return render_template(
        'dashboard.html',
        patients=patients,
        doctors=doctors,
        appointments=appointments,
        records=records,
        billings=billings,
        finance_stats=finance_stats,
        counts=counts,
        search=search_query
    )

# --- PATIENT ACTIONS ---

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    name = request.form.get('name', '').strip()
    age_str = request.form.get('age', '').strip()
    city = request.form.get('city', '').strip()
    phone = request.form.get('phone', '').strip() or None
    email = request.form.get('email', '').strip() or None
    gender = request.form.get('gender', '').strip() or None
    blood_group = request.form.get('blood_group', '').strip() or None
    ec_name = request.form.get('ec_name', '').strip() or None
    ec_phone = request.form.get('ec_phone', '').strip() or None
    
    if not name or not age_str or not city:
        return jsonify({"success": False, "message": "Name, Age, and City are required!"}), 400
        
    try:
        age = int(age_str)
        if age <= 0 or age > 150:
            return jsonify({"success": False, "message": "Age must be between 1 and 150"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Age must be a valid integer"}), 400
        
    try:
        db.add_patient(name, age, city, phone, email, gender, blood_group, ec_name, ec_phone)
        return jsonify({"success": True, "message": "Patient added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/edit_patient/<int:patient_id>', methods=['POST'])
def edit_patient(patient_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    name = request.form.get('name', '').strip()
    age_str = request.form.get('age', '').strip()
    city = request.form.get('city', '').strip()
    phone = request.form.get('phone', '').strip() or None
    email = request.form.get('email', '').strip() or None
    gender = request.form.get('gender', '').strip() or None
    blood_group = request.form.get('blood_group', '').strip() or None
    ec_name = request.form.get('ec_name', '').strip() or None
    ec_phone = request.form.get('ec_phone', '').strip() or None
    
    if not name or not age_str or not city:
        return jsonify({"success": False, "message": "Name, Age, and City are required!"}), 400
        
    try:
        age = int(age_str)
        if age <= 0 or age > 150:
            return jsonify({"success": False, "message": "Age must be between 1 and 150"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Age must be a valid integer"}), 400
        
    try:
        db.update_patient(patient_id, name, age, city, phone, email, gender, blood_group, ec_name, ec_phone)
        return jsonify({"success": True, "message": "Patient updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        success = db.delete_patient(patient_id)
        if success:
            return jsonify({"success": True, "message": "Patient deleted successfully!"})
        else:
            return jsonify({"success": False, "message": "Patient not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# --- DOCTOR ACTIONS ---

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    name = request.form.get('name', '').strip()
    specialization = request.form.get('specialization', '').strip()
    phone = request.form.get('phone', '').strip() or None
    email = request.form.get('email', '').strip() or None
    shift_timings = request.form.get('shift_timings', '').strip() or None
    
    if not name or not specialization:
        return jsonify({"success": False, "message": "Name and Specialization are required!"}), 400
        
    try:
        db.add_doctor(name, specialization, phone, email, shift_timings)
        return jsonify({"success": True, "message": "Doctor added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/edit_doctor/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    name = request.form.get('name', '').strip()
    specialization = request.form.get('specialization', '').strip()
    phone = request.form.get('phone', '').strip() or None
    email = request.form.get('email', '').strip() or None
    shift_timings = request.form.get('shift_timings', '').strip() or None
    
    if not name or not specialization:
        return jsonify({"success": False, "message": "Name and Specialization are required!"}), 400
        
    try:
        db.update_doctor(doctor_id, name, specialization, phone, email, shift_timings)
        return jsonify({"success": True, "message": "Doctor updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        success = db.delete_doctor(doctor_id)
        if success:
            return jsonify({"success": True, "message": "Doctor deleted successfully!"})
        else:
            return jsonify({"success": False, "message": "Doctor not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# --- APPOINTMENT ACTIONS ---

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    doctor_id = request.form.get('doctor_id', '').strip()
    date_str = request.form.get('appointment_date', '').strip()
    status = request.form.get('status', 'Scheduled').strip()
    symptoms = request.form.get('symptoms', '').strip() or None
    
    if not patient_id or not doctor_id or not date_str:
        return jsonify({"success": False, "message": "Patient, Doctor, and Date are required!"}), 400
        
    # Standard HTML datetime-local format: YYYY-MM-DDTHH:MM
    date_str = date_str.replace('T', ' ')
    
    try:
        db.add_appointment(patient_id, doctor_id, date_str, status, symptoms)
        return jsonify({"success": True, "message": "Appointment scheduled successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/edit_appointment/<int:appointment_id>', methods=['POST'])
def edit_appointment(appointment_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    doctor_id = request.form.get('doctor_id', '').strip()
    date_str = request.form.get('appointment_date', '').strip()
    status = request.form.get('status', 'Scheduled').strip()
    symptoms = request.form.get('symptoms', '').strip() or None
    
    if not patient_id or not doctor_id or not date_str:
        return jsonify({"success": False, "message": "Patient, Doctor, and Date are required!"}), 400
        
    date_str = date_str.replace('T', ' ')
    
    try:
        db.update_appointment(appointment_id, patient_id, doctor_id, date_str, status, symptoms)
        return jsonify({"success": True, "message": "Appointment updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        success = db.delete_appointment(appointment_id)
        if success:
            return jsonify({"success": True, "message": "Appointment deleted successfully!"})
        else:
            return jsonify({"success": False, "message": "Appointment not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# --- MEDICAL RECORD ACTIONS ---

@app.route('/add_record', methods=['POST'])
def add_record():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    diagnosis = request.form.get('diagnosis', '').strip()
    treatment = request.form.get('treatment', '').strip() or None
    prescription = request.form.get('prescription', '').strip() or None
    
    if not patient_id or not diagnosis:
        return jsonify({"success": False, "message": "Patient and Diagnosis are required!"}), 400
        
    try:
        db.add_medical_record(patient_id, diagnosis, treatment, prescription)
        return jsonify({"success": True, "message": "Medical record added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/edit_record/<int:record_id>', methods=['POST'])
def edit_record(record_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    diagnosis = request.form.get('diagnosis', '').strip()
    treatment = request.form.get('treatment', '').strip() or None
    prescription = request.form.get('prescription', '').strip() or None
    
    if not patient_id or not diagnosis:
        return jsonify({"success": False, "message": "Patient and Diagnosis are required!"}), 400
        
    try:
        db.update_medical_record(record_id, patient_id, diagnosis, treatment, prescription)
        return jsonify({"success": True, "message": "Medical record updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        success = db.delete_medical_record(record_id)
        if success:
            return jsonify({"success": True, "message": "Medical record deleted successfully!"})
        else:
            return jsonify({"success": False, "message": "Record not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# --- BILLING ACTIONS ---

@app.route('/add_billing', methods=['POST'])
def add_billing():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    total_str = request.form.get('total_amount', '').strip()
    paid_str = request.form.get('paid_amount', '0.0').strip()
    status = request.form.get('payment_status', 'Unpaid').strip()
    method = request.form.get('payment_method', '').strip() or None
    
    if not patient_id or not total_str:
        return jsonify({"success": False, "message": "Patient and Total Amount are required!"}), 400
        
    try:
        total = float(total_str)
        paid = float(paid_str)
        if total < 0 or paid < 0:
            return jsonify({"success": False, "message": "Amounts cannot be negative!"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Amounts must be valid decimals"}), 400
        
    try:
        db.add_billing(patient_id, total, paid, status, method)
        return jsonify({"success": True, "message": "Invoice created successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/edit_billing/<int:billing_id>', methods=['POST'])
def edit_billing(billing_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    patient_id = request.form.get('patient_id', '').strip()
    total_str = request.form.get('total_amount', '').strip()
    paid_str = request.form.get('paid_amount', '').strip()
    status = request.form.get('payment_status', 'Unpaid').strip()
    method = request.form.get('payment_method', '').strip() or None
    
    if not patient_id or not total_str or not paid_str:
        return jsonify({"success": False, "message": "Patient, Total, and Paid amount are required!"}), 400
        
    try:
        total = float(total_str)
        paid = float(paid_str)
        if total < 0 or paid < 0:
            return jsonify({"success": False, "message": "Amounts cannot be negative!"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Amounts must be valid decimals"}), 400
        
    try:
        db.update_billing(billing_id, patient_id, total, paid, status, method)
        return jsonify({"success": True, "message": "Invoice updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/delete_billing/<int:billing_id>', methods=['POST'])
def delete_billing(billing_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        success = db.delete_billing(billing_id)
        if success:
            return jsonify({"success": True, "message": "Invoice deleted successfully!"})
        else:
            return jsonify({"success": False, "message": "Invoice not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
