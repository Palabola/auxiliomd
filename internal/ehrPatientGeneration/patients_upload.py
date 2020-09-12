import fhir
import json
import csv
import sys
import random
from datetime import datetime, timedelta

def randomDateTime(min_year=2010, max_year=2018):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    d = start + (end - start) * random.random()
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
def createMedicationStatement(p, name):
    if p[name] != '0': 
        print('Creating medicationStatement '+name)
        return ','+ fhir.post(fhir.medicationStatement(p['Patient ID'], name)) +','+p[name]
    else:
        return ',,'+p[name]

def createCondition(p, name):
    if p[name] != '0': 
        print('Creating condition '+name+' '+p[name])
        return ','+ fhir.post(fhir.condition(p['Patient ID'], name, p[name])) +','+p[name]
    else:
        return ',,'+p[name]

def createObservation(p, category, name, unit='', effectiveDateTime='', value='', cnames=None, cvalues=None):
    v = ''
    if cnames == None:
        if value == '': value = p[name]
        print('Creating observation '+name+' '+value+' '+unit)
        data = fhir.observation(p['Patient ID'], category, name, value, unit, effectiveDateTime)
        v += ','+value
    else:
        data = fhir.observation(p['Patient ID'], category, name, '', '', effectiveDateTime)
        for idx, cname in enumerate(cnames):
            if cvalues == None: value = p[cname]
            else: value = cvalues[idx]
            print('Creating observation '+cname+' '+value+' '+unit)
            data = fhir.observationComponent(data, cname, value, unit)
            v += ','+value
    return ','+ fhir.post(data) +v

def createPatient(p, orgId, fout):
    # Demographic
    patientId = fhir.post(fhir.patient(orgId, p['First Name'], p['Last Name'], p['Gender'], p['Birth Date']))
    print('Patient ID: '+patientId)
    if int(patientId) < 0: return;
    p['Patient ID'] = patientId
    line = p['Patient ID']+','+p['First Name']+','+p['Last Name']+','+p['Gender']+','+p['Birth Date']
    # Comorbidity
    for name in ['ASA Score','Ischemic Heart Disease','Cardiac Failure','Renal Failure','Liver','Any Malignancy']: line += createCondition(p, name)
    # Medications
    for name in ['Aspirin','Adenosine Diphosphate Inhibitors','Anticoagulation','NSAIDs']: line += createMedicationStatement(p, name)
    # Clinical Features at Presentation
	# Pulse 91.5 (0-180)
    line += createObservation(p, 'vital-signs', 'Pulse', 'bpm', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'vital-signs', 'Pulse', 'bpm', randomDateTime(2010,2018), str(random.randrange(60,180)))
	# Systolic Blood Pressure 127.2 (0-200)
    p['Diastolic Blood Pressure'] = str(random.randrange(70,90))
    line += createObservation(p, 'vital-signs', 'Blood Pressure', 'mmHg', randomDateTime(2019,2019), cnames=['Systolic Blood Pressure','Diastolic Blood Pressure'])
    for i in range(4): 
        createObservation(p, 'vital-signs', 'Blood Pressure', 'mmHg', randomDateTime(2010,2018), 
            cnames=['Systolic Blood Pressure','Diastolic Blood Pressure'], cvalues=[str(random.randrange(60,180)), str(random.randrange(40,120))])
    for name in ['Syncope','Altered Mental Status','Hematemesis','Melena','Hematochezia']: line += createCondition(p, name)
    # Initial Laboratory Values
	# Hemoglobin 112.8 (16-205)
    line += createObservation(p, 'laboratory', 'Hemoglobin', 'g/L', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'laboratory', 'Hemoglobin', 'g/L', randomDateTime(2010,2018), str(random.randrange(20,200)))
	# Urea 11.0 (0.5-80)
    line += createObservation(p, 'laboratory', 'Urea', 'mg/L', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'laboratory', 'Urea', 'mg/L', randomDateTime(2010,2018), str(random.randrange(1,80)))
	# Creatinine 102.5 (0-707.2)
    line += createObservation(p, 'laboratory', 'Creatinine', 'mg/L', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'laboratory', 'Creatinine', 'mg/L', randomDateTime(2010,2018), str(random.randrange(1,700)))
	# Albumin 35.8 (8-65)
    line += createObservation(p, 'laboratory', 'Albumin', 'g/L', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'laboratory', 'Albumin', 'g/L', randomDateTime(2010,2018), str(random.randrange(10,60)))
	# INR 1.4 (0.4-10)
    line += createObservation(p, 'laboratory', 'INR', '', randomDateTime(2019,2019))
    for i in range(4): createObservation(p, 'laboratory', 'INR', '', randomDateTime(2010,2018), str(random.randrange(1,10)))

    fout.write(line+'\n')

def createHeader(fout):
    # Demographic
    line = 'Patient ID,First Name,Last Name,Gender,Birth Date'
    # Comorbidity
    for name in ['ASA Score','Ischemic Heart Disease','Cardiac Failure','Renal Failure','Liver','Any Malignancy']: line += ','+name+' ID,'+name
    # Medications
    for name in ['Aspirin','Adenosine Diphosphate Inhibitors','Anticoagulation','NSAIDs']: line += ','+name+' ID,'+name
    # Clinical Features at Presentation
    line += ',Pulse ID,Pulse,Blood Pressure ID,Systolic Blood Pressure,Diastolic Blood Pressure'
    for name in ['Syncope','Altered Mental Status','Hematemesis','Melena','Hematochezia']: line += ','+name+' ID,'+name
    # Initial Laboratory Values
    for name in ['Hemoglobin','Urea','Creatinine','Albumin','INR']: line += ','+name+' ID,'+name
    fout.write(line+'\n')
    
def createFromCSV(server, orgId, start, max):
    # Read CSV file
    pi = 1
    with open('patients_'+server+'_'+orgId+'.csv', 'w') as fout:
        createHeader(fout)
        with open('patients_fhir.csv', 'r') as f:
            for p in csv.DictReader(f, delimiter = ','):
                if pi >= start:
                    print('Creating patient '+str(pi)+'...')
                    createPatient(p, orgId, fout)
                pi += 1
                if pi > max: break

if __name__ == '__main__':
    server = 'logica01'
    start = 248             # Change this
    max = 248               # Change this
    if len(sys.argv) > 1: server = sys.argv[1]
    if len(sys.argv) > 2: max = int(sys.argv[2])
    fhir.baseUrl = fhir.baseUrls[server]
    #orgId = fhir.post(fhir.organization('AuxilioMD01'))
    orgId = "1"
    print('Org ID: '+orgId)
    if int(orgId) > 0:
        createFromCSV(server, orgId, start, max)
        print('Org ID: '+orgId)
