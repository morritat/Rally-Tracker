/**
 * Загрузка этапов с сервера и отображение актуальной погоды.
 */
async function loadStages() {
    const grid = document.getElementById('stagesGrid');
    if (!grid) return;

    try {
        const response = await fetch('/api/stages');
        const data = await response.json();

        if (!data.success || !data.stages || data.stages.length === 0) {
            grid.innerHTML = '<div class="empty-card">Этапы не найдены</div>';
            return;
        }

        grid.innerHTML = '';

        data.stages.forEach(stage => {
            const date = new Date(stage.date);
            const day = date.getDate();
            const month = date.toLocaleString('ru', { month: 'short' }).toUpperCase();

            const surfaceColors = {
                'wet': '#3498db',
                'dry': '#27ae60',
                'snow': '#ecf0f1',
                'gravel': '#e67e22',
                'asphalt': '#34495e'
            };
            const surfaceColor = surfaceColors[stage.surface_type] || '#95a5a6';

            const weatherText = stage.weather_temp !== null && stage.weather_temp !== undefined
                ? `${stage.weather_temp}°C, ${stage.weather_desc || ''}${stage.wind_speed !== null && stage.wind_speed !== undefined ? `, ветер ${stage.wind_speed} м/с` : ''}`
                : 'Погода временно недоступна';

            const card = document.createElement('div');
            card.className = 'stage-card';
            card.onclick = () => window.location.href = `stage.html?id=${stage.id}`;

            card.innerHTML = `
                <div class="sc-image">
                    <img src="/static/img/img${stage.id}_${stage.id === 1 ? 'forest' : stage.id === 2 ? 'mountain' : stage.id === 3 ? 'desert' : 'snow'}.jpg" alt="${stage.name}"
                         onerror="this.src='/static/img/wallpaper_index.jpg'">
                    <div class="sc-date">
                        <span class="day">${day}</span>
                        <span class="month">${month}</span>
                    </div>
                </div>
                <div class="sc-body">
                    <h3 class="sc-title">${stage.name}</h3>
                    <div class="sc-category" style="color: ${surfaceColor}">
                        ${(stage.surface_type || 'N/A').toUpperCase()} · ${stage.distance_km} км
                    </div>
                    <p class="sc-desc">${weatherText}</p>
                    <div class="sc-more">
                        Подробнее <i class="fas fa-plus"></i>
                    </div>
                </div>
            `;

            grid.appendChild(card);
        });

    } catch (error) {
        console.error('Ошибка загрузки этапов:', error);
        grid.innerHTML = '<div class="error-card">Не удалось загрузить этапы. Проверьте сервер.</div>';
    }
}

document.addEventListener('DOMContentLoaded', loadStages);
setInterval(loadStages, 5 * 60 * 1000);


/**
 * Текущая погода в Петрозаводске — ориентир для Карелии.
 * Один и тот же результат показывается над и под списком этапов.
 */
async function loadKareliaWeather() {
    const panels = [
        document.getElementById('currentWeatherTop'),
        document.getElementById('currentWeatherBottom')
    ].filter(Boolean);
    if (!panels.length) return;

    try {
        const response = await fetch('/api/stages/weather/karelia');
        const data = await response.json();
        if (!response.ok || !data.success || !data.weather) {
            throw new Error(data.message || 'Погода временно недоступна');
        }

        const weather = data.weather;
        const description = weather.desc || 'Нет описания';
        const icon = getWeatherIcon(description);
        const updated = weather.updated_at
            ? new Date(weather.updated_at).toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})
            : '';

        panels.forEach(panel => {
            panel.replaceChildren();

            const heading = document.createElement('div');
            heading.className = 'weather-heading';
            heading.textContent = `Погода в Карелии · ${data.location || 'Петрозаводск'}`;

            const content = document.createElement('div');
            content.className = 'weather-content';

            const symbol = document.createElement('div');
            symbol.className = 'weather-icon';
            symbol.textContent = icon;

            const temperature = document.createElement('div');
            temperature.className = 'weather-temperature';
            temperature.textContent = `${weather.temp}°C`;

            const details = document.createElement('div');
            details.className = 'weather-details';

            const condition = document.createElement('div');
            condition.className = 'weather-description';
            condition.textContent = description;

            const wind = document.createElement('div');
            wind.className = 'weather-wind';
            wind.textContent = `Ветер: ${weather.wind_speed ?? 0} м/с`;

            details.append(condition, wind);
            content.append(symbol, temperature, details);

            const footer = document.createElement('div');
            footer.className = 'weather-updated';
            footer.textContent = updated ? `Обновлено: ${updated}` : 'Актуальные данные';

            panel.append(heading, content, footer);
        });
    } catch (error) {
        console.error('Ошибка загрузки погоды Карелии:', error);
        panels.forEach(panel => {
            panel.innerHTML = '<div class="weather-heading">Погода в Карелии</div><div class="weather-loading">Погода временно недоступна</div>';
        });
    }
}

function getWeatherIcon(description) {
    const text = String(description).toLowerCase();
    if (text.includes('гроза')) return '⛈️';
    if (text.includes('снег') || text.includes('метель')) return '🌨️';
    if (text.includes('дожд') || text.includes('ливень')) return '🌧️';
    if (text.includes('туман') || text.includes('дым')) return '🌫️';
    if (text.includes('облач') || text.includes('пасмур')) return '☁️';
    if (text.includes('ясно') || text.includes('солн')) return '☀️';
    return '🌤️';
}

document.addEventListener('DOMContentLoaded', loadKareliaWeather);
setInterval(loadKareliaWeather, 5 * 60 * 1000);
