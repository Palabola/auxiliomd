/**
 * Entry function to retrieve and display patient data
 * @param {*} patientId - ID of the patient
 * @param {*} fhirOauth2 - If the path requires OAuth2 authentication
 */
function showPatient(patientId, fhirOauth2 = false) {
	if (fhirOauth2) { // called from epic, cerner standalone or ehr index.html
		serviceUrl = "";
	} else {
		serviceUrl = "https://api.logicahealth.org/AuxilioMD01/open";
	}

	retrieveData(serviceUrl, patientId).then(	// Retrieves data from the FHIR server
		function (p) {	// p is the returned EHR data as a processed dictionary
			var patient = p["patient"];

			fhirTable(p, "observation");
			fhirTable(p, "condition");
			fhirTable(p, "medication");

			const systolicBPNormalizedValue = p['Systolic BP'];
			const hemoglobinNormalizedValue = p['Hemoglobin'];
			const heartRateNormalizedValue = p['Heart Rate'];
			const inrNormalizedValue = p['INR'];

			$("#systolic-bp").attr("data-value", "0.1");
			$("#hemoglobin").attr("data-value", "0.1");
			$("#heart-rate").attr("data-value", "0.1");
			$("#inr").attr("data-value", "0.1");

			// compute UGIB risk
			var ugibRisk = functions.httpsCallable("ugibRisk");

			ugibRisk(patient).then(function (result) {
				console.log("UGIB Risk: " + result)
				$("#risk").html("UGIB Risk: " + result.data.risk);
			});
		},
		// Display 'Failed to call FHIR Service' if extractData failed
		function () {
			window.alert('Failed to call FHIR Service');
		}
	);
}

/**
 * Normalizes the raw data into a more-easily processable format
 * @param {Object} p - Patient data
 * @oaran {string} fhirType - Attribute of patient data to be formatted
 */
function fhirTable(p, fhirType) {
	rs = p[fhirType];
	for (var key in rs) {
		values = rs[key];
		sortBy(values, { prop: "effectiveDateTime" });
		lastIndex = values.length - 1;
		value = values[lastIndex]["value"]
		p["patient"][key] = value;
	}
}

/**
 * Sorting function
 */
var sortBy = (function () {
	var toString = Object.prototype.toString,
		// default parser function
		parse = function (x) { return x; },
		// gets the item to be sorted
		getItem = function (x) {
			var isObject = x != null && typeof x === "object";
			var isProp = isObject && this.prop in x;
			return this.parser(isProp ? x[this.prop] : x);
		};

	/**
	 * Sorts an array of elements.
	 *
	 * @param {Array} array: the collection to sort
	 * @param {Object} cfg: the configuration options
	 * @property {String}   cfg.prop: property name (if it is an Array of objects)
	 * @property {Boolean}  cfg.desc: determines whether the sort is descending
	 * @property {Function} cfg.parser: function to parse the items to expected type
	 * @return {Array}
	 */
	return function sortby(array, cfg) {
		if (!(array instanceof Array && array.length)) return [];
		if (toString.call(cfg) !== "[object Object]") cfg = {};
		if (typeof cfg.parser !== "function") cfg.parser = parse;
		cfg.desc = !!cfg.desc ? -1 : 1;
		return array.sort(function (a, b) {
			a = getItem.call(cfg, a);
			b = getItem.call(cfg, b);
			return cfg.desc * (a < b ? -1 : +(a > b));
		});
	};

}());