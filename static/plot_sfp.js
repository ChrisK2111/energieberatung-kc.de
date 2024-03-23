const colorCodes = [
	{ qp:  30, class: "A+", rgb:   [0,166,80], description: "Fortschrittlicher Standard"},
	{ qp:  50, class:  "A", rgb:  [53,178,75], description: "Gesetzliche Anforderung an Neubauten"},
	{ qp:  75, class:  "B", rgb: [134,199,59], description: "Gesetzliche Anforderung an Neubauten (Stand 2002)"},
	{ qp: 100, class:  "C", rgb: [207,222,35], description: "Teilsaniertes Gebäude"},
	{ qp: 130, class:  "D", rgb:  [255,241,0], description: "Teilsaniertes oder unsaniertes Gebäude"},
	{ qp: 160, class:  "E", rgb: [254,207,11], description: "Teilsaniertes oder unsaniertes Gebäude"},
	{ qp: 200, class:  "F", rgb: [246,117,26], description: "Teilsaniertes oder unsaniertes Gebäude"},
	{ qp: 250, class:  "G", rgb:  [177,16,22], description: "Teilsaniertes oder unsaniertes Gebäude"},
	{ qp: 999, class:  "H", rgb:  [177,16,22], description: "Teilsaniertes oder unsaniertes Gebäude"}
];

const descriptionInitialCondition = [
	{qp:  30, text: ["Ihr Gebäude erfüllt die fortschrittlichsten energetischen Standards.  Glückwunsch!"]},
	{qp:  60, text: ["Ihr Gebäude erfüllt die aktuell geltenden Anforderungen an Neubauten. Glückwunsch!"]},
	{qp:  90, text: ["Ihr Gebäude erfüllt die Anforderungen an Neubauten aus dem Jahr 2002."]},
	{qp: 130, text: ["Die energetische Eigenschaften ihres Gebäudes sind überdurchschnittlich gut, bieten aber dennoch ein großes Einsparpotential."]},
	{qp: 180, text: ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
					"Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
	{qp: 230, text: ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
					 "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
	{qp: 999, text: ["Der Energieverbrauch Ihres Gebäudes ist außerordentlich groß.",
					 "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]}
]

document.addEventListener('DOMContentLoaded', function () {
	if (window.location.pathname === '/sfp'){
		document.getElementById('sfpForm').addEventListener('submit', function(event) {
			event.preventDefault(); // Standardformularverhalten unterdrücken
		
			// Formulardaten als FormData-Objekt sammeln
			const formData = new FormData(this);
		
			// POST-Anfrage an die Flask-Route senden
			fetch('/sfp', {
				method: 'POST',
				body: formData
			})
			.then(response => {
				// Überprüfen, ob die Anfrage erfolgreich war
				if (!response.ok) {
					throw new Error('Serverfehler: ' + response.status);
				}
				// Die HTML-Seite als Text extrahieren
				return response.text();
			})
			.then(html => {
				// Die HTML-Seite im Browser anzeigen
				document.body.innerHTML = html;
				// GET-Anfrage senden, nachdem die Seite geladen wurde
				return fetch('/get_sfp_data'); // Diese Route gibt den JSON-String zurück
			})
			.then(response => response.json())
			.then(data => {
				// Verarbeite die JSON-Antwort hier
				plotSfp(data);
				plotSfpRetrofitChart(data)
			})
			.catch(error => {
				console.error('Fehler beim Senden des Formulars:', error);
			});
		});
	};
});




function plotSfp(primaryEnergyDemand) {

	let q0Building = primaryEnergyDemand[0]['heating_demand'];

	if (typeof sfpEClassChart !== 'undefined') { // Überprüfen, ob das Diagramm vorhanden ist, bevor es zerstört wird
		sfpEClassChart.destroy();
	}

	let ctx = document.getElementById('SfpEnergyEfficiencyChart');
	ctx.style.display = '';

	let qData = colorCodes.slice(0,-1).map(row => row.qp)
	let numEClasses = qData.length;
	let indexBuilding = 0;
	let labels = colorCodes.slice(0,-1).map(row => row.class);
	let backgroundColor = colorCodes.slice(0,-1).map(row => 'rgb(' +row.rgb + ')');
	let xmax = qData[qData.length -1] + 80;

	if (q0Building> qData[numEClasses-1]){
		qData[numEClasses] = q0Building;
		indexBuilding = numEClasses;
		labels = colorCodes.map(row => row.class);
		backgroundColor = colorCodes.map(row => 'rgb(' +row.rgb + ')');
		xmax = q0Building + 80;
	} else {
		for (ii = 0; ii < numEClasses; ii++) {
			if (q0Building <= qData[ii]) {
				indexBuilding = ii;
				break
			}
		}
	}

	let data = {
			labels,
			datasets: [
			{
				data: qData,
				backgroundColor
			}
			]
		};


	sfpEClassChart = new Chart(
		ctx,
		{
		  type: 'bar',
		  data: data,
		options: {
			devicePixelRatio: 4,
			responsive: true,
			maintainAspectRatio: false,
			indexAxis: 'y',
			events: null,
			plugins:{
				legend: {
					display: false // Hier wird die Legende deaktiviert
				},
				tooltip: {
						backgroundColor: 'rgba(0,0,0,0.5)',
						xAlign: 'left',
						displayColors: false,
						callbacks: {
							title: function(context){
								return null
							},
							label: function(context){
								return 'Ihr Gebäude'
							}
						}
				}
			},
			scales: {
					x: {
						max: xmax,
						title: {
							display: true,
							text: 'Energie in kWh/(m\u00B2a)'
						}
						},
					y: {
						title: {
							display: true,
							text: 'Effizienzklasse'
						}
					}
				}
			}
		}
	  );
	  
	  sfpEClassChart.tooltip.setActiveElements([{datasetIndex:0, index: indexBuilding}]);
	  sfpEClassChart.update();


}

function populateInitialConditionCard(rfData){
	let container = document.getElementById("descriptionInitialConditionContainer");

	let demand0   = Math.round(rfData[0]['primary_energy_demand']);
	let demandEnd = Math.round(rfData[rfData.length - 1]['primary_energy_demand']);
	let p1 = document.createElement('p');
	let p2 = document.createElement('p');
	let description = "";
	let eClass = getEnergyClass(demand0);
	let cost = Math.round(rfData[0]['energy_cost']  / 10) * 10;
	let savings = Math.round((rfData[0]['energy_cost'] - rfData[rfData.length - 1]['energy_cost']) / 10) * 10;



	for (ii=0;ii<descriptionInitialCondition.length;ii++) {
		if (demand0 <= descriptionInitialCondition[ii].qp){
			description = descriptionInitialCondition[ii].text.join(' ');
			break
		}
	}


	// Löscht alle Kinder des Containers
    container.innerHTML = '';

	p1.textContent = description;
	container.appendChild(p1)

	p2.innerHTML = "Der rechnerische Endenergiebedarf Ihres Gebäudes beträgt " + 
					'<span style="white-space: nowrap">'+demand0 + ' kWh/(m\u00B2a). </span>' + "<br>" +
					"Damit erfüllt Ihr Gebäude die Anforderungen der Energieeffizienzklasse <strong>" + eClass +"</strong>.";
	container.appendChild(p2)

}

function plotSfpRetrofitChart(rfData){
	var qData  = [];
	var rgbData = [];
	var labels = [];
	var idRf = 'Ist';

	for (yr = 0; yr < rfData.length; yr++) {
		if (rfData[yr].retrofit_cost > 0 || yr === 0) {
			let q = rfData[yr].primary_energy_demand;
			qData.push(q);
			rgbData.push(
				'rgba(' + getRGBofDemand(q).join(', ') + ', 0.9)'
				);
			labels.push(idRf);
			if (idRf==='Ist'){
				idRf = 0;
			}
			idRf += 1;
		}
	}

	var data = {
		labels: labels,
		datasets: [{
			label: "Primärenergiebedarf",
			data: qData,
			backgroundColor: rgbData
		}]
	}

	if (typeof sfpChart !== 'undefined') { // Überprüfen, ob das Diagramm vorhanden ist, bevor es zerstört wird
		sfpChart.destroy();
	}
	var grapharea = document.getElementById('sanierungsfahrplanChart')

	grapharea.style.display = '';

	var config = {
		type: 'bar',
		data: data,
		options: {
			devicePixelRatio: 4,
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					title: {
						display: true,
						text: 'Energie in kWh/(m\u00B2a)'
					},
				},
				x: {
					title: {
						display: true,
						text: 'Maßnahme',
					}
				}
			},
			plugins: {
				legend: {
					display: false
				},
				tooltip: {
					callbacks: {
						label: function(context) {
							let label = context.dataset.label || '';
	
							if (label) {
								label += ': ';
							}
							if (context.parsed.y !== null) {
								label += Math.round(context.parsed.y);
							}
							return label;
						},
						title: function(context) {
							let title = context[0].label || '';
	
							if (title!=='Ist') {
								title = 'Maßnahme: ' + title;
							}
							return title;
						}
					}
				}
			}
		}
	};


	

	sfpChart = new Chart(grapharea, config
	);


	return data;
}

function getEnergyClass(demand){
	let eClass = "";
	for (ii=0;ii<colorCodes.length;ii++) {
		if (demand <= colorCodes[ii].qp){
			eClass = colorCodes[ii].class;
			break
		}
	}
	return eClass;
}

function getRGBofDemand(demand) {
	var rgbValues = [200, 200, 200];
	// Neue RGB-Werte definieren (z.B. 255, 0, 0 für Rot)
	// lineare interpolation zwischen zwei Werten
	for (jCode = 0; jCode < colorCodes.length; jCode++) {
		if (demand <= colorCodes[jCode].qp) {
			let ratio = 1;
			let rgb1 = colorCodes[jCode].rgb;
			let rgb2 = colorCodes[jCode].rgb;
			if (jCode !== 0) {
				rgb2 = colorCodes[jCode - 1].rgb
				ratio = (demand - colorCodes[jCode].qp) / (colorCodes[jCode - 1].qp - colorCodes[jCode].qp);
			}

			rgbValues = rgb1.map(function (element, index) {
				return element + (rgb2[index] - element) * ratio;
			})

			break
		}
	}
	return rgbValues; 
}