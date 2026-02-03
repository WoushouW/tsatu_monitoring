"""
Модуль для отримання даних з Google Sheets
ВИПРАВЛЕНО: читає дані з горизонтального формату (дати в стовпцях D, E, F...)
"""
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Налаштування API
API_KEY = os.getenv('GOOGLE_API_KEY')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Резервні дані станцій (ТІЛЬКИ якщо Google Sheets недоступний)
# Дані з таблиці: 16 станцій, загальна потужність 4230 кВт
FALLBACK_STATIONS = [
    {'station_id': 'SS001', 'station_name': 'СЕС Бориспіль-1', 'station_pair': 'A', 'location': 'Київська обл., Бориспіль', 'latitude': 50.3547, 'longitude': 30.9508, 'commissioning_date': '2019-05-15', 'total_capacity_kw': 250.0, 'panel_type': 'JA Solar', 'panel_power_w': 450, 'panel_count': 556, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-100KTL-M1', 'inverter_count': 3, 'inverter_power_kw': 100.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS002', 'station_name': 'СЕС Бориспіль-2', 'station_pair': 'A', 'location': 'Київська обл., Бориспіль', 'latitude': 50.3612, 'longitude': 30.9621, 'commissioning_date': '2019-06-20', 'total_capacity_kw': 280.0, 'panel_type': 'Longi', 'panel_power_w': 455, 'panel_count': 615, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-100KTL-M1', 'inverter_count': 3, 'inverter_power_kw': 100.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS003', 'station_name': 'СЕС Вінниця-1', 'station_pair': 'B', 'location': 'Вінницька обл., Вінниця', 'latitude': 49.8397, 'longitude': 24.0297, 'commissioning_date': '2019-08-10', 'total_capacity_kw': 150.0, 'panel_type': 'Trina Solar', 'panel_power_w': 400, 'panel_count': 375, 'inverter_brand': 'SMA', 'inverter_model': 'Sunny Tripower 50', 'inverter_count': 3, 'inverter_power_kw': 50.0, 'mounting_type': 'rooftop', 'monitoring_system': 'SMA Sunny Portal'},
    {'station_id': 'SS004', 'station_name': 'СЕС Вінниця-2', 'station_pair': 'B', 'location': 'Вінницька обл., Вінниця', 'latitude': 49.7245, 'longitude': 23.9108, 'commissioning_date': '2019-09-25', 'total_capacity_kw': 180.0, 'panel_type': 'Canadian Solar', 'panel_power_w': 420, 'panel_count': 429, 'inverter_brand': 'SMA', 'inverter_model': 'Sunny Tripower 60', 'inverter_count': 3, 'inverter_power_kw': 60.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'SMA Sunny Portal'},
    {'station_id': 'SS005', 'station_name': 'СЕС Дніпро-1', 'station_pair': 'C', 'location': 'Дніпропетровська обл., Дніпро', 'latitude': 48.4647, 'longitude': 35.0462, 'commissioning_date': '2020-03-12', 'total_capacity_kw': 400.0, 'panel_type': 'JA Solar', 'panel_power_w': 500, 'panel_count': 800, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-215KTL-H0', 'inverter_count': 2, 'inverter_power_kw': 215.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS006', 'station_name': 'СЕС Дніпро-2', 'station_pair': 'C', 'location': 'Дніпропетровська обл., Дніпро', 'latitude': 48.6283, 'longitude': 35.2536, 'commissioning_date': '2020-04-18', 'total_capacity_kw': 450.0, 'panel_type': 'Longi', 'panel_power_w': 520, 'panel_count': 865, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-215KTL-H0', 'inverter_count': 2, 'inverter_power_kw': 215.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS007', 'station_name': 'СЕС Харків-1', 'station_pair': 'D', 'location': 'Харківська обл., Харків', 'latitude': 49.9935, 'longitude': 36.2304, 'commissioning_date': '2020-05-22', 'total_capacity_kw': 320.0, 'panel_type': 'Trina Solar', 'panel_power_w': 480, 'panel_count': 667, 'inverter_brand': 'Fronius', 'inverter_model': 'Fronius Symo 100', 'inverter_count': 4, 'inverter_power_kw': 100.0, 'mounting_type': 'rooftop', 'monitoring_system': 'Fronius Solar.web'},
    {'station_id': 'SS008', 'station_name': 'СЕС Харків-2', 'station_pair': 'D', 'location': 'Харківська обл., Харків', 'latitude': 49.8211, 'longitude': 36.0528, 'commissioning_date': '2020-07-14', 'total_capacity_kw': 350.0, 'panel_type': 'JA Solar', 'panel_power_w': 500, 'panel_count': 700, 'inverter_brand': 'Fronius', 'inverter_model': 'Fronius Symo 100', 'inverter_count': 4, 'inverter_power_kw': 100.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Fronius Solar.web'},
    {'station_id': 'SS009', 'station_name': 'СЕС Одеса-1', 'station_pair': 'E', 'location': 'Одеська обл., Одеса', 'latitude': 46.4825, 'longitude': 30.7233, 'commissioning_date': '2020-09-05', 'total_capacity_kw': 200.0, 'panel_type': 'Canadian Solar', 'panel_power_w': 440, 'panel_count': 455, 'inverter_brand': 'SolarEdge', 'inverter_model': 'SE100K', 'inverter_count': 2, 'inverter_power_kw': 100.0, 'mounting_type': 'rooftop', 'monitoring_system': 'SolarEdge Monitoring'},
    {'station_id': 'SS010', 'station_name': 'СЕС Одеса-2', 'station_pair': 'E', 'location': 'Одеська обл., Одеса', 'latitude': 46.2983, 'longitude': 30.6597, 'commissioning_date': '2020-10-20', 'total_capacity_kw': 220.0, 'panel_type': 'Longi', 'panel_power_w': 450, 'panel_count': 489, 'inverter_brand': 'SolarEdge', 'inverter_model': 'SE110K', 'inverter_count': 2, 'inverter_power_kw': 110.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'SolarEdge Monitoring'},
    {'station_id': 'SS011', 'station_name': 'СЕС Запоріжжя-1', 'station_pair': 'F', 'location': 'Запорізька обл., Запоріжжя', 'latitude': 47.8388, 'longitude': 35.1396, 'commissioning_date': '2021-02-15', 'total_capacity_kw': 500.0, 'panel_type': 'JA Solar', 'panel_power_w': 550, 'panel_count': 909, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-215KTL-H0', 'inverter_count': 3, 'inverter_power_kw': 215.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS012', 'station_name': 'СЕС Запоріжжя-2', 'station_pair': 'F', 'location': 'Запорізька обл., Запоріжжя', 'latitude': 46.8489, 'longitude': 35.3675, 'commissioning_date': '2021-03-28', 'total_capacity_kw': 480.0, 'panel_type': 'Longi', 'panel_power_w': 530, 'panel_count': 906, 'inverter_brand': 'Huawei', 'inverter_model': 'SUN2000-185KTL-H0', 'inverter_count': 3, 'inverter_power_kw': 185.0, 'mounting_type': 'ground-mounted', 'monitoring_system': 'Huawei FusionSolar'},
    {'station_id': 'SS013', 'station_name': 'СЕС Хмельницький-1', 'station_pair': 'G', 'location': 'Хмельницька обл., Хмельницький', 'latitude': 49.2331, 'longitude': 28.4682, 'commissioning_date': '2021-05-10', 'total_capacity_kw': 120.0, 'panel_type': 'Trina Solar', 'panel_power_w': 410, 'panel_count': 293, 'inverter_brand': 'SMA', 'inverter_model': 'Sunny Tripower 40', 'inverter_count': 3, 'inverter_power_kw': 40.0, 'mounting_type': 'rooftop', 'monitoring_system': 'SMA Sunny Portal'},
    {'station_id': 'SS014', 'station_name': 'СЕС Хмельницький-2', 'station_pair': 'G', 'location': 'Хмельницька обл., Хмельницький', 'latitude': 49.5564, 'longitude': 27.9558, 'commissioning_date': '2021-06-18', 'total_capacity_kw': 140.0, 'panel_type': 'Canadian Solar', 'panel_power_w': 430, 'panel_count': 326, 'inverter_brand': 'SMA', 'inverter_model': 'Sunny Tripower 50', 'inverter_count': 3, 'inverter_power_kw': 50.0, 'mounting_type': 'rooftop', 'monitoring_system': 'SMA Sunny Portal'},
    {'station_id': 'SS015', 'station_name': 'СЕС Полтава-1', 'station_pair': 'H', 'location': 'Полтавська обл., Полтава', 'latitude': 49.5883, 'longitude': 34.5514, 'commissioning_date': '2021-07-22', 'total_capacity_kw': 90.0, 'panel_type': 'JA Solar', 'panel_power_w': 420, 'panel_count': 214, 'inverter_brand': 'Fronius', 'inverter_model': 'Fronius Symo 30', 'inverter_count': 3, 'inverter_power_kw': 30.0, 'mounting_type': 'rooftop', 'monitoring_system': 'Fronius Solar.web'},
    {'station_id': 'SS016', 'station_name': 'СЕС Полтава-2', 'station_pair': 'H', 'location': 'Полтавська обл., Полтава', 'latitude': 49.0669, 'longitude': 33.4239, 'commissioning_date': '2021-08-30', 'total_capacity_kw': 100.0, 'panel_type': 'Longi', 'panel_power_w': 440, 'panel_count': 227, 'inverter_brand': 'Fronius', 'inverter_model': 'Fronius Symo 35', 'inverter_count': 3, 'inverter_power_kw': 35.0, 'mounting_type': 'rooftop', 'monitoring_system': 'Fronius Solar.web'}
]

# Резервні дані виробітку (з датами 2021-2024)
def generate_fallback_production():
    """Генерує резервні дані виробітку з реальними датами (4 роки)"""
    start_date = datetime(2021, 10, 11)
    end_date = datetime(2024, 10, 10)
    
    production_data = {}
    
    for station in FALLBACK_STATIONS:
        station_id = station['station_id']
        capacity = station['total_capacity_kw']
        
        daily_records = []
        current_date = start_date
        
        while current_date <= end_date:
            # Генерація реалістичних даних виробітку (сума всіх інверторів)
            # Потужність / 3 інвертори * 4.5 год = виробіток на інвертор
            # Приклад: 250кВт/3 * 4.5год = 375 кВт·год на інвертор → сума ~1125кВт·год
            # Але у таблиці значення ~100-120 на інвертор → сума ~330кВт·год
            base_production = capacity * 1.3  # 1.3 години піку (реалістичніше)
            variation = (hash(f"{station_id}{current_date}") % 40) - 20
            production = base_production + variation
            
            daily_records.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'production_kwh': round(production, 2)
            })
            
            current_date += timedelta(days=1)
        
        production_data[station_id] = daily_records
    
    return production_data

FALLBACK_PRODUCTION = generate_fallback_production()


def get_all_stations():
    """Отримує список всіх станцій з Google Sheets або резервних даних"""
    if not API_KEY or not SPREADSHEET_ID:
        print("⚠ Використовуються резервні дані станцій")
        return FALLBACK_STATIONS
    
    try:
        service = build('sheets', 'v4', developerKey=API_KEY)
        sheet = service.spreadsheets()
        
        # Читання даних з листа "Станции и оборудование"
        # Структура: A-R (до колонки R включно)
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Станции и оборудование'!A2:R100"
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("⚠ Дані не знайдено, використовуються резервні")
            return FALLBACK_STATIONS
        
        stations = []
        for row in values:
            if len(row) >= 13:
                try:
                    station = {
                        'station_id': row[0],                                          # Колонка A
                        'station_name': row[1],                                        # Колонка B
                        'station_pair': row[2] if len(row) > 2 else '',                # Колонка C
                        'location': row[3] if len(row) > 3 else '',                    # Колонка D
                        'latitude': float(row[4].replace(',', '.')) if len(row) > 4 else 0.0,   # Колонка E
                        'longitude': float(row[5].replace(',', '.')) if len(row) > 5 else 0.0,  # Колонка F
                        'commissioning_date': row[6] if len(row) > 6 else '2021-01-01', # Колонка G
                        'total_capacity_kw': float(row[7]) if len(row) > 7 else 0.0,   # Колонка H
                        'panel_type': row[8] if len(row) > 8 else 'Generic',           # Колонка I
                        'panel_power_w': int(row[9]) if len(row) > 9 else 0,           # Колонка J
                        'panel_count': int(row[10]) if len(row) > 10 else 0,           # Колонка K
                        'inverter_brand': row[11] if len(row) > 11 else 'Generic',     # Колонка L
                        'inverter_model': row[12] if len(row) > 12 else 'Model',       # Колонка M
                        'inverter_count': int(row[13]) if len(row) > 13 else 0,        # Колонка N
                        'inverter_power_kw': float(row[14].replace(',', '.')) if len(row) > 14 else 0.0, # Колонка O
                        'mounting_type': row[15] if len(row) > 15 else 'rooftop',      # Колонка P
                        'monitoring_system': row[16] if len(row) > 16 else 'Generic'  # Колонка Q
                    }
                    stations.append(station)
                except (ValueError, IndexError) as e:
                    continue
        
        if stations:
            print(f"✓ Завантажено {len(stations)} станцій з Google Sheets")
            return stations
        else:
            print("⚠ Помилка парсингу, використовуються резервні дані")
            return FALLBACK_STATIONS
            
    except HttpError as e:
        print(f"⚠ Помилка API: {e}")
        return FALLBACK_STATIONS
    except Exception as e:
        print(f"⚠ Помилка завантаження: {e}")
        return FALLBACK_STATIONS


def get_production_data(station_ids=None, start_date=None, end_date=None):
    """
    Отримує дані виробітку для вибраних станцій за період
    ЛОГІКА: у колонці B листа "Виробіток енергії" шукаємо ВСІ рядки з SS001,
             знаходимо колонку з датою (2021-10-12) і сумуємо всі значення
    """
    if not API_KEY or not SPREADSHEET_ID:
        print("⚠ Використовуються резервні дані виробітку")
        return filter_production_data(FALLBACK_PRODUCTION, station_ids, start_date, end_date)
    
    try:
        service = build('sheets', 'v4', developerKey=API_KEY)
        sheet = service.spreadsheets()
        
        # КРОК 1: Читання заголовків (рядок 1) - дати в колонках D, E, F...
        # Лист: "Выработка энергии"
        header_result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Выработка энергии'!D1:ZZ1"  # Дати починаються з колонки D
        ).execute()
        
        header_values = header_result.get('values', [[]])[0]
        
        # Парсинг дат із заголовків
        date_columns = []  # [('2021-10-11', 3), ('2021-10-12', 4), ...] - (дата, індекс)
        for i, col_value in enumerate(header_values):
            if col_value:
                try:
                    # Спроба парсити дату
                    date_obj = datetime.strptime(col_value.strip(), '%Y-%m-%d')
                    date_columns.append((date_obj.strftime('%Y-%m-%d'), i + 3))  # i+3 тому що D=3
                except ValueError:
                    try:
                        # Альтернативний формат
                        date_obj = datetime.strptime(col_value.strip(), '%d.%m.%Y')
                        date_columns.append((date_obj.strftime('%Y-%m-%d'), i + 3))
                    except ValueError:
                        # Пропускаємо нерозпізнані дати
                        continue
        
        print(f"✓ Знайдено {len(date_columns)} дат в заголовку листа 'Выработка энергии'")
        
        # КРОК 2: Читання даних виробітку (починаючи з рядка 2)
        # Колонка B - station_id (SS001, SS002...)
        data_result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Выработка энергии'!A2:ZZ1000"  # Читаємо всі рядки
        ).execute()
        
        data_values = data_result.get('values', [])
        
        if not data_values:
            print("⚠ Дані виробітку не знайдено, використовуються резервні")
            return filter_production_data(FALLBACK_PRODUCTION, station_ids, start_date, end_date)
        
        # Парсинг даних виробітку з групуванням по station_id
        # Структура: {station_id: {date: sum_production}}
        station_data = {}
        
        for row in data_values:
            if len(row) < 4:
                continue
            
            try:
                # Колонка B (індекс 1) - station_id (SS001, SS002...)
                station_id = row[1].strip() if len(row) > 1 else None
                
                # Пропускаємо рядки без station_id
                if not station_id or not station_id.startswith('SS'):
                    continue
                
                # Ініціалізуємо словник для станції
                if station_id not in station_data:
                    station_data[station_id] = {}
                
                # Читаємо дані виробітку з колонок D, E, F... (індекси 3, 4, 5...)
                for date_str, col_index in date_columns:
                    if col_index < len(row) and row[col_index]:
                        try:
                            # Читаємо значення з таблиці (кВт·год)
                            production_value = str(row[col_index]).replace(',', '.')  # Заміна коми на крапку
                            production_kwh = float(production_value)
                            
                            # Додаємо до суми (сумуємо всі рядки з однаковим station_id)
                            if date_str in station_data[station_id]:
                                station_data[station_id][date_str] += production_kwh
                            else:
                                station_data[station_id][date_str] = production_kwh
                                
                        except (ValueError, IndexError):
                            continue
                
            except (ValueError, IndexError) as e:
                continue
        
        # Конвертуємо у фінальний формат
        production_dict = {}
        for station_id, dates in station_data.items():
            production_dict[station_id] = [
                {'date': date, 'production_kwh': production}
                for date, production in sorted(dates.items())
            ]
        
        if production_dict:
            print(f"✓ Завантажено дані виробітку для {len(production_dict)} станцій з Google Sheets")
            return filter_production_data(production_dict, station_ids, start_date, end_date)
        else:
            print("⚠ Не вдалося розпарсити дані, використовуються резервні")
            return filter_production_data(FALLBACK_PRODUCTION, station_ids, start_date, end_date)
            
    except HttpError as e:
        print(f"⚠ Помилка API: {e}")
        return filter_production_data(FALLBACK_PRODUCTION, station_ids, start_date, end_date)
    except Exception as e:
        print(f"⚠ Помилка завантаження: {e}")
        return filter_production_data(FALLBACK_PRODUCTION, station_ids, start_date, end_date)


def filter_production_data(production_dict, station_ids, start_date, end_date):
    """Фільтрує дані виробітку за станціями та періодом"""
    filtered = {}
    
    # Фільтр по станціях
    if station_ids:
        for station_id in station_ids:
            if station_id in production_dict:
                filtered[station_id] = production_dict[station_id]
    else:
        filtered = production_dict.copy()
    
    # Фільтр по датах
    if start_date and end_date:
        # Перевіряємо тип (str або datetime)
        if isinstance(start_date, str):
            start_str = start_date
        else:
            start_str = start_date.strftime('%Y-%m-%d')
            
        if isinstance(end_date, str):
            end_str = end_date
        else:
            end_str = end_date.strftime('%Y-%m-%d')
        
        for station_id in filtered:
            filtered[station_id] = [
                record for record in filtered[station_id]
                if start_str <= record['date'] <= end_str
            ]
    
    return filtered


def get_available_date_range():
    """Повертає доступний діапазон дат з даних"""
    # Спочатку пробуємо завантажити з Google Sheets
    production_data = get_production_data()
    
    if not production_data:
        # Якщо немає даних, повертаємо діапазон з резервних даних
        return {
            'min_date': '2021-10-11',
            'max_date': '2024-10-10'
        }
    
    all_dates = []
    for station_data in production_data.values():
        for record in station_data:
            all_dates.append(record['date'])
    
    if all_dates:
        return {
            'min_date': min(all_dates),
            'max_date': max(all_dates)
        }
    else:
        return {
            'min_date': '2021-10-11',
            'max_date': '2024-10-10'
        }


def get_station_by_id(station_id):
    """Отримує дані конкретної станції за ID"""
    stations = get_all_stations()
    for station in stations:
        if station['station_id'] == station_id:
            return station
    return None


def get_statistics():
    """Отримує загальну статистику по всіх станціях"""
    stations = get_all_stations()
    
    total_capacity = sum(s['total_capacity_kw'] for s in stations)
    locations = set(s['location'] for s in stations)
    monitoring_systems = set(s['monitoring_system'] for s in stations)
    
    return {
        'total_stations': len(stations),
        'total_capacity_kw': total_capacity,
        'total_locations': len(locations),
        'total_monitoring_systems': len(monitoring_systems)
    }
