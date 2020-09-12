index.html -> Click a link to /fhir/<launch-ehr-standalone>.html

/fhir/<launch-ehr-standalone> -> Invoke oauth.authorize() function with given client ID, scope, and server. Then redirects to /fhir/index.html with an access token upon successful authorization.

/fhir/index.html -> Invoke retrieveData() to use access token , which then calls processData() in smart-app.js to display the assessment

smart-app.js -> processData() invokes GCP function riskAssessment() to run the GIB model on the data

Starting Pages:
index.html - EHR Launches
demo.html - EHR + Standalone Launches

./fhir/:
EHR Launch Pages
Standalone Launch Pages
Client UI (./fhir/index.html)

PWA Files:
app.js
sw.js
manifest.json
favicon.ico
./images/