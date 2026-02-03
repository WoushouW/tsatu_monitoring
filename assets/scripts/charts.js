// Сторінка графіків з виправленою логікою дат
let allStations = [];
let selectedStations = [];
let productionChart = null;
let currentPeriod = 30;
let customDateRange = null;
let availableDateRange = null;

// Кольори для графіків
const CHART_COLORS = [
    '#4a90e2', '#50c878', '#f39c12', '#e74c3c', '#9b59b6',
    '#3498db', '#2ecc71', '#f1c40f', '#e67e22', '#1abc9c',
    '#34495e', '#16a085', '#27ae60', '#2980b9', '#8e44ad',
    '#c0392b'
];

// Завантаження при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    loadDateRange();
    loadStationsList();
    setupPeriodSelector();
    setupCustomDateRange();
    setupExportButtons();
    initializeChart();
});

// Завантаження доступного діапазону дат
async function loadDateRange() {
    try {
        const response = await fetch('/api/date-range');
        const data = await response.json();
        
        if (data.success) {
            availableDateRange = {
                min: data.min_date,
                max: data.max_date
            };
            
            // Налаштування обмежень для date input
            const startDateInput = document.getElementById('start-date');
            const endDateInput = document.getElementById('end-date');
            
            startDateInput.min = availableDateRange.min;
            startDateInput.max = availableDateRange.max;
            endDateInput.min = availableDateRange.min;
            endDateInput.max = availableDateRange.max;
            
            // Встановлення початкових значень
            startDateInput.value = calculateStartDate(currentPeriod);
            endDateInput.value = availableDateRange.max;
            
            console.log('Доступний діапазон дат:', availableDateRange);
        }
    } catch (error) {
        console.error('Помилка завантаження діапазону дат:', error);
    }
}

// Розрахунок дати початку на основі періоду (від останньої доступної дати)
function calculateStartDate(days) {
    if (!availableDateRange) {
        return null;
    }
    
    const endDate = new Date(availableDateRange.max);
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - days + 1);
    
    // Перевірка, чи не виходить за мінімальну дату
    const minDate = new Date(availableDateRange.min);
    if (startDate < minDate) {
        return availableDateRange.min;
    }
    
    return startDate.toISOString().split('T')[0];
}

// Завантаження списку станцій
async function loadStationsList() {
    try {
        const response = await fetch('/api/stations');
        const data = await response.json();
        
        if (data.success) {
            allStations = data.stations;
            displayStationsList(data.stations);
        }
    } catch (error) {
        console.error('Помилка завантаження списку:', error);
    }
}

// Відображення списку станцій з чекбоксами
function displayStationsList(stations) {
    const listContainer = document.getElementById('stations-list');
    
    listContainer.innerHTML = stations.map((station, index) => {
        return `
            <div class="station-list-item" data-station-id="${station.station_id}">
                <input type="checkbox" 
                       id="station-${station.station_id}" 
                       value="${station.station_id}"
                       onchange="toggleStation('${station.station_id}')">
                <label for="station-${station.station_id}">
                    <strong>${station.station_name}</strong>
                    <span>${station.location}</span>
                </label>
            </div>
        `;
    }).join('');
    
    // Кнопки "Вибрати всі" та "Очистити"
    document.getElementById('select-all-btn').addEventListener('click', selectAllStations);
    document.getElementById('clear-all-btn').addEventListener('click', clearAllStations);
}

// Вибрати всі станції
function selectAllStations() {
    selectedStations = allStations.map(s => s.station_id);
    updateCheckboxes();
    loadProductionData();
}

// Очистити вибір
function clearAllStations() {
    selectedStations = [];
    updateCheckboxes();
    clearChart();
    updateExportButtons();
}

// Оновлення чекбоксів
function updateCheckboxes() {
    allStations.forEach(station => {
        const checkbox = document.getElementById(`station-${station.station_id}`);
        const item = document.querySelector(`[data-station-id="${station.station_id}"]`);
        
        if (checkbox) {
            checkbox.checked = selectedStations.includes(station.station_id);
            
            if (checkbox.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        }
    });
}

// Перемикання станції
function toggleStation(stationId) {
    const index = selectedStations.indexOf(stationId);
    
    if (index > -1) {
        selectedStations.splice(index, 1);
    } else {
        selectedStations.push(stationId);
    }
    
    updateCheckboxes();
    
    if (selectedStations.length > 0) {
        loadProductionData();
    } else {
        clearChart();
    }
    
    updateExportButtons();
}

// Завантаження даних виробітку
async function loadProductionData() {
    const chartInfo = document.getElementById('chart-info');
    chartInfo.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Завантаження даних...</p>';
    
    try {
        // Визначення періоду
        let startDate, endDate;
        
        if (customDateRange) {
            startDate = customDateRange.start;
            endDate = customDateRange.end;
        } else {
            endDate = availableDateRange.max;
            startDate = calculateStartDate(currentPeriod);
        }
        
        // Запит даних
        const stationsParam = selectedStations.join(',');
        const response = await fetch(`/api/production?stations=${stationsParam}&start_date=${startDate}&end_date=${endDate}`);
        const data = await response.json();
        
        if (data.success) {
            chartInfo.innerHTML = `<p><i class="fas fa-check-circle"></i> Вибрано станцій: ${selectedStations.length} | Період: ${data.period.start} - ${data.period.end}</p>`;
            updateChart(data.data);
        } else {
            chartInfo.innerHTML = '<p><i class="fas fa-exclamation-triangle"></i> Помилка завантаження даних</p>';
        }
    } catch (error) {
        console.error('Помилка завантаження даних:', error);
        chartInfo.innerHTML = '<p><i class="fas fa-exclamation-triangle"></i> Помилка завантаження даних</p>';
    }
}

// Оновлення графіка
function updateChart(productionData) {
    // Збір всіх унікальних дат
    const allDates = new Set();
    Object.values(productionData).forEach(stationData => {
        stationData.forEach(entry => allDates.add(entry.date));
    });
    
    const sortedDates = Array.from(allDates).sort();
    
    // Підготовка datasets для кожної станції
    const datasets = selectedStations.map((stationId, index) => {
        const station = allStations.find(s => s.station_id === stationId);
        const stationData = productionData[stationId] || [];
        
        // Створення мапи дата -> виробництво
        const dataMap = {};
        stationData.forEach(entry => {
            dataMap[entry.date] = entry.production_kwh;
        });
        
        // Масив даних для графіка
        const chartData = sortedDates.map(date => dataMap[date] || 0);
        
        return {
            label: station ? station.station_name : stationId,
            data: chartData,
            borderColor: CHART_COLORS[index % CHART_COLORS.length],
            backgroundColor: CHART_COLORS[index % CHART_COLORS.length] + '20',
            borderWidth: 2,
            tension: 0.4,
            fill: true
        };
    });
    
    // Оновлення або створення графіка
    if (productionChart) {
        productionChart.data.labels = sortedDates;
        productionChart.data.datasets = datasets;
        productionChart.update();
    } else {
        const ctx = document.getElementById('production-chart').getContext('2d');
        productionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedDates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y.toFixed(2) + ' кВт·год';
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Виробництво (кВт·год)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(0);
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Дата'
                        }
                    }
                }
            }
        });
    }
}

// Очищення графіка
function clearChart() {
    if (productionChart) {
        productionChart.data.labels = [];
        productionChart.data.datasets = [];
        productionChart.update();
    }
    
    document.getElementById('chart-info').innerHTML = '<p><i class="fas fa-info-circle"></i> Виберіть станції для відображення даних</p>';
}

// Ініціалізація графіка
function initializeChart() {
    const ctx = document.getElementById('production-chart').getContext('2d');
    productionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Налаштування вибору періоду
function setupPeriodSelector() {
    const periodButtons = document.querySelectorAll('.period-btn');
    
    periodButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Видалення активного класу
            periodButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Скидання кастомного періоду
            customDateRange = null;
            
            // Встановлення періоду
            currentPeriod = parseInt(btn.dataset.period);
            
            // Оновлення полів дат
            if (availableDateRange) {
                const startDate = calculateStartDate(currentPeriod);
                document.getElementById('start-date').value = startDate;
                document.getElementById('end-date').value = availableDateRange.max;
            }
            
            // Перезавантаження даних
            if (selectedStations.length > 0) {
                loadProductionData();
            }
        });
    });
}

// Налаштування кастомного діапазону
function setupCustomDateRange() {
    const applyBtn = document.getElementById('apply-custom-period');
    
    applyBtn.addEventListener('click', () => {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        if (!startDate || !endDate) {
            alert('Будь ласка, виберіть обидві дати');
            return;
        }
        
        if (startDate > endDate) {
            alert('Дата початку не може бути пізніше дати кінця');
            return;
        }
        
        // Встановлення кастомного періоду
        customDateRange = {
            start: startDate,
            end: endDate
        };
        
        // Видалення активного класу з кнопок періоду
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Перезавантаження даних
        if (selectedStations.length > 0) {
            loadProductionData();
        }
    });
}

// Налаштування кнопок експорту
function setupExportButtons() {
    const exportExcelBtn = document.getElementById('export-excel');
    
    exportExcelBtn.addEventListener('click', () => {
        if (selectedStations.length === 0) {
            alert('Будь ласка, виберіть хоча б одну станцію');
            return;
        }
        
        // Визначення періоду
        let startDate, endDate;
        
        if (customDateRange) {
            startDate = customDateRange.start;
            endDate = customDateRange.end;
        } else {
            endDate = availableDateRange.max;
            startDate = calculateStartDate(currentPeriod);
        }
        
        // Формування URL для експорту
        const stationsParam = selectedStations.join(',');
        const url = `/api/export/excel?stations=${stationsParam}&start_date=${startDate}&end_date=${endDate}`;
        
        // Завантаження файлу
        window.location.href = url;
    });
}

// Оновлення стану кнопок експорту
function updateExportButtons() {
    const exportExcelBtn = document.getElementById('export-excel');
    
    if (selectedStations.length > 0) {
        exportExcelBtn.disabled = false;
    } else {
        exportExcelBtn.disabled = true;
    }
}
