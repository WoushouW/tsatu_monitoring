"""
Веб-додаток для моніторингу сонячних електростанцій
"""
from flask import Flask, render_template, jsonify, request, send_file
from data_parser import get_all_stations, get_station_by_id, get_statistics, get_production_data, get_available_date_range
from datetime import datetime, timedelta
import io
import csv

app = Flask(__name__, 
            template_folder='pages',
            static_folder='assets')

app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    """Головна сторінка з цікавим контентом"""
    return render_template('index.html')

@app.route('/stations')
def stations():
    """Сторінка з інформацією про станції"""
    return render_template('stations.html')

@app.route('/charts')
def charts():
    """Сторінка з графіками"""
    return render_template('charts.html')

@app.route('/api/stations')
def api_stations():
    """API: список всіх станцій"""
    stations = get_all_stations()
    return jsonify({
        'success': True,
        'count': len(stations),
        'stations': stations
    })

@app.route('/api/station/<station_id>')
def api_station(station_id):
    """API: дані конкретної станції"""
    station = get_station_by_id(station_id)
    if station:
        return jsonify({
            'success': True,
            'station': station
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Станція не знайдена'
        }), 404

@app.route('/api/production')
def api_production():
    """API: дані виробітку для станцій за період"""
    station_ids = request.args.get('stations', '').split(',')
    station_ids = [sid.strip() for sid in station_ids if sid.strip()]
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Парсинг дат
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Невірний формат дати'
        }), 400
    
    # Отримання даних
    if not station_ids:
        station_ids = None
    
    production_data = get_production_data(station_ids, start_date, end_date)
    
    return jsonify({
        'success': True,
        'data': production_data,
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    })

@app.route('/api/date-range')
def api_date_range():
    """API: доступний діапазон дат"""
    date_range = get_available_date_range()
    return jsonify({
        'success': True,
        **date_range
    })

@app.route('/api/statistics')
def api_statistics():
    """API: загальна статистика"""
    stats = get_statistics()
    return jsonify({
        'success': True,
        **stats
    })

@app.route('/api/export/excel')
def export_excel():
    """Експорт даних у Excel (CSV)"""
    station_ids = request.args.get('stations', '').split(',')
    station_ids = [sid.strip() for sid in station_ids if sid.strip()]
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
    except ValueError:
        return jsonify({'error': 'Невірний формат дати'}), 400
    
    if not station_ids:
        return jsonify({'error': 'Не вказано станції'}), 400
    
    # Отримання даних
    production_data = get_production_data(station_ids, start_date, end_date)
    stations = get_all_stations()
    station_map = {s['station_id']: s for s in stations}
    
    # Створення CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовок
    writer.writerow(['Звіт виробітку сонячних електростанцій'])
    writer.writerow([f'Період: {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'])
    writer.writerow([])
    
    for station_id in station_ids:
        if station_id not in production_data or station_id not in station_map:
            continue
        
        station = station_map[station_id]
        data = production_data[station_id]
        
        # Дані станції
        writer.writerow([f'{station["station_name"]} - {station["location"]}'])
        writer.writerow(['Потужність (кВт)', station['total_capacity_kw']])
        writer.writerow([])
        
        # Таблиця даних
        writer.writerow(['Дата', 'Виробництво (кВт·год)'])
        
        total_production = 0
        for entry in data:
            writer.writerow([entry['date'], entry['production_kwh']])
            total_production += entry['production_kwh']
        
        writer.writerow(['ЗАГАЛОМ:', total_production])
        writer.writerow([])
        writer.writerow([])
    
    # Повернення файлу
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'ses_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
