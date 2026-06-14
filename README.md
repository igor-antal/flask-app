# 🌐 CRUD webová aplikace
**Webová aplikace pro správu klientů a jejich smluv.**  

🚀 Živá ukázka projektu https://igorantal.pythonanywhere.com/ 

Umožňuje:
- Vytvářet nové zázamy klientů.
- Vytvářet záznamy smluv u konkrétního klienta.
- Upravovat záznamy.
- Mazat záznamy

## Technologie
**Backend**:
- Logika: Python - Flask
- Databáze: SQLite za použití ORM SQLAlchemy
- Šablonovací systém HTML: Jinja2

**Frontend**:
- HTML, JS bootstrap
- FE je statický, HTML se mění pouze na straně serveru.

### Lokální instalace
**1. klonování repozitáře:**  
Bash:  
"git clone https://github.com/igor-antal/flask-app.git"  
"cd flask-app"

**2. vytvoření a aktivace virtuálního prostředí**  
Bash:  
"python -m venv venv"  
"venv\Scripts\activate"

**3. instalace knihoven**  
Bash:  
"pip install -r requirements.txt"

**4. spuštění**  
Bash:  
"flask run"
Aplikace bude dostupná v prohlížeči na adrese http://127.0.0.1:5000/
