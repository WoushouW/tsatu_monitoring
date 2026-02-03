// Головна сторінка - завантаження статистики
document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
});

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        if (data.success) {
            // Оновлення статистики
            document.getElementById('total-stations').textContent = data.total_stations;
            document.getElementById('total-capacity').textContent = `${data.total_capacity_kw} кВт`;
            document.getElementById('total-locations').textContent = data.total_locations;
            document.getElementById('total-systems').textContent = data.total_monitoring_systems;
            
            // Оновлення hero секції
            if (document.getElementById('hero-capacity')) {
                document.getElementById('hero-capacity').textContent = data.total_capacity_kw;
            }
            if (document.getElementById('hero-locations')) {
                document.getElementById('hero-locations').textContent = data.total_locations;
            }
            if (document.getElementById('hero-stations')) {
                document.getElementById('hero-stations').textContent = data.total_stations;
            }
        }
    } catch (error) {
        console.error('Помилка завантаження статистики:', error);
    }
}
