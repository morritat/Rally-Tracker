"""Скрипт инициализации базы данных Rally Stage Tracker."""
import os
import sys
from backend.database import Database


def init_db():
    """Создание схемы и загрузка seed-данных."""
    db = Database()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, 'database', 'schema.sql')
    seed_path = os.path.join(base_dir, 'database', 'seed.sql')
    
    # Проверка существования файлов
    if not os.path.exists(schema_path):
        print(f"❌ Файл не найден: {schema_path}")
        sys.exit(1)
    
    if not os.path.exists(seed_path):
        print(f"❌ Файл не найден: {seed_path}")
        sys.exit(1)
    
    print("🔄 Создание схемы БД...")
    try:
        db.execute_script(schema_path)
        print("✅ Схема создана")
    except Exception as e:
        print(f"❌ Ошибка схемы: {e}")
        sys.exit(1)
    
    print("🔄 Загрузка seed-данных...")
    try:
        db.execute_script(seed_path)
        print("✅ Seed-данные загружены")
    except Exception as e:
        print(f"❌ Ошибка seed: {e}")
        sys.exit(1)
    
    print("🎉 База данных готова!")
    print(f"📁 Файл БД: {db.db_path}")


if __name__ == '__main__':
    init_db()