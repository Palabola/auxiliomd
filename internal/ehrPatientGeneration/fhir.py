import requests
import json

cascadeServers = ['uhn']

baseUrls = { 'pyrohealth': 'https://stu3.test.pyrohealth.net/fhir/',
'uhn': 'http://fhirtest.uhn.ca/baseDstu3/',
'logicax': 'https://api.logicahealth.org/AuxilioMDX/open/',
'logica1': 'https://api.logicahealth.org/AuxilioMD1/open/',
'logica3': 'https://api.logicahealth.org/AuxilioMD3/open/',
'logica01': 'https://api.logicahealth.org/AuxilioMD01/open/' }

baseUrl = ''

def organization(name):
    data = { 
"resourceType": "Organization",
"name": name
}
    return data

def patient(organization, fname, lname, gender, birthDate):
    data = { 
"resourceType": "Patient",
"name": [{ "family": lname, "given": [ fname ] }],
"gender": gender,
"birthDate": birthDate,
"managingOrganization": { "reference": "Organization/"+organization }
}
    return data
    
def observation(patient, category, code, value='', unit='', effectiveDateTime='') :
    data = {
"resourceType": "Observation",
"subject": { "reference": "Patient/"+patient },
"code": { "coding": [{ "display": code }], "text": code },
"status": "final",
}
    if category == 'vital-signs':
        data['category'] = { "coding": [{ "system": "http://hl7.org/fhir/observation-category", "code": "vital-signs", "display": "Vital Signs" }], "text": "Vital Signs" }
    else:
        data['category'] = { "coding": [{ "system": "http://hl7.org/fhir/observation-category", "code": "laboratory", "display": "Laboratory" }], "text": "Laboratory" }
    if value != '': data['valueQuantity'] = { "value": value, "unit": unit }
    if effectiveDateTime != '': data['effectiveDateTime'] = effectiveDateTime
    return data
    
def observationComponent(obv, code, value, unit=''):
    if not 'component' in obv: obv['component'] = []
    obv['component'].append({ "code": { "coding": [{ "display": code }], "text": code }, "valueQuantity": { "value": value, "unit": unit }})
    return obv

def condition(patient, code, severity='1') :
    data = {
"resourceType": "Condition",
"subject": { "reference": "Patient/"+patient },
"code": { "coding": [{ "display": code }], "text": code },
"severity": { "coding": [{ "display": severity }], "text": severity }
}
    return data

def medicationStatement(patient, name, dosage=''):
    data = { # effectiveDateTime, effectivePeriod, taken, status
"resourceType": "MedicationStatement",
"subject": { "reference": "Patient/"+patient },
"medicationCodeableConcept": { "coding": [{ "display": name }], "text": name },
"status": "active",
"taken": "y",
"dosage": [{ "text": "once daily", "timing": { "repeat": { "frequency": 1, "period": 1, "periodUnit": "d" } }, "doseQuantity": { "value": 1, "unit": "tablet" } }]
}
    return data

def search(resourceType, query):
    r = requests.get(baseUrl+resourceType+'?'+query)
    if (r.status_code != 200):
        print('Failed to search '+resourceType+'?'+query)
        print(r.text)
        return None
    else:
        return json.loads(r.text)
        
def get(resourceType, id):
    if id == '': return # without id will return all resourceTypes in a bundle equivalent to search
    r = requests.get(baseUrl+resourceType+'/'+id)
    if (r.status_code != 200):
        print('Failed to get '+resourceType+'/'+id)
        print(r.text)
        return None
    else:
        return json.loads(r.text)
        
def post(data):
    r = requests.post(baseUrl+data['resourceType'], json=data)
    if (r.status_code != 201):
        print('Failed to add '+data['resourceType'])
        print(r.text)
        return '-1'
    else:
        return json.loads(r.text)['id']

def update(data):
    r = requests.put(baseUrl+data['resourceType']+'/'+data['id'], json=data)
    if (r.status_code != 200):
        print('Failed to update '+data['resourceType']+'/'+data['id'])
        print(r.text)
        return '-1'
    else:
        return '1'

def delete(resourceType, id):
    if id == '': return # cannot delete without id
    r = requests.delete(baseUrl+resourceType+'/'+id)
    if (r.status_code != 200):
        print('Failed to delete '+resourceType+'/'+id)
        print(r.text)
        return '-1'
    else:
        return '1'

"""
Create patient visually at http://clinfhir.com

http://fhirtest.uhn.ca/baseDstu3/Organization?name=AuxilioMD
http://fhirtest.uhn.ca/baseDstu3/Organization/2660673
http://fhirtest.uhn.ca/baseDstu3/Patient?organization=Organization/2660673
http://fhirtest.uhn.ca/baseDstu3/Patient?family=Auxilio
http://fhirtest.uhn.ca/baseDstu3/Patient/2660674
http://fhirtest.uhn.ca/baseDstu3/Observation?patient=2660674
http://fhirtest.uhn.ca/baseDstu3/Condition?patient=2660674
http://fhirtest.uhn.ca/baseDstu3/MedicationStatement?patient=2660674

Organization ID: 2695515 (10 patients), 2695634 (652 patients)

DELETE http://fhirtest.uhn.ca/baseDstu3/Organization/2695515?_cascade=delete
DELETE http://fhirtest.uhn.ca/baseDstu3/Patient/2660674?_cascade=delete

https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Patient/Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Observation?patient=Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB&code=8310-5
https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Condition?patient=Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/MedicationStatement?patient=Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB

https://www.hl7.org/fhir/patient.html
http://hl7.org/fhir/STU3/patient.html
http://hl7.org/fhir/DSTU2/patient.html
https://www.hl7.org/fhir/observation.html
http://hl7.org/fhir/STU3/observation.html
http://hl7.org/fhir/DSTU2/observation.html
https://www.hl7.org/fhir/condition.html
http://hl7.org/fhir/STU3/condition.html
http://hl7.org/fhir/DSTU2/condition.html
https://www.hl7.org/fhir/medicationstatement.html
http://hl7.org/fhir/STU3/condition.html
http://hl7.org/fhir/DSTU2/condition.html

https://open.epic.com/Clinical/Patient
https://open.epic.com/Clinical/Observation
https://open.epic.com/Clinical/Condition
https://open.epic.com/Clinical/Medication

https://fhir.cerner.com/millennium/dstu2/individuals/patient/
https://fhir.cerner.com/millennium/dstu2/diagnostic/observation/
https://fhir.cerner.com/millennium/dstu2/general-clinical/condition/
https://fhir.cerner.com/millennium/dstu2/medications/medication-statement/

https://homepage.net/name_generator/

https://fhir-drills.github.io/simple-patient.html
"""