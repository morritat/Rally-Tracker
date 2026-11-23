/** Public stage details and live stage-specific weather; protected competition data requires login. */
const protectedNotice = '<div class="restricted-content" style="padding:1.5rem;background:var(--card,#1f1f2d);color:#fff;border-left:4px solid var(--red,#e11)"><h3>Доступ для зарегистрированных участников</h3><p>Результаты, телеметрия, радио и видео доступны после входа в аккаунт.</p><a class="btn" href="/login.html">Войти</a> <a class="btn" href="/register.html">Регистрация</a></div>';

async function loadStage() {
    const stageId = new URLSearchParams(window.location.search).get('id') || 1;
    try {
        const response = await fetch(`/api/stages/${stageId}`);
        const data = await response.json();
        if (!data.success || !data.stage) {
            document.getElementById('stageName').textContent = 'Этап не найден';
            return;
        }
        const stage = data.stage;
        document.getElementById('stageName').textContent = stage.name;
        const date = new Date(stage.date);
        const dateStr = date.toLocaleString('ru-RU', {day:'numeric', month:'long', year:'numeric', hour:'2-digit', minute:'2-digit'});
        const metaWeather = stage.weather_temp !== null && stage.weather_temp !== undefined
            ? `${stage.weather_temp}°C, ${stage.weather_desc || ''}, Ветер ${stage.wind_speed ?? 0} м/с`
            : 'Погода временно недоступна';
        document.getElementById('stageMeta').innerHTML = `<span>${dateStr}</span><span>${stage.location || 'Не указано'}</span><span>${stage.distance_km} км</span><span>${metaWeather}</span>`;
        await loadStageLiveWeather(stageId, stage.location);
        await showProtectedTabs(stageId);
    } catch (err) {
        console.error('Ошибка загрузки этапа:', err);
        document.getElementById('stageName').textContent = 'Ошибка загрузки';
    }
}
async function showProtectedTabs(stageId) {
    const token = localStorage.getItem('token');
    let signedIn = false;
    if (token) {
        try {
            const check = await fetch('/api/auth/me', {headers:{Authorization:`Bearer ${token}`}});
            signedIn = check.ok;
            if (!signedIn) { localStorage.removeItem('token'); localStorage.removeItem('user'); }
        } catch (_) { signedIn = false; }
    }
    if (!signedIn) {
        ['resultsAccess','telemetryContent','radioContent','videoContent'].forEach(id => {
            const el = document.getElementById(id); if (el) el.innerHTML = protectedNotice;
        });
        return;
    }
    const resultsTable = document.getElementById('resultsTable');
    if (resultsTable) resultsTable.style.display = '';
    const access = document.getElementById('resultsAccess'); if (access) access.innerHTML = '';
    ['telemetryContent','radioContent','videoContent'].forEach(id => {
        const el = document.getElementById(id); if (el) el.innerHTML = '<p>Материалы этого раздела пока не опубликованы.</p>';
    });
    await loadResults(stageId, token);
}
async function loadResults(stageId, token) {
    const tbody = document.getElementById('resultsBody');
    try {
        const response = await fetch(`/api/results/stage/${stageId}`, {headers:{Authorization:`Bearer ${token}`}});
        if (!response.ok) throw new Error('results unavailable');
        const data = await response.json();
        if (!data.success || !data.results?.length) { tbody.innerHTML='<tr><td colspan="6">Результаты пока не добавлены</td></tr>'; return; }
        tbody.innerHTML = '';
        data.results.forEach((r,i) => {
            const total = r.time_seconds + r.penalty_seconds;
            const totalFmt = `${Math.floor(total/60)}:${(total%60).toFixed(1).padStart(4,'0')}`;
            const penalty = r.penalty_seconds > 0 ? `+${r.penalty_seconds} сек` : '0 сек';
            const posClass = i===0?'pos-1':i===1?'pos-2':i===2?'pos-3':'';
            const tr=document.createElement('tr');
            tr.innerHTML=`<td><span class="pos ${posClass}">${i+1}</span></td><td>${r.pilot_name} / ${r.navigator_name}</td><td class="team-name">${r.car_model}</td><td>${formatTime(r.time_seconds)}</td><td>${penalty}</td><td class="pts">${totalFmt}</td>`;
            tbody.appendChild(tr);
        });
    } catch(e) { tbody.innerHTML='<tr><td colspan="6">Не удалось загрузить результаты.</td></tr>'; }
}
function formatTime(seconds) { return `${Math.floor(seconds/60)}:${(seconds%60).toFixed(1).padStart(4,'0')}`; }
async function loadStageLiveWeather(stageId, stageLocation) {
    const panel = document.getElementById('stageLiveWeather'); if (!panel) return;
    try {
        const response = await fetch(`/api/stages/${stageId}/weather-current`);
        const data = await response.json();
        if (!response.ok || !data.success || !data.weather) throw new Error('weather unavailable');
        const w=data.weather, desc=w.desc||'Нет описания';
        const updated=w.updated_at?new Date(w.updated_at).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'}):'';
        panel.innerHTML=`<div class="weather-heading">Актуальная погода · ${data.location || stageLocation || 'этап'}</div><div class="weather-content"><div class="weather-icon">${weatherIcon(desc)}</div><div class="weather-temperature">${w.temp}°C</div><div class="weather-details"><div class="weather-description">${desc}</div><div class="weather-wind">Ветер: ${w.wind_speed ?? 0} м/с</div></div></div><div class="weather-updated">${updated?`Обновлено: ${updated} · `:''}автообновление каждые 5 минут</div>`;
    } catch(_) { panel.innerHTML=`<div class="weather-heading">Актуальная погода · ${stageLocation||'этап'}</div><div class="weather-loading">Погода временно недоступна</div>`; }
}
function weatherIcon(desc) { const t=String(desc).toLowerCase(); if(t.includes('гроза'))return '⛈️'; if(t.includes('снег')||t.includes('метель'))return '🌨️'; if(t.includes('дожд')||t.includes('лив'))return '🌧️'; if(t.includes('туман'))return '🌫️'; if(t.includes('облач')||t.includes('пасмур'))return '☁️'; if(t.includes('ясно'))return '☀️'; return '🌤️'; }
document.addEventListener('DOMContentLoaded',loadStage);
setInterval(()=>{const id=new URLSearchParams(location.search).get('id')||1; const loc=document.getElementById('stageLiveWeather')?.dataset.location; loadStageLiveWeather(id,loc);},5*60*1000);
