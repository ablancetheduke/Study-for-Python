# app/routes.py
from flask import render_template, request, redirect, url_for
from app import app

@app.route('/', methods=['GET', 'POST'])
def index():
    committee_name = ""
    agenda = ""
    
    if request.method == 'POST':
        committee_name = request.form.get('committee_name')
        agenda = request.form.get('agenda')

    return render_template('index.html', committee_name=committee_name, agenda=agenda)

