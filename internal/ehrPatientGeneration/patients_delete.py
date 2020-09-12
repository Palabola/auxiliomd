import fhir
import csv
import sys

def deleteResourceFromCSV(p):
    # Comorbidity
    for name in ['ASA Score','Ischemic Heart Disease','Cardiac Failure','Renal Failure','Liver','Any Malignancy']: fhir.delete('Condition', p[name+' ID'])

    # Medications
    for name in ['Aspirin','Adenosine Diphosphate Inhibitors','Anticoagulation','NSAIDs']: fhir.delete('MedicationStatement', p[name+' ID'])

    # Clinical Features at Presentation
    for name in ['Pulse','Blood Pressure']: delete('Observation', p[name+' ID'])
    for name in ['Syncope','Altered Mental Status','Hematemesis','Melena','Hematochezia']: fhir.delete('Condition', p[name+' ID'])

    # Initial Laboratory Values
    for name in ['Hemoglobin','Urea','Creatinine','Albumin','INR']: fhir.delete('Observation', p[name+' ID'])

    # Demographic
    fhir.delete('Patient', p['Patient ID'])

def deletePatientFromCSV(server, orgId):
    # Read CSV file
    pi = 1
    with open('patients_'+server+'_'+orgId+'.csv', 'r') as f:
        for p in csv.DictReader(f, delimiter = ','):
            print('Deleting patient '+str(pi)+'...')
            deleteResourceFromCSV(p)
            pi += 1

def deleteResource(type, query):
    r = fhir.search(type, query)
    if not 'entry' in r: return
    for re in r['entry']: 
        print('Deleting '+type+' '+re['resource']['id'])
        fhir.delete(type, re['resource']['id'])

def deletePatient(server, orgId):
    # Read FHIR server
    pi = 1
    r = fhir.search('Patient', 'organization=Organization/'+orgId)
    if not 'entry' in r: return
    for re in r['entry']:
        print('Deleting patient '+str(pi)+'...')
        patientId = re['resource']['id']
        if server in fhir.cascadeServers:
            patientId += '?_cascade=delete'
        else:
            deleteResource('Observation', 'subject=Patient/'+patientId)
            deleteResource('Condition', 'subject=Patient/'+patientId)
            deleteResource('MedicationStatement', 'subject=Patient/'+patientId)
        fhir.delete('Patient', patientId)
        pi += 1

if __name__ == '__main__':
    server = 'logica3'
    orgId = '1'
    csv = False
    if len(sys.argv) > 1: orgId = sys.argv[1]
    if len(sys.argv) > 2: server = sys.argv[2]
    if len(sys.argv) > 3: 
        if sys.argv[3] == 'True': csv = True
    fhir.baseUrl = fhir.baseUrls[server]
    if csv:
        deletePatientFromCSV(server, orgId)
    else:
        deletePatient(server, orgId)
