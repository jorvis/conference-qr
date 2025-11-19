# 🧭 ConferenceQR (Jinja2 Version) — Setup Instructions

This document explains how to install, configure, and run the Jinja2 version of **ConferenceQR**, a LAMP-based QR scanning and reward tracker for conferences.

---

## 🚀 1. Server Prerequisites

Ensure your system has a working LAMP stack (Linux, Apache, MySQL/MariaDB, Python). Then install the required packages:

```bash
sudo apt-get update
sudo apt-get install -y apache2 mariadb-server python3-pip qrencode
sudo a2enmod cgi rewrite
sudo systemctl reload apache2
```

Install Python dependencies:

```bash
python3 -m pip install jinja2 mysql-connector-python
```

---

## 🗄️ 2. Database Setup

Load the schema and seed data into MySQL:

```bash
sudo mysql < sql/schema.sql
sudo mysql conferenceqr < sql/seed.sql
```

This creates:
- **Database:** `conferenceqr`
- **Tables:** `attendees`, `places`, `scans`
- **Data:** 24 exhibitors (`E01–E24`) and 3 sessions (`S01–S03`)

---

## 🌐 3. Deploy Files to Apache

Copy or symlink the CGI scripts and templates to your Apache web root:

```bash
sudo cp -r cgi-bin /var/www/html/
```

Ensure proper permissions:

```bash
sudo chown -R www-data:www-data /var/www/html/cgi-bin
sudo chmod -R 755 /var/www/html/cgi-bin
```

Enable CGI if not already:

```bash
sudo a2enmod cgi
sudo systemctl reload apache2
```

---

## ⚙️ 4. Configure the App

Edit `/var/www/html/cgi-bin/config.py`:

```python
DB_CONFIG = {
    "user": "confqr",
    "password": "YOUR_DB_PASSWORD",
    "host": "localhost",
    "database": "conferenceqr"
}
BASE_URL = "https://your-domain.example"
CONFERENCE_NAME = "My Awesome Conference 2025"
ADMIN_KEY = "choose_a_secret_key"
```

Don't forget to also actually create this user!

```mysql
CREATE USER confqr@localhost IDENTIFIED BY 'YOUR_DB_PASSWORD';

GRANT SELECT, INSERT, UPDATE, DELETE ON conferenceqr.* to confqr@localhost;
```

---

## 🧾 5. Generate QR Codes

From the `qr` directory:

```bash
cd qr
BASE_URL="https://your-domain.example" ./generate_qr.sh
```

This generates PNG files like:

```
E01.png  E02.png  ...  E24.png  S01.png  S02.png  S03.png
```

Each links to:
- `/cgi-bin/scan.py?code=E01`
- `/cgi-bin/scan.py?code=S01`
etc.

---

## 🔍 6. Test the Application

Open these in your browser:

- **Attendee scan:** `https://your-domain.example/cgi-bin/scan.py?code=E01`
- **Progress page:** `https://your-domain.example/cgi-bin/progress.py`
- **Admin dashboard:** `https://your-domain.example/cgi-bin/admin.py?key=YOUR_ADMIN_KEY`

---

## 🧱 Optional Apache Configuration Snippet

If your server does not yet serve `/cgi-bin` paths, add this to your Apache config:

```apache
ScriptAlias /cgi-bin/ /var/www/html/cgi-bin/
<Directory "/var/www/html/cgi-bin">
    Options +ExecCGI
    AddHandler cgi-script .py
    Require all granted
</Directory>
```

Then reload Apache:

```bash
sudo systemctl reload apache2
```

---

Happy scanning! 🎉
