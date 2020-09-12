import csv
import datetime
import random

maleFirstNames = { 'n': [], 'i': 0 }
femaleFirstNames = { 'n': [], 'i': 0 }
lastNames = { 'n': [], 'i': 0 }

def getName(names):
    i = names['i']
    name = names['n'][i]
    i += 1
    if i >= len(names['n']): i = 0
    names['i'] = i
    return name

def getBirthDate(age):
    today = datetime.date.today()
    year = str(today.year-int(age))
    month = str(random.randint(1,today.month))
    if len(month) < 2: month = '0'+month
    day = str(random.randint(1,today.day))
    if len(day) < 2: day = '0'+day
    return year + '-' + month + '-' + day

def createHeader(fout):
    # Demographic
    line = 'First Name,Last Name,Gender,Birth Date'
    # Comorbidity
    for name in ['ASA Score','Ischemic Heart Disease','Cardiac Failure','Renal Failure','Liver','Any Malignancy']: line += ','+name
    # Medications
    for name in ['Aspirin','Adenosine Diphosphate Inhibitors','Anticoagulation','NSAIDs']: line += ','+name
    # Clinical Features at Presentation
    for name in ['Pulse', 'Systolic Blood Pressure']: line += ','+name
    for name in ['Syncope','Altered Mental Status','Hematemesis','Melena','Hematochezia']: line += ','+name
    # Initial Laboratory Values
    for name in ['Hemoglobin','Urea','Creatinine','Albumin','INR']: line += ','+name
    fout.write(line+'\n')
    
"""
OrderedDict([('', '0'), ('id', '0'), ('site', '0'), ('age', '63'), ('sex', '0'), ('syncope', '0'), ('pulse', '91'), ('systolicbloodpressure', '127'), 
('haemoglobin', '113'), ('urea', '11.0'), ('creatinine', '102'), ('albumin', '35.8'), ('inr', '1.4'), ('alteredmentalstatus', '0'), ('ischaemicheartdisease', '0'), 
('cardiacfailure', '0'), ('renalfailure', '0'), ('malignancy_all', '0'), ('asascore', '1'), ('haemetemesis', '0'), ('melaena', '0'), ('haematochezia', '0'), 
('Aspirin', '0'), ('adp_inhibitors', '0'), ('Anticoagulant', '0'), ('nsaids', '0'), ('liver_categ', '0'), ('need_of_hospital_based_intervention', '0')])
"""
def createPatient(fout, p):
	# Demographic
	# Age 62.7 (18-106) 
	# Sex 58% (male, female)
    if p['sex'] == '1':
        gender = 'male'
        firstName = getName(maleFirstNames)
    else:
        gender = 'female'
        firstName = getName(femaleFirstNames)
    lastName = getName(lastNames)
    birthDate = getBirthDate(p['age'])
    line = firstName + ',' + lastName + ',' + gender + ',' + birthDate
	
	# Comorbidity
	# ASA Score 1 12% 2 30% 3 47% 4 9.9% 5 0.8%
    line += ',' + p['asascore']	
	# Ischemic Heart Disease 20%
    line += ',' + p['ischaemicheartdisease']
	# Cardiac Failure 10%
    line += ',' + p['cardiacfailure'] 
	# Renal Failure 8%
    line += ',' + p['renalfailure'] 
	# Liver 0 81% 1 5% 2 6% 3 9%
    line += ',' + p['liver_categ'] 
	# Any Malignancy 15%
    line += ',' + p['malignancy_all'] 

	# Medications
	# Aspirin 26%
    line += ',' + p['Aspirin'] 
	# Adenosine diphosphate (ADP) Inhibitors (Clopidogrel/Prasugrel, Ticagrelor) 7%
    line += ',' + p['adp_inhibitors'] 
	# Anticoagulation 13%
    line += ',' + p['Anticoagulant'] 
	# Non-steroidal anti-inflammatory drugs (NSAIDs) 14%
    line += ',' + p['nsaids'] 

	# Clinical Features at Presentation
	# Pulse 91.5 (0-180)
    line += ',' + p['pulse']
	# Systolic Blood Pressure 127.2 (0-200)
    line += ',' + p['systolicbloodpressure']
	# Syncope 10%
    line += ',' + p['syncope'] 
	# Altered Mental Status 11%
    line += ',' + p['alteredmentalstatus'] 
	# Hematemesis (Vomiting Blood) 43%
    line += ',' + p['haemetemesis'] 
	# Melena (Black Tarry Stool) 51%
    line += ',' + p['melaena'] 
	# Hematochezia (Bloody Stool) 6%
    line += ',' + p['haematochezia'] 

	# Initial Laboratory Values
	# Hemoglobin 112.8 (16-205)
    line += ',' + p['haemoglobin']
	# Urea 11.0 (0.5-80)
    line += ',' + p['urea']
	# Creatinine 102.5 (0-707.2)
    line += ',' + p['creatinine']
	# Albumin 35.8 (8-65)
    line += ',' + p['albumin']
	# INR 1.4 (0.4-10)
    line += ',' + p['inr']
    
    fout.write(line+'\n')

def convert():
    # Read names
    with open('FirstNamesMale.txt', 'r') as f: 
        for name in f: maleFirstNames['n'].append(name.strip())
    with open('FirstNamesFemale.txt', 'r') as f: 
        for name in f: femaleFirstNames['n'].append(name.strip())
    with open('LastNames.txt', 'r') as f: 
        for name in f: lastNames['n'].append(name.strip())
    # Read CSV file
    with open('patients_fhir.csv', 'w') as fout:
        createHeader(fout)
        with open('patients.csv', 'r') as fin:
            for p in csv.DictReader(fin, delimiter = ','):
                createPatient(fout, p)

if __name__ == '__main__':
    convert()
    