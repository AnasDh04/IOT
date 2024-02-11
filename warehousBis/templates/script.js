// // Assuming you have real temperature data, for example:
// const temperatureData = {
//     labels: ["9AM", "10AM", "11AM", "12PM", "1PM", "2PM"], // This would be your time data
//     datasets: [{
//       label: 'Temperature',
//       backgroundColor: 'rgb(255, 99, 132)',
//       borderColor: 'rgb(255, 99, 132)',
//       data: [22, 24, 21, 25, 23, 22], // This would be your temperature data
//     }]
//   };
  
//   const configTemperature = {
//     type: 'line',
//     data: temperatureData,
//     options: {}
//   };
  
  window.onload = function() {
    fetch('/api/get_temperature_data') // Use the correct path to your Django view
      .then(response => response.json())
      .then(data => {
        var ctxTemperature = document.getElementById('temperatureGraph').getContext('2d');
        new Chart(ctxTemperature, {
          type: 'line',
          data: data,
          options: {}
        });
      })
      .catch(error => console.error('Error fetching temperature data:', error));
  };
  
  