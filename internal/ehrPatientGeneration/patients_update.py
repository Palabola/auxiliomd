import fhir
import json
import csv
import sys
    
def updateMedicationStatement(p, name):
    if p[name+' ID'] != '':
        data = fhir.medicationStatement(p['Patient ID'], name, p[name])
        data['id'] = p[name+' ID']
        print('Updating medicationStatement '+name)
        fhir.update(data)

def updateCondition(p, name):
    if p[name+' ID'] != '': 
        data = fhir.condition(p['Patient ID'], name, p[name])
        data['id'] = p[name+' ID']
        print('Updating condition '+name+' '+p[name])
        fhir.update(data)

def updateObservation(p, category, name, unit='', cnames=None):
    if cnames == None:
        print('Updating observation '+name+' '+p[name]+' '+unit)
        data = fhir.observation(p['Patient ID'], category, name, p[name], unit)
    else:
        data = fhir.observation(p['Patient ID'], category, name)
        for cname in cnames:
            print('Updating observation '+cname+' '+p[cname]+' '+unit)
            data = fhir.observationComponent(data, cname, p[cname], unit)
    data['id'] = p[name+' ID']
    fhir.update(data)

def updatePatient(p, orgId):
    # Demographic
    data = fhir.patient(orgId, p['First Name'], p['Last Name'], p['Gender'], p['Birth Date'])
    data['id'] = p['Patient ID']
    print('Updating patient '+p['First Name']+' '+p['Last Name']+' '+p['Gender']+' '+p['Birth Date'])
    fhir.update(data)

    # Comorbidity
    for name in ['ASA Score','Ischemic Heart Disease','Cardiac Failure','Renal Failure','Liver','Any Malignancy']: updateCondition(p, name)

    # Medications
    for name in ['Aspirin','Adenosine Diphosphate Inhibitors','Anticoagulation','NSAIDs']: updateMedicationStatement(p, name)

    # Clinical Features at Presentation
    updateObservation(p, 'vital-signs', 'Pulse', 'bpm')
    updateObservation(p, 'vital-signs', 'Blood Pressure', 'mmHg', ['Systolic Blood Pressure','Diastolic Blood Pressure'])
    for name in ['Syncope','Altered Mental Status','Hematemesis','Melena','Hematochezia']: updateCondition(p, name)

    # Initial Laboratory Values
    updateObservation(p, 'laboratory', 'Hemoglobin', 'g/L')
    updateObservation(p, 'laboratory', 'Urea', 'mg/L')
    updateObservation(p, 'laboratory', 'Creatinine', 'mg/L')
    updateObservation(p, 'laboratory', 'Albumin', 'g/L')
    updateObservation(p, 'laboratory', 'INR')

def updateFromCSV(server, orgId):
    # Read CSV file
    pi = 1
    with open('patients_'+server+'_'+orgId+'.csv', 'r') as f:
        for p in csv.DictReader(f, delimiter = ','):
            print('Updating patient '+str(pi)+'...')
            updatePatient(p, orgId)
            pi += 1

if __name__ == '__main__':
    server = 'uhn'
    orgId = '2705851'
    if len(sys.argv) > 1: orgId = sys.argv[1]
    if len(sys.argv) > 2: server = sys.argv[2]
    fhir.baseUrl = fhir.baseUrls[server]
    updateFromCSV(server, orgId)
