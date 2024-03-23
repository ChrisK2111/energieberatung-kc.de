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
			.then(response => response.json())
			.then(data => {
				// Verarbeite die JSON-Antwort hier
				plotSfp(data);
			})
			.catch(error => {
				console.error('Fehler beim Senden des Formulars:', error);
			});
		});
	};
});




function plotSfp(primaryEnergyDemand) {

	let q0Building = primaryEnergyDemand['heating_demand'];

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