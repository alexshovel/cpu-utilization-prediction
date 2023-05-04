// used for example purposes
function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// create initial empty chart
var ctx_live = document.getElementById("mycanvas");

const DATA_COUNT = 4;
var CURRENT_STEP = 0;
const labels = [];
const Utils = ChartUtils.init();
for (let i = 0; i < DATA_COUNT; ++i) {
  labels.push(i.toString());
}

//const datapoints = [0, 20, 20, 60, 60, 120, NaN, 180, 120, 125, 105, 110, 170];
const datapoints = [...Array(600/DATA_COUNT).keys()];

const data = {
  labels: labels,
  datasets: [
    {
      label: 'Текущее значение ',
      data: [],
      borderColor: Utils.CHART_COLORS.red,
      fill: false,
      cubicInterpolationMode: 'monotone',
      tension: 0.4
    }, {
      label: 'Прогноз на 30 секунд',
      data: [],
      borderColor: Utils.CHART_COLORS.blue,
      fill: false,
      tension: 0.4
    }, {
      label: 'Прогноз на 60 секунд ',
      data: [],
      borderColor: Utils.CHART_COLORS.green,
      fill: false
    }, {
      label: 'Прогноз на 300 секунд ',
      data: [],
      borderColor: Utils.CHART_COLORS.yellow,
      fill: false
    }
  ]
};

var config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'График прогноза нагрузки на CPU'
        },
      },
      interaction: {
        intersect: false,
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Value'
          },
          suggestedMin: 0,
          suggestedMax: 500
        }
      }
    },
};

var myChart = new Chart(ctx_live, config);

// logic to get new data
var getData = function() {
  $.ajax({
    url: 'http://194.35.127.114:49800/api/cpu',
    success: function(data) {
      //myChart.data.labels[CURRENT_STEP]="Замер" + CURRENT_STEP;
      myChart.data.datasets[0].data[CURRENT_STEP] = data.current_cpu;
      myChart.data.datasets[1].data[CURRENT_STEP+2] = data.predictions['30s'];
      if (CURRENT_STEP+4 >= DATA_COUNT) {
        myChart.data.labels[CURRENT_STEP+4]=CURRENT_STEP+4;
        //myChart.data.datasets[0].data.push(0);
        //myChart.data.datasets[1].data.push(0);
        //myChart.data.datasets[2].data.push(0);
      }
      //myChart.data.datasets[3].data[CURRENT_STEP+10] = data.predictions['300s'];
      myChart.data.datasets[2].data[CURRENT_STEP+4] = data.predictions['60s'];
      CURRENT_STEP++;
      myChart.update();
    }
  });
};

setInterval(getData, 15000);
// setInterval(getData, 3000);
