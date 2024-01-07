from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import ForeignKey
import os
import datetime as dt


app = Flask(__name__)
app.secret_key = os.urandom(12)

db_path = os.path.join(os.path.dirname(__file__), 'insurance_co.db')  # Location of our database (same folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path  # SQLAlchemy will be using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Policyholders(db.Model):
    """
    Database class/object.

    represents Policyholders table in insurance_co.db.

    Attributes / Columns
    --------------------
    c_id = Primary key, Integer, Autoincrement
    pin = Personal Identification Number, Integer, Unique
    name = Text
    surname = Text
    birthdate = Date
    none are nullable
    """
    c_id = db.Column(db.Integer,  primary_key=True, nullable=False, autoincrement=True)
    pin = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)

    def __init__(self, pin, name, surname, birthdate):
        self.pin = pin
        self.name = name
        self.surname = surname
        self.birthdate = birthdate


class Contracts(db.Model):
    """
    Database class/object.

    represents Contracts table in insurance_co.db.
    Is subservient table to Policyholders in 1:n relationship.

    Attributes / Columns
    --------------------
    contract_id = Primary Key ,Integer, Autoincrement
    customer = Foreign key == pin column in Policyholders table
    contract_number = Integer, Unique
    insurance_type = Text
    premium = Integer
    """
    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    customer = db.Column(ForeignKey(Policyholders.pin), nullable=False)
    contract_number = db.Column(db.Integer, unique=True, nullable=False)
    insurance_type = db.Column(db.String(100), nullable=False)
    premium = db.Column(db.Integer, nullable=False)

    def __init__(self, customer, contract_number, insurance_type, premium):
        self.customer = customer
        self.contract_number = contract_number
        self.insurance_type = insurance_type
        self.premium = premium


@app.route('/')
def index():
    """
    Renders index.html and manages searching for entries in Policyholders table.
    Matches searched term with pin, surname and name columns.

    Returns
    -------
    Renders index.html including all OR searched for Policyholders entries.
    """
    q = request.args.get("q")
    if q:
        results = Policyholders.query.filter(Policyholders.name.icontains(q)
                                             | Policyholders.surname.icontains(q)
                                             | Policyholders.pin.icontains(q))
    else:
        results = Policyholders.query.all()
    return render_template("index.html", show=results)


@app.route('/insert', methods=['POST'])
def insert():
    """
    Inserts data into Policyholders table.

    Returns
    -------
        redirects to 'index'
    """
    if request.method == 'POST':
        pin = request.form['pin']
        name = request.form['name']
        surname = request.form['surname']
        birthdate = request.form['birthdate']

        my_data = Policyholders(pin, name, surname, parse_date(birthdate))
        db.session.add(my_data)
        try:
            db.session.commit()
            flash("Customer inserted successfully.")
        except IntegrityError:
            db.session.rollback()
            flash("Personal identification number already exists!")
        return redirect(url_for('index'))


def parse_date(date):
    """
    Parses HTML date type input into Python/SQLite date type.

    Parameter
    ---------
    date
        String representing date in Y-m-d format

    Returns
    -------
    Date type
    """
    return dt.datetime.strptime(date, '%Y-%m-%d').date()


@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    Edits existing entry in Policyholders table.

    Returns
    -------
    redirects to 'index'
    """
    if request.method == 'POST':
        my_data = Policyholders.query.get(request.form.get('c_id'))
        my_data.pin = request.form['pin']
        my_data.name = request.form['name']
        my_data.surname = request.form['surname']
        my_data.birthdate = parse_date(request.form['birthdate'])
        try:
            db.session.commit()
            flash("Customer updated successfully.")
        except IntegrityError:
            db.session.rollback()
            flash("Personal identification number already exists!")
        return redirect(url_for('index'))


@app.route('/delete/<c_id>/', methods=['GET', 'POST'])
def delete(c_id):
    """
    Deletes entry from Policyholders and all subservient Contracts entries.

    Parameter
    ---------
    c_id
        Determines which Policyholder and Contracts entries will be removed.

    Returns
    -------
    redirects to 'index'
    """
    contracts = Contracts.query.filter(Contracts.customer == Policyholders.query.get(c_id).pin)
    contracts.delete()

    my_data = Policyholders.query.get(c_id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Entry has been removed!")
    return redirect(url_for('index'))


@app.route('/detail/<pin>', methods=['GET'])
def detail(pin):
    """
    Renders "customer detail information" = Data from 1 Policyholders entry and their subservient Contracts entries
    if any exist.

    Parameter
    ---------
    pin
        Unique identification determining which Policyholders entry will be rendered.

    Returns
    -------
    Renders detail.html containing selected Policyholders and Contracts data.
    """
    customer = Policyholders.query.filter(Policyholders.pin == pin).first()
    contracts = Contracts.query.filter(Contracts.customer == pin).all()
    return render_template('detail.html', customer=customer, contract=contracts)


@app.route('/contract_insert', methods=['POST', 'GET'])
def contract_insert():
    """
    Inserts entry to Contracts table.

    Returns
    -------
    redirects to 'detail'
    """
    if request.method == 'POST':
        customer = request.form.get('customer')
        number = request.form['c_num']
        c_type = request.form['c_type']
        premium = request.form['c_premium']
        my_data = Contracts(customer, number, c_type, premium)
        db.session.add(my_data)
        try:
            db.session.commit()
            flash("Contract inserted successfully!")
        except IntegrityError:
            db.session.rollback()
            flash("Contract number number already exists!")
        return redirect(url_for('detail', pin=customer))


@app.route('/contract_delete/<con_id>/', methods=['GET', 'POST'])
def contract_delete(con_id):
    """
    Removes entry from Contracts table.

    Parameter
    ---------
    con_id
        Primary Key - determines  which entry gets deleted

    Returns
    -------
    redirects to 'detail'
    """

    customer = request.form.get('customer')
    my_data = Contracts.query.get(con_id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Contract has been removed!")
    print(customer)
    return redirect(url_for('detail', pin=customer))


@app.route('/contract_edit', methods=['GET', 'POST'])
def contract_edit():
    """
    Edits entry in Contracts table.

    Returns
    -------
    redirects to 'detail'
    """
    contract = Contracts.query.get(request.form.get('contract'))
    contract.contract_number = request.form['c_num']
    contract.insurance_type = request.form['c_type']
    contract.premium = request.form['c_premium']
    try:
        db.session.commit()
        flash("Contract updated successfully!")
    except IntegrityError:
        db.session.rollback()
        flash("Contract number number already exists!")
    customer = request.form.get('customer')
    return redirect(url_for('detail', pin=customer))


if __name__ == "__main__":
    app.run()

