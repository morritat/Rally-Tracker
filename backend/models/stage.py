"""Модель «Этап (СУ)»."""
from backend.models.base_model import BaseModel
from backend.database import Database
from backend.services.weather_service import WeatherService


class Stage(BaseModel):
    table_name = 'stages'

    def __init__(self, name=None, date=None, location=None,
                 latitude=None, longitude=None, distance_km=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.date = date
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.distance_km = distance_km

    def save(self) -> int:
        stage_id = self.db.execute(
            """INSERT INTO stages (name, date, location, latitude, longitude, distance_km)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (self.name, self.date, self.location, self.latitude,
             self.longitude, self.distance_km)
        )
        self._refresh_weather(stage_id, self.latitude, self.longitude, self.date)
        self.id = stage_id
        return stage_id

    @classmethod
    def _refresh_weather(cls, stage_id, latitude, longitude, date=None):
        if latitude is None or longitude is None:
            return None
        weather = WeatherService.get_weather(latitude, longitude, date)
        if weather:
            Database().execute(
                """UPDATE stages
                   SET weather_temp = ?, weather_desc = ?,
                       wind_speed = ?, surface_type = ?
                   WHERE id = ?""",
                (weather['temp'], weather['desc'], weather['wind_speed'],
                 weather['surface_type'], stage_id)
            )
        return weather

    @classmethod
    def get_all_with_weather(cls):
        db = Database()
        stages = db.fetch_all('SELECT * FROM stages ORDER BY date ASC')
        # Погода всегда берётся из OpenWeatherMap; кэш сервиса ограничивает частоту запросов до 1 раза в 5 минут.
        for stage in stages:
            weather = cls._refresh_weather(
                stage['id'], stage['latitude'], stage['longitude'], stage['date']
            )
            if weather:
                stage.update({
                    'weather_temp': weather['temp'],
                    'weather_desc': weather['desc'],
                    'wind_speed': weather['wind_speed'],
                    'surface_type': weather['surface_type'],
                    'weather_updated_at': weather.get('updated_at'),
                })
            else:
                # Не показываем устаревшую погоду из БД, если API временно недоступен.
                stage.update({
                    'weather_temp': None, 'weather_desc': None,
                    'wind_speed': None, 'surface_type': None,
                    'weather_updated_at': None,
                })
        return stages

    @classmethod
    def get_by_id(cls, stage_id: int):
        db = Database()
        stage = db.fetch_one(
            """SELECT s.*,
                      (SELECT COUNT(*) FROM results WHERE stage_id = s.id) as results_count
               FROM stages s WHERE s.id = ?""",
            (stage_id,)
        )
        if stage:
            weather = cls._refresh_weather(
                stage['id'], stage['latitude'], stage['longitude'], stage['date']
            )
            if weather:
                stage.update({
                    'weather_temp': weather['temp'],
                    'weather_desc': weather['desc'],
                    'wind_speed': weather['wind_speed'],
                    'surface_type': weather['surface_type'],
                    'weather_updated_at': weather.get('updated_at'),
                })
            else:
                # Не показываем устаревшую погоду из БД, если API временно недоступен.
                stage.update({
                    'weather_temp': None, 'weather_desc': None,
                    'wind_speed': None, 'surface_type': None,
                    'weather_updated_at': None,
                })
        return stage

    @classmethod
    def update(cls, stage_id: int, **kwargs) -> bool:
        allowed = {
            'name', 'date', 'location', 'latitude', 'longitude', 'distance_km',
            'weather_temp', 'weather_desc', 'wind_speed', 'surface_type'
        }
        kwargs = {k: v for k, v in kwargs.items() if k in allowed}
        if not kwargs:
            return False
        db = Database()
        sets = [f'{key} = ?' for key in kwargs]
        params = list(kwargs.values()) + [stage_id]
        db.execute(
            f"UPDATE stages SET {', '.join(sets)} WHERE id = ?", tuple(params)
        )
        return True

    @classmethod
    def update_weather(cls, stage_id: int):
        db = Database()
        stage = db.fetch_one('SELECT * FROM stages WHERE id = ?', (stage_id,))
        if not stage or stage['latitude'] is None or stage['longitude'] is None:
            return None
        return cls._refresh_weather(
            stage_id, stage['latitude'], stage['longitude'], stage['date']
        )
