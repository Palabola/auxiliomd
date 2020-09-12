// --------------------------
// Firebase Configuration
// --------------------------
var firebaseConfig = {
	// Insert Firebase configuration here
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

var functions = firebase.functions();

/**
 * Retrieves data from given FHIR server
 * @param {*} serviceUrl - Required if not invoked with OAuth2.0.
 * @param {*} patientId - Required if not invoked with OAuth2.0.
 */
function retrieveData(serviceUrl = "", patientId = "") {
	var ret = $.Deferred();

	/**
	 * Returns the severity of a Condition entry as a string
	 * @param {*} entrySeverity - JSON containing the severity of the Condition entry
	 */
	function getCondition(entrySeverity) {
		return entrySeverity.text;
	}

	/**
	 * Returns the valueQuantity of an Observation entry as a string
	 * @param {*} entryValueQuantity - JSON containing the value and unit of the Observation entry
	 */
	function getObservation(entryValueQuantity) {
		//https://www.hl7.org/fhir/observation.html
		//valueQuantity, valueCodeableConcept, valueString, valueBoolean, valueInteger, valueRange, valueRatio, valueSampledData, valueTime, valueDateTime, valuePeriod
		valueString = entryValueQuantity.value;
		if (entryValueQuantity.unit != null) {
			valueString += " " + entryValueQuantity.unit;
		}
		return valueString;
	}

	/**
	 * Adds a new name-value pair to the result dictionary for the given medical entry
	 * @param {*} entry - Raw JSON of the medical entry
	 * @param {*} resourceType - Type of the resource (e.g. Observation, Condition, MedicationStatement)
	 * @param {*} entryNameKey - Name of the entry attribute containing the name of the medical entry (e.g. code, medicationCodeableConcept)
	 * @param {*} entryValueKey - Name of the entry attribute containing the value of the medical entry (e.g. valueQuantity, severity)
	 * @param {*} valueRetrieveFunction - Function for retrieving the value of an entry
	 * @param {*} result - Dictionary meant to contain name-value pairs for each medical entry in a given resourceType
	 * Modifies result
	 */
	function getData(entry, resourceType, entryNameKey, entryValueKey, valueRetrieveFunction, result) {
		if (entry.resourceType != null && entry.resourceType != resourceType) {	// resourceType not what we expect, nothing to do
			return;
		}

		if (entry[entryNameKey] == null) {
			return;
		}

		if (entryValueKey == null || typeof entry[entryValueKey] == "undefined") {
			processedEntry = {
				value: "",
				id: entry.id,
				effectiveDateTime: entry.effectiveDateTime
			};
		} else {
			processedEntry = {
				value: valueRetrieveFunction(entry[entryValueKey]),
				id: entry.id, effectiveDateTime: entry.effectiveDateTime
			};
		}

		entryName = entry[entryNameKey].text;

		if (entryName in result) {
			result[entryName].push(processedEntry);
		} else {
			result[entryName] = [processedEntry];
		}
	}

	/**
	 * Returns a dictionary containing name-value pairs for each medical entry in a given resourceType
	 * @param {*} resourceObj - Raw JSON containing all entries with the given resourceType
	 * @param {*} resourceType - Type of the resource (e.g. Observation, Condition, MedicationStatement)
	 * @param {*} entryNameKey - Name of the entry attribute containing the name of the medical entry (e.g. code, medicationCodeableConcept)
	 * @param {*} entryValueKey - Name of the entry attribute containing the value of the medical entry (e.g. valueQuantity, severity)
	 * @param {*} valueRetrieveFunction - Function for retrieving the value of an entry
	 */
	function getSmartData(fhirObj, resourceType, entryNameKey, entryValueKey, valueRetrieveFunction) {
		// console.log(JSON.stringify(fhirObj, null, 2));

		result = {}

		// Unwrapping fhirObj from 'data' attribute if needed
		if (fhirObj.data != null) {	// public query returns with results wrapped in data dict
			if (fhirObj.data.entry != null) {
				entries = fhirObj.data.entry;
			} else {	// a search can end up with 0 entry
				return {};
			}
		} else {	// oauth2 query returns results without wrapping in data dict
			entries = fhirObj;
		}

		entries.forEach(function (entry) {

			// Unwrapping entry from 'resource' attribute if needed
			if (entry.resource != null) {	// public query returns with results wrapped in resource dict
				entry = entry.resource;
			}

			if (entry.component != null) { // Check for multiple components. Observations like Blood Pressure has sub-components like Systolic and Diastolic Blood Pressure
				entry.component.forEach(function (component) {
					// Manually adding attributes from entry into component for standardization
					component["id"] = entry.id;
					component["effectiveDateTime"] = entry.effectiveDateTime;
					getData(component, resourceType, entryNameKey, entryValueKey, valueRetrieveFunction, result);
				})
			} else {
				//console.log(entry[entryNameKey].text);
				getData(entry, resourceType, entryNameKey, entryValueKey, valueRetrieveFunction, result);
			}
		});

		return result;
	}

	/**
	 * Returns a dictionary containing processed patient information
	 * @param {*} patientFHIRObj - JSON containing patient data as specified by the FHIR standard
	 */
	function getPatientData(patientFHIRObj) {
		// console.log(patientFHIRObj);
		var patient = {}
		if (typeof patientFHIRObj.name[0] !== "undefined") {
			patient["First Name"] = (typeof patientFHIRObj.name[0].given == "string" ? patientFHIRObj.name[0].given : patientFHIRObj.name[0].given.join(" "));		// Check multiple first names
			patient["Last Name"] = (typeof patientFHIRObj.name[0].family == "string" ? patientFHIRObj.name[0].family : patientFHIRObj.name[0].family.join(" "));	// Check multiple last names
		}
		patient["Gender"] = patientFHIRObj.gender;
		patient["Birth Date"] = patientFHIRObj.birthDate;
		return patient;
	}

	/**
	 * Callback from FHIR on successful connection
	 * @param {*} smartReference - Reference object to the FHIR server with many query functions
	 */
	function onReady(smartReference) {
		if (smartReference.hasOwnProperty('patient')) {
			var patientPromise = smartReference.patient.read();

			var observationPromise = smartReference.patient.api.search({ type: "Observation", query: { category: "vital-signs,laboratory", _count: 100 } });
			var conditionPromise = smartReference.patient.api.search({ type: "Condition", query: { _count: 100 } });
			var medicationPromise = smartReference.patient.api.search({ type: "MedicationStatement", query: { _count: 100 } });

			$.when(patientPromise, observationPromise, conditionPromise, medicationPromise).fail(onError);
			$.when(patientPromise, observationPromise, conditionPromise, medicationPromise).done(function (patient, observation, condition, medication) {
				// Processing raw data
				ret.resolve({
					patient: getPatientData(patient),
					observation: getSmartData(observation, "Observation", "code", "valueQuantity", getObservation),
					condition: getSmartData(condition, "Condition", "code", "severity", getCondition),
					medication: getSmartData(medication, "MedicationStatement", "medicationCodeableConcept", null, null)
				});
			});
		} else {
			onError();
		}
	}

	/**
	 * Callback from FHIR on error
	 */
	function onError() {
		console.log("Loading error", arguments);
		ret.reject();
	}

	/* --- Main Execution --- */

	if (serviceUrl == "") {
		// Run with OAuth2
		FHIR.oauth2.ready(onReady, onError);
	} else {
		// Run without OAuth2
		onReady(FHIR.client({
			serviceUrl: serviceUrl,
			patientId: patientId
		}));
	}

	return ret.promise();
}