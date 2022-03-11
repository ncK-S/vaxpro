from werkzeug.utils import redirect
from app import app
from app import db
from app.models import Employer, Employee, Vaccine_Dose
from flask import json, render_template, request, session, url_for, jsonify, flash

# API = db.Model

@app.route('/')
def index():
    if 'employer' in session.keys():
        return redirect(url_for('employees'))
    else:
        return render_template('main.html')

@app.route('/register-employer', methods=['POST'])
def register_employer():
    form = request.form
    employer = Employer(
        name=form['name'],
        email=form['email-address'],
        phone_number=form['phone-number'])
    Employer.set_password(form['password'])
    db.session.add(employer)
    db.session.commit()
    return render_template('employees.html')

@app.route('/validate-employer', methods=['POST'])
def validate_employer():
    if request.method == "POST":
        email_address = request.get_json()['email']
        employer = Employer.query.filter_by(email=email_address).first()
        if employer:
            return jsonify({'user_exists': 'true'})
        else:
            return jsonify({'user_exists': 'false'})

@app.route('/validate-password', methods=['POST'])
def validate_password():
    if request.method == "POST":
        email_address = request.get_json()['email']
        password = request.get_json()['password']
        userFound = 'false'
        passwordCorrect = 'false'
        employer = Employer.query.filter_by(email=email_address).first()
        if employer:
            userFound = 'true'
            if employer.check_password(password):
                passwordCorrect = 'true'
        
        return jsonify({'user_exists': userFound, 'passwordCorrect': passwordCorrect})
        
@app.route('/login-employer', methods=['POST'])
def login_employer():
    form = request.form
    employer = Employer.query.filter_by(email=form['email-address']).first()

    if employer and employer.check_password(form['password']):
        return redirect(url_for('patients'))
    else:
        flash("Password was incorrect or user doesn't exist.")
        return redirect(url_for('employees.html'))

@app.route('/logout-employer', methods=['POST', 'GET'])
def logout_employer():
    session.pop('employer', None)
    return redirect(url_for('main.html'))


@app.route('/employee', methods=['POST', 'GET'])
def employee():
    employer = None
    if session['employer']:
        employer = session['employer']
        employee = Employee.query.filter_by(employer_id=employer)
        return render_template('employees.html', employee=employee)
    return render_template('employees.html')

@app.route('/register-employee', methods=['POST', 'GET'])
def register_employee():
    form = request.form
    email = form['email-address']
    employee = Employee.query.filter_by(email=email).first()
    if not employee:
        employee = Employee(
            name=form['name'],
            id=form['employee_id'],
            email=form['email'],
            phone_number=form['phone-number'],
            doctor_id=session['employee'])
        db.session.add(employee)
        db.session.commit()
        flash('Employee successfully registered')
        return redirect(url_for('employees'))
    else:
        flash('Employee already exists')
        return redirect(url_for('employees'))

@app.route('/vaccine-record/<employee_id>', methods=['GET', 'POST'])
def vaccine_record(employee_id):
    if not employee_id:
        return redirect(url_for('employees'))
    employee = Employee.query.filter_by(id=employee_id).first()
    if employee:
        vaccine_doses = Vaccine_Dose.query.filter_by(employee_id=employee_id)
        return render_template('vaccine_record.html', vaccine_doses=vaccine_doses, patient_id=patient_id)
    return render_template('vaccine_record.html')

@app.route('/add-vaccine-record/<employee_id>', methods=['POST', 'GET'])
def add_vaccine_record(employee_id):
    form = request.form
    dose_id = form['dose-id']
    dose_number = form['dose-number']
    vaccine_dose = Vaccine_Dose.query.filter_by(employee_id=employee_id, dose_no=dose_number).first()
    if vaccine_dose:
        flash('This dose number has already been entered.')
        return redirect(url_for('vaccine_record', employee_id=employee_id))
    vaccine_dose = Vaccine_Dose.query.filter_by(dose_id=dose_id).first()
    if vaccine_dose:
        flash('A dose with this serial number already exists in the database')
        return redirect(url_for('vaccine_record', employee_id=employee_id))
    vaccine_dose = Vaccine_Dose(
        type=form['type'],
        volume=form['volume'],
        dose_no=form['dose-number'],
        dose_id=dose_id,
        employee_id=employee_id
    )
    db.session.add(vaccine_dose)
    db.session.commit()
    flash('Vaccine dose successfully added.')
    return redirect(url_for('vaccine_record', employee_id=employee_id))


    
@app.route('/delete-employee/<employee_id>', methods=['GET'])
def delete_employee(employee_id):
    Employee.query.filter_by(id=employee_id).delete()
    db.session.commit()
    flash('Employee dose successfully deleted.')
    return redirect(url_for('employees', employee_id=employee_id))
