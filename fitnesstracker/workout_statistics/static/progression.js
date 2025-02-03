document.addEventListener("DOMContentLoaded", function () {
    fetch('/statistics/api/exercises')
        .then(response => response.json())
        .then(exercises => {
            let dropdown = document.getElementById("exercise");
            exercises.forEach(exercise => {
                let option = document.createElement("option");
                option.value = exercise;
                option.textContent = exercise;
                dropdown.appendChild(option);
            });
            // Auto-update chart on page load with first exercise
            if (exercises.length > 0) {
                dropdown.value = exercises[0];
                updateChart();
            }
        })
        .catch(error => console.error("Error loading exercises:", error));
});


function updateChart() {
    let exercise = document.getElementById("exercise").value;
    let windowSize = document.getElementById("window").value;

    fetch(`/statistics/api/progression?exercise=${exercise}&window=${windowSize}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("plot_progression").innerHTML = `<p>${data.error}</p>`;
                document.getElementById("plot_volume").innerHTML = "";
                return;
            }

            let dates = data.map(d => d.Date);
            let weights = data.map(d => d.Weight);
            let reps = data.map(d => d.Repetitions);
            let volumes = data.map(d => d.Volume);
            let weightsMA = data.map(d => d.Weight_MA);
            let repsMA = data.map(d => d.Repetitions_MA);

            // First plot: Weight & Repetitions
            let weightTrace = {
                x: dates,
                y: weights,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Weight (kg)',
                line: { color: 'blue' }
            };

            let weightMATrace = {
                x: dates,
                y: weightsMA,
                type: 'scatter',
                mode: 'lines',
                name: `Weight MA (Window=${windowSize})`,
                line: { color: 'blue', dash: 'dash' }
            };

            let repsTrace = {
                x: dates,
                y: reps,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Repetitions',
                line: { color: 'red' }
            };

            let repsMATrace = {
                x: dates,
                y: repsMA,
                type: 'scatter',
                mode: 'lines',
                name: `Reps MA (Window=${windowSize})`,
                line: { color: 'red', dash: 'dash' }
            };

            let layout1 = {
                title: {
                    text: `Progression for ${exercise}`,
                    font: { size: 14 }
                },
                xaxis: { 
                    title: { text: "Date", font: { size: 12 } },
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: "Weight (kg) / Reps", font: { size: 12 } },
                    tickfont: { size: 10 }
                },
                legend: { font: { size: 10 }, orientation: "h", x: 0.5, xanchor: "center", y: -0.3 },
                margin: { l: 50, r: 30, t: 60, b: 50 }, // Increased top margin to 60px
                autosize: true,
                // modebar: { orientation: 'v' } // Move modebar to the side
            };

            Plotly.newPlot('plot_progression', [weightTrace, weightMATrace, repsTrace, repsMATrace], layout1,
                                         { displayModeBar: false });

            // Second plot: Volume
            let volumeTrace = {
                x: dates,
                y: volumes,
                type: 'bar',
                name: 'Volume (Weight × Reps)',
                marker: { color: 'rgba(50,171,96,0.6)' }
            };

            let layout2 = {
                title: {
                    text: `Training Volume for ${exercise}`,
                    font: { size: 14 }
                },
                xaxis: { 
                    title: { text: "Date", font: { size: 12 } },
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: "Volume (Weight × Reps)", font: { size: 12 } },
                    tickfont: { size: 10 }
                },
                margin: { l: 50, r: 30, t: 60, b: 50 }, // Increased top margin to 60px
                autosize: true,
                // modebar: { orientation: 'v' } // Move modebar to the side
            };

            Plotly.newPlot('plot_volume', [volumeTrace], layout2, { displayModeBar: false });
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Ensure chart updates dynamically
document.getElementById("exercise").addEventListener("change", updateChart);
document.getElementById("window").addEventListener("input", updateChart);

// Handle chart resize for responsiveness
window.addEventListener('resize', function () {
    Plotly.Plots.resize(document.getElementById('plot_progression'));
    Plotly.Plots.resize(document.getElementById('plot_volume'));
});
