# 🏥 Hospital Management System (HMS)

An elegant and premium Hospital Management System built with Python, MySQL, and styled with high-fidelity aesthetics. The project provides two user interface options:
1. 🖥️ **Desktop Version**: A modern desktop application built using Tkinter and `ttk` widgets.
2. 🌐 **Web Version**: A high-fidelity, responsive, slate-dark dashboard built using Flask, vanilla CSS, and JavaScript.

Both applications share a centralized database operations layer in `db.py`, ensuring data consistency and cleaner codebase.

---

## ✨ Features

- **🔐 Secure Admin Login**: Session-based credentials for authorized system management (default credentials: `admin` / `1234`).
- **📋 Centralized Patients Table**: A clean and readable tabular display showing all patient database details (ID, Name, Age, City).
- **🔎 Real-time Search / Filtering**: Dynamically filter patients list by Name or City.
- **🛠️ Full CRUD Operations**: Seamlessly Add, Edit, or Delete patient records with immediate layout updates.
- **📊 Metric Cards (Web)**: Interactive overview of hospital statistics (Total Patients count, Average Patient Age, and Active Cities count).
- **⚙️ Auto-Initialization**: Automatically creates the MySQL database `hospital`, sets up required tables (`users`, `patients`), and creates a default admin user on the first run.

---

## 🛠️ Tech Stack

- **Core Logic**: Python 3
- **Database**: MySQL Server
- **Desktop UI**: Tkinter (with `ttk` themes)
- **Web UI**: Flask (Backend), HTML5, CSS3 (Slate Glassmorphism), Vanilla JavaScript (Frontend)

---

## 📂 Project Structure

```
hospital-management-system/
├── app.py               # Tkinter Desktop Entry point
├── web_app.py           # Flask Web Server Entry point
├── db.py                # Database queries and utility functions
├── .env.example         # Configuration template for MySQL connection
├── templates/
│   ├── login.html       # Web login screen template
│   └── dashboard.html   # Web dashboard CRUD template
└── static/
    └── css/
        └── style.css    # Premium CSS design stylesheet
```

---

## ⚙️ Setup and Installation

### 1. Prerequisites
- **Python 3.8+** installed.
- **MySQL Server** installed and running on `localhost`.

### 2. Automated Installation (Recommended)
We have provided a setup script that creates a clean virtual environment and configures the template environment file:
```bash
# Make the installer executable (if needed)
chmod +x install.sh

# Run the installer
./install.sh
```

### 3. Database Credentials Configuration
Open the newly created `.env` file in a text editor and update it with your MySQL credentials:
```ini
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=hospital
```
*Note: You do not need to manually create the database or tables. The system will auto-initialize everything on the first startup.*

---

## 🚀 How to Run

Before running the application, make sure to activate the virtual environment:
```bash
source venv/bin/activate
```

### Option A: Modern Desktop Application (Tkinter)
Launch the desktop interface by executing:
```bash
python3 app.py
```
- **Login Credentials**: Username `admin`, Password `1234`.
- Double-click any row in the patient list to edit its details.

### Option B: High-Fidelity Web Dashboard (Flask)
Launch the local web server:
```bash
python3 web_app.py
```
Then open your web browser and navigate to:
```
http://127.0.0.1:5000
```
- **Login Credentials**: Username `admin`, Password `1234`.
- Log in, manage patient databases, filter records, or add/delete entries with interactive popups.
