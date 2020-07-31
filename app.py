from __future__ import division
from flask import Flask
import os
from flask import render_template, url_for
from flask import request
from cloudant import Cloudant
from datetime import datetime
import atexit
import os
import json

app = Flask(__name__)

client = None

db_name = 'usage_db'
#if 'VCAP_SERVICES' in os.environ:
#    vcap = json.loads(os.getenv('VCAP_SERVICES'))
#    if 'cloud-object-storage' in vcap:
#        print("Found cloud-object-storage in  vcap")
#    else:
#        print("Not cloud-object-storage in  vcap")

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        get_username = creds['username']
        get_apikey = creds['apikey']
        #url = 'https://' + creds['host']
        #client = Cloudant(user, password, url=url, connect=True)
        client = Cloudant.iam(get_username, get_apikey)
        client.connect()
        #db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    client.connect()
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloud-object-storage-vm'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        client.connect()

# db_exists=''
#database_name = 'usage_db'
# my_db = ''

# Creating new database if doesn't exist
#if client:
#    if database_name.exists():
#       db_exists='Y'
#    else:
#        db_exists='N'
#    if (db_exists=='N'):

my_db = client.create_database(db_name, throw_on_exists=False)

# json_document = None

# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

#port = int(os.getenv("PORT"))

def  calculate_fourwheeler(fourwheeler_runkm, fourwheeler_runtime, number_of_persons):
    emission_rate = 120.1
    calculated_emission_per_person = fourwheeler_runtime * number_of_persons
    total_emission_fourwheeler = fourwheeler_runkm * emission_rate
    calculated_emission_four_wheeler = total_emission_fourwheeler / calculated_emission_per_person
    return calculated_emission_four_wheeler

def calculate_twowheeler(twowheeler_runkm, twowheeler_runtime, number_of_persons):
    emission_rate = 0.50
    calculated_emission_per_person = twowheeler_runtime * number_of_persons
    total_emission_twowheeler = twowheeler_runkm * emission_rate
    calculated_emission_two_wheeler = total_emission_twowheeler / calculated_emission_per_person
    return calculated_emission_two_wheeler

def calculate_refrigerator(refrigerator_runtime, house_population):
    emission_rate = 85.9
    calculated_emission_per_person = refrigerator_runtime / house_population
    calculated_emission_refrigerator = calculated_emission_per_person * emission_rate
    return calculated_emission_refrigerator

def calculate_lpg(lpg_runtime, house_population):
    emission_rate = 169.5
    calculated_emission_per_person = lpg_runtime / house_population
    calculated_emission_lpg = calculated_emission_per_person * emission_rate
    return calculated_emission_lpg

def calculate_ac(ac_runtime, house_population):
    emission_rate = 117.17
    calculated_emission_per_person = ac_runtime / house_population
    calculated_emission_ac = calculated_emission_per_person * emission_rate
    return calculated_emission_ac

def calculate_entertainment_unit(entertainment_unit_runtime, house_population):
    emission_rate = 110
    calculated_emission_per_person = entertainment_unit_runtime / house_population
    calculated_emission_entertainment_unit = calculated_emission_per_person * emission_rate
    return calculated_emission_entertainment_unit


@app.route('/')
def home():
    return render_template('carbonfootprint.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    number_of_persons = request.form['persons']
    email = request.form['email']
    name = request.form['name']
    fourwheeler_runkm = float(request.form['run_fourwheeler'])
    fourwheeler_runtime = float(request.form['runtime_fourwheeler'])
    twowheeler_runkm = float(request.form['run_twowheeler'])
    twowheeler_runtime = float(request.form['runtime_twowheeler'])
    house_population = request.form['people']
    refrigerator_runtime = float(request.form['runtime_refrigerator'])
    lpg_runtime = float(request.form['runtime_lpg'])
    ac_runtime = float(request.form['runtime_ac'])
    entertainment_unit_runtime = float(request.form['runtime_entertainmentunit'])


    int_number_of_persons = float(number_of_persons)
    int_fourwheeler_runkm = float(fourwheeler_runkm)
    int_fourwheeler_runtime = float(fourwheeler_runtime)
    int_twowheeler_runkm = float(twowheeler_runkm)
    int_twowheeler_runtime = float(twowheeler_runtime)
    int_house_population = float(house_population)
    int_refrigerator_runtime = float(refrigerator_runtime)
    int_lpg_runtime = float(lpg_runtime)
    int_ac_runtime = float(ac_runtime)
    int_entertainment_unit_runtime = float(entertainment_unit_runtime)

    if int_fourwheeler_runtime != 0 :
        calculated_emission_four_wheeler = calculate_fourwheeler(int_fourwheeler_runkm, int_fourwheeler_runtime, int_number_of_persons)
    else:
        calculated_emission_four_wheeler = 0

    if int_twowheeler_runtime != 0:
        calculated_emission_two_wheeler = calculate_twowheeler(int_twowheeler_runkm, int_twowheeler_runtime, int_number_of_persons)
    else:
        calculated_emission_two_wheeler = 0

    calculated_emission_refrigerator = calculate_refrigerator(int_refrigerator_runtime, int_house_population)
    calculated_emission_lpg = calculate_lpg(int_lpg_runtime, int_house_population)
    calculated_emission_ac = calculate_ac(int_ac_runtime, int_house_population)
    calculated_emission_entertainment_unit = calculate_entertainment_unit(int_entertainment_unit_runtime, int_house_population)


    calculated_emission = calculated_emission_four_wheeler + calculated_emission_two_wheeler + calculated_emission_refrigerator + calculated_emission_lpg + calculated_emission_ac + calculated_emission_entertainment_unit

    json_document = {
        "Name": name,
        "Email": email,
        "number_of_persons": int_number_of_persons,
        "fourwheeler_runkm": int_fourwheeler_runkm,
        "fourwheeler_runtime": int_fourwheeler_runtime,
        "twowheeler_runkm": int_twowheeler_runkm,
        "twowheeler_runtime": int_twowheeler_runtime,
        "house_population": int_house_population,
        "refrigerator_runtime": int_refrigerator_runtime,
        "lpg_runtime": int_lpg_runtime,
        "ac_runtime": int_ac_runtime,
        "entertainment_unit_runtime": int_entertainment_unit_runtime,
        "Entered_TS": dt_string,
        "CO2_QTY": calculated_emission
    }

    new_document = my_db.create_document(json_document)
    print("documnet added to database")

    #msg = '';
    #if calculated_emission < 228.31:
    #    msg = "Hello" + ' ' + name + ' ' + ", your Carbon emission for today is " + ' ' + str(calculated_emission) + ' ' + "Gram." + ' ' + "Incredible, You are doing great!!"
    #else:
    #    msg = "Hello" + ' ' + name + ' ' + ", your Carbon emission for today is " + ' ' + str(calculated_emission) + ' ' + "Gram." + ' ' + "You have exceeded your daily limit , kindly limit your usage."
    #
    #return render_template('carbonfootprint.html', msg=msg)
    #

    return render_template('carbonfootprint.html', name=name, calculated_emission=calculated_emission )
    
port = int(os.getenv('PORT', 8000))

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=port, debug=True)
