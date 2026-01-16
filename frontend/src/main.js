import './style.css'
import Chart from 'chart.js/auto'

const API_BASE = 'http://127.0.0.1:5000/api';

let chartInstance = null;

async function init() {
  console.log("Initializing GreenGrid Dashboard...");
  setupEventListeners();
  await fetchAndRenderChart();
  await fetchRecommendations();
}

function setupEventListeners() {
  const tempSlider = document.getElementById('tempSlider');
  const tempValue = document.getElementById('tempValue');
  const hourSlider = document.getElementById('hourSlider');
  const hourValue = document.getElementById('hourValue');
  const predictBtn = document.getElementById('predictBtn');

  tempSlider.addEventListener('input', (e) => {
    tempValue.textContent = `${e.target.value}°C`;
  });

  hourSlider.addEventListener('input', (e) => {
    hourValue.textContent = `${e.target.value}:00`;
  });

  predictBtn.addEventListener('click', runPrediction);
  document.getElementById('optimizeBtn').addEventListener('click', optimizeGrid);
}

async function fetchAndRenderChart() {
  try {
    const response = await fetch(`${API_BASE}/usage`);
    const data = await response.json();

    const labels = data.map(d => d.hour);
    const usages = data.map(d => d.usage);
    const temps = data.map(d => d.temperature);

    renderChart(labels, usages, temps);
  } catch (error) {
    console.error("Error fetching usage data:", error);
  }
}

function renderChart(labels, usageData, tempData) {
  const ctx = document.getElementById('energyChart').getContext('2d');

  if (chartInstance) {
    chartInstance.destroy();
  }

  // Create gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(16, 185, 129, 0.5)'); // Primary color opacity
  gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Energy Usage (kWh)',
          data: usageData,
          borderColor: '#10b981',
          backgroundColor: gradient,
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#10b981'
        },
        {
          label: 'Temperature (°C)',
          data: tempData,
          borderColor: '#3b82f6',
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          labels: { color: '#94a3b8' }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8' }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#3b82f6' }
        }
      }
    }
  });
}

async function runPrediction() {
  const temp = document.getElementById('tempSlider').value;
  const hour = document.getElementById('hourSlider').value;

  const btn = document.getElementById('predictBtn');
  const output = document.getElementById('predictedLoad');

  btn.textContent = "Simulating...";
  btn.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hour: hour,
        temperature: temp,
        is_weekend: 0
      })
    });

    const result = await response.json();
    output.textContent = `${result.predicted_usage} kWh`;

    // Highlight effect
    output.style.color = '#fff';
    setTimeout(() => output.style.color = '#10b981', 300);

    // Also fetch system status
    updateSystemStatus(hour, temp);

  } catch (error) {
    console.error("Prediction error:", error);
    output.textContent = "Error";
  } finally {
    btn.textContent = "Run Simulation";
    btn.disabled = false;
  }
}

async function fetchRecommendations() {
  try {
    const response = await fetch(`${API_BASE}/recommendations`);
    const data = await response.json();
    const container = document.getElementById('recommendationsList');

    container.innerHTML = data.recommendations.map(rec => `
      <div class="rec-card ${rec.category}">
        <div class="category-tag">${rec.category}</div>
        <p>${rec.text}</p>
      </div>
    `).join('');

  } catch (error) {
    console.error("Error fetching recommendations:", error);
  }
}

async function updateSystemStatus(hour, temp) {
  try {
    const response = await fetch(`${API_BASE}/system_status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hour: hour, temperature: temp })
    });
    const status = await response.json();

    const setBadge = (id, state) => {
      const el = document.getElementById(id);
      el.textContent = state;
      el.className = `badge ${state === 'ON' ? 'ON' : 'OFF'}`;
    };

    setBadge('lightStatus', status.streetlights);
    setBadge('acStatus', status.ac_system);

  } catch (error) {
    console.error("Status error:", error);
  }
}

async function optimizeGrid() {
  const btn = document.getElementById('optimizeBtn');
  const originalText = btn.textContent;
  btn.textContent = "Optimizing...";

  try {
    const response = await fetch(`${API_BASE}/optimize`, { method: 'POST' });
    const result = await response.json();

    alert(`Grid Optimized!\nSavings: ${result.savings_estimated}\nActions:\n- ${result.actions.join('\n- ')}`);

  } catch (error) {
    alert("Optimization failed");
  } finally {
    btn.textContent = originalText;
  }
}

init();
