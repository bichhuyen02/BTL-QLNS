function cateChart(labels, data, colors, borderColors) {
  const ctx = document.getElementById('cateChart');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: 'Thống kê số sản phẩm theo danh mục',
        data: data,
        borderWidth: 1,
        backgroundColor: colors,
        borderColor: borderColors
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

function revenueChart(labels, data, colors, borderColors) {
  const ctx = document.getElementById('revenueChart');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Thống kê doanh thu',
        data: data,
        borderWidth: 1,
        backgroundColor: colors,
        borderColor: borderColors
      }],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}