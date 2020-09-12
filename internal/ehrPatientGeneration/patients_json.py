import fhir
import json
import csv
import sys
import random

def createMedicationStatement(data, p, name):
    if p[name] != '0': 
        print('Creating medicationStatement '+name)
        data.append({ "resource": fhir.medicationStatement(p['Patient ID'], name), "request": { "method": "POST", "url": "MedicationStatement" } })

def createCondition(data, p, name):
    if p[name] != '0': 
        print('Creating condition '+name+' '+p[name])
        data.append({ "resource": fhir.condition(p['Patient ID'], name, p[name]), "request": { "method": "POST", "url": "Condition" } })

def createObservation(data, p, category, name, unit='', cnames=None):
    if cnames == None:
        print('Creating observation '+name+' '+p[name]+' '+unit)
        d = fhir.observation(p['Patient ID'], category, name, p[name], unit)
    else:
        d = fhir.observation(p['Patient ID'], category, name)
        for cname in cnames:
            print('Creating observation '+cname+' '+p[cname]+' '+unit)
            d = fhir.observationComponent(d, cname, p[cname], unit)
    data.append({ "resource": d, "request": { "method": "POST", "url": "Observation" } })

def createPatient(p, fout):
    data = []
    # Comorbidity
    # ASA Score 1 12% 2 30% 3 47% 4 9.9% 5 0.8%
    createCondition(data, p, 'ASA Score')
    # Ischemic Heart Disease 20%
    createCondition(data, p, 'Ischemic Heart Disease')
    # Cardiac Failure 10%
    createCondition(data, p, 'Cardiac Failure')
    # Renal Failure 8%
    createCondition(data, p, 'Renal Failure')
    # Liver 0 81% 1 5% 2 6% 3 9% 0=no liver disease, 1=liver disease, 2=liver cirrhosis, 3=liver failure
    createCondition(data, p, 'Liver')
    # Any Malignancy 15%
    createCondition(data, p, 'Any Malignancy')

    # Medications
    # Aspirin 26%
    createMedicationStatement(data, p, 'Aspirin')
    # Adenosine diphosphate (ADP) Inhibitors (Clopidogrel/Prasugrel, Ticagrelor) 7%
    createMedicationStatement(data, p, 'Adenosine Diphosphate Inhibitors')
    # Anticoagulation 13%
    createMedicationStatement(data, p, 'Anticoagulation')
    # Non-steroidal anti-inflammatory drugs (NSAIDs) 14%
    createMedicationStatement(data, p, 'NSAIDs')

    # Clinical Features at Presentation
    # Pulse 91.5 (0-180)
    createObservation(data, p, 'vital-signs', 'Pulse', 'bpm')
    # Systolic Blood Pressure 127.2 (0-200)
    p['Diastolic Blood Pressure'] = str(random.randrange(70,90))
    createObservation(data, p, 'vital-signs', 'Blood Pressure', 'mmHg', ['Systolic Blood Pressure','Diastolic Blood Pressure'])
    # Syncope 10%
    createCondition(data, p, 'Syncope')
    # Altered Mental Status 11%
    createCondition(data, p, 'Altered Mental Status')
    # Hematemesis (Vomiting Blood) 43%
    createCondition(data, p, 'Hematemesis')
    # Melena (Black Tarry Stool) 51%
    createCondition(data, p, 'Melena')
    # Hematochezia (Bloody Stool) 6%
    createCondition(data, p, 'Hematochezia')

    # Initial Laboratory Values
    # Hemoglobin 112.8 (16-205)
    createObservation(data, p, 'laboratory', 'Hemoglobin', 'g/L')
    # Urea 11.0 (0.5-80)
    createObservation(data, p, 'laboratory', 'Urea', 'mg/L')
    # Creatinine 102.5 (0-707.2)
    createObservation(data, p, 'laboratory', 'Creatinine', 'mg/L')
    # Albumin 35.8 (8-65)
    createObservation(data, p, 'laboratory', 'Albumin', 'g/L')
    # INR 1.4 (0.4-10)
    createObservation(data, p, 'laboratory', 'INR')

    fout.write(json.dumps(data)+'\n')

def createFromCSV(patientId, max):
    # Read CSV file
    pi = 1
    with open('patients_'+patientId+'.json', 'w') as fout:
        fout.write('{ "resourceType": "Bundle", "type": "transaction", "entry":\n')
        with open('patients_fhir.csv', 'r') as f:
            for p in csv.DictReader(f, delimiter = ','):
                p['Patient ID'] = patientId
                print('Creating patient '+str(pi)+'...')
                createPatient(p, fout)
                pi += 1
                if pi > max: break
        fout.write('}')

if __name__ == '__main__':
    patientId = '151'
    max = 1
    if len(sys.argv) > 1: patientId = sys.argv[1]
    if len(sys.argv) > 2: max = sys.argv[2]
    createFromCSV(patientId,max)
