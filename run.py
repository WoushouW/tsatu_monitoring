"""
Точка входу для запуску Flask додатку
"""
from app import app
import os

if __name__ == '__main__':
    # для Render
    port = int(os.environ.get('PORT', 5000))
    
    # Запуск додатку
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
