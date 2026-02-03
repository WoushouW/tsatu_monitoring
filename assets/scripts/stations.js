// Сторінка станцій - відображення карток станцій з фільтрами
let allStations = [];
let filteredStations = [];

document.addEventListener('DOMContentLoaded', () => {
    loadStations();
    setupFilters();
});

async function loadStations() {
    try {
        const response = await fetch('/api/stations');
        const data = await response.json();
        
        if (data.success) {
            allStations = data.stations;
            filteredStations = [...allStations];
            displayStations(filteredStations);
        }
    } catch (error) {
        console.error('Помилка завантаження станцій:', error);
        document.getElementById('stations-container').innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Помилка завантаження даних</p>
            </div>
        `;
    }
}

function displayStations(stations) {
    const container = document.getElementById('stations-container');
    
    if (stations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <p>Станції не знайдено</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = stations.map(station => {
        const mountingTag = station.mounting_type === 'rooftop' ? 
            '<span class="tag rooftop"><i class="fas fa-home"></i> Дахова</span>' :
            '<span class="tag ground"><i class="fas fa-mountain"></i> Наземна</span>';
        
        return `
            <div class="station-card">
                <div class="station-header">
                    <div class="station-title">
                        <h3>${station.station_name}</h3>
                        <p><i class="fas fa-map-marker-alt"></i> ${station.location}</p>
                    </div>
                    <div class="station-icon">
                        <i class="fas fa-solar-panel"></i>
                    </div>
                </div>
                
                <div class="station-details">
                    <div class="detail-item">
                        <span class="detail-label">Потужність</span>
                        <span class="detail-value">${station.total_capacity_kw} кВт</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Панелі</span>
                        <span class="detail-value">${station.panel_count} шт</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Тип панелей</span>
                        <span class="detail-value">${station.panel_type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Інвертори</span>
                        <span class="detail-value">${station.inverter_brand}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Введено в експлуатацію</span>
                        <span class="detail-value">${station.commissioning_date}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Моніторинг</span>
                        <span class="detail-value">${station.monitoring_system}</span>
                    </div>
                </div>
                
                <div class="station-tags">
                    ${mountingTag}
                    <span class="tag monitoring"><i class="fas fa-desktop"></i> ${station.monitoring_system}</span>
                </div>
            </div>
        `;
    }).join('');
}

function setupFilters() {
    const searchInput = document.getElementById('search-input');
    const filterMounting = document.getElementById('filter-mounting');
    const filterMonitoring = document.getElementById('filter-monitoring');
    
    searchInput.addEventListener('input', applyFilters);
    filterMounting.addEventListener('change', applyFilters);
    filterMonitoring.addEventListener('change', applyFilters);
}

function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const mountingType = document.getElementById('filter-mounting').value;
    const monitoringSystem = document.getElementById('filter-monitoring').value;
    
    filteredStations = allStations.filter(station => {
        // Пошук
        const matchesSearch = !searchTerm || 
            station.station_name.toLowerCase().includes(searchTerm) ||
            station.location.toLowerCase().includes(searchTerm);
        
        // Фільтр за типом монтажу
        const matchesMounting = mountingType === 'all' || station.mounting_type === mountingType;
        
        // Фільтр за системою моніторингу
        const matchesMonitoring = monitoringSystem === 'all' || station.monitoring_system === monitoringSystem;
        
        return matchesSearch && matchesMounting && matchesMonitoring;
    });
    
    displayStations(filteredStations);
}
