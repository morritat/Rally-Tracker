/**
 * Админ-панель: загрузка пользователей и управление ими.
 */
let currentUsers = [];

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // 1. Проверка прав (если нет токена или роль не admin)
    if (!token || user.role !== 'admin') {
        alert('Доступ запрещён. Требуются права администратора.');
        window.location.href = 'login.html';
        return;
    }

    const addButton = document.getElementById('addUserBtn');
    if (addButton) addButton.addEventListener('click', addUser);
    await loadUsers();
});

async function loadUsers() {
    const tbody = document.getElementById('usersTableBody');
    const token = localStorage.getItem('token');

    try {
        const response = await fetch('/api/admin/users', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Не удалось загрузить пользователей');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.message);

        const users = data.users;
        currentUsers = users;
        renderStats(users);
        renderTable(users, tbody);

    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--red);">Ошибка загрузки: ${error.message}</td></tr>`;
    }
}

function renderStats(users) {
    const total = users.length;
    const active = users.filter(u => !u.is_blocked).length;
    const blocked = users.filter(u => u.is_blocked).length;
    const admins = users.filter(u => u.role === 'admin').length;

    document.getElementById('statTotal').textContent = String(total).padStart(2, '0');
    document.getElementById('statActive').textContent = String(active).padStart(2, '0');
    document.getElementById('statBlocked').textContent = String(blocked).padStart(2, '0');
    document.getElementById('statAdmins').textContent = String(admins).padStart(2, '0');
    document.getElementById('paginationInfo').textContent = `Показано ${total} из ${total}`;
}

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>\"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[char]));
}

function renderTable(users, tbody) {
    tbody.innerHTML = '';

    users.forEach(u => {
        const roleClass = u.role === 'admin' ? 'role-admin' : (u.role === 'marshal' ? 'role-marshal' : 'role-user');
        const roleLabel = u.role === 'admin' ? 'ADMIN' : (u.role === 'marshal' ? 'NAVIGATOR' : 'USER');
        
        const statusClass = u.is_blocked ? 'blocked' : 'active';
        const statusLabel = u.is_blocked ? 'BLOCKED' : 'ACTIVE';

        // Формируем кнопки действий в зависимости от статуса и роли
        let actions = `<button class="act-btn" onclick="editUser(${u.id})">Edit</button>`;
        
        if (u.role !== 'admin') { // Админа нельзя заблокировать или удалить через этот интерфейс
            if (u.is_blocked) {
                actions += `<button class="act-btn green" onclick="unblockUser(${u.id})">Unblock</button>`;
            } else {
                actions += `<button class="act-btn gray" onclick="blockUser(${u.id})">Block</button>`;
            }
            actions += `<button class="act-btn" onclick="deleteUser(${u.id})">Delete</button>`;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td data-label="ID">${String(u.id).padStart(2, '0')}</td>
            <td data-label="Email">${escapeHTML(u.email)}</td>
            <td data-label="Имя">${escapeHTML(u.full_name)}</td>
            <td data-label="Роль"><span class="role-tag ${roleClass}">${roleLabel}</span></td>
            <td data-label="Статус"><span class="status-dot ${statusClass}"></span>${statusLabel}</td>
            <td data-label="Действия">${actions}</td>
        `;
        tbody.appendChild(tr);
    });
}

// --- Функции действий ---

async function blockUser(userId) {
    if (!confirm('Заблокировать этого пользователя?')) return;
    await updateUserStatus(userId, true);
}

async function unblockUser(userId) {
    if (!confirm('Разблокировать этого пользователя?')) return;
    await updateUserStatus(userId, false);
}

async function updateUserStatus(userId, isBlocked) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/admin/users/${userId}/status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_blocked: isBlocked })
        });
        const data = await response.json();
        if (data.success) {
            loadUsers(); // Перезагружаем таблицу
        } else {
            alert('Ошибка: ' + data.message);
        }
    } catch (error) {
        alert('Ошибка сети');
    }
}

async function deleteUser(userId) {
    if (!confirm('Вы уверены, что хотите БЕЗВОЗВРАТНО удалить этого пользователя?')) return;
    
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (data.success) {
            loadUsers();
        } else {
            alert('Ошибка: ' + data.message);
        }
    } catch (error) {
        alert('Ошибка сети');
    }
}

async function editUser(userId) {
    const user = currentUsers.find(u => Number(u.id) === Number(userId));
    if (!user) return;
    const newName = prompt('Имя пользователя:', user.full_name);
    if (newName === null) return;
    const newEmail = prompt('Email пользователя:', user.email);
    if (newEmail === null) return;
    const newRole = prompt('Роль (user или marshal): ', user.role === 'marshal' ? 'marshal' : 'user');
    if (newRole === null) return;
    if (!['user', 'marshal'].includes(newRole.trim())) {
        alert('Роль должна быть user или marshal.');
        return;
    }
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: newName.trim(), email: newEmail.trim(), role: newRole.trim() })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Не удалось обновить пользователя');
        await loadUsers();
    } catch (error) {
        alert(error.message || 'Ошибка сети');
    }
}


async function addUser() {
    const fullName = prompt('Имя нового пользователя:');
    if (fullName === null || !fullName.trim()) return;
    const email = prompt('Email нового пользователя:');
    if (email === null || !email.trim()) return;
    const password = prompt('Временный пароль (минимум 6 символов):');
    if (password === null) return;
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName: fullName.trim(), email: email.trim(), password })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Не удалось создать пользователя');
        alert('Пользователь создан. Он сможет войти со своим email и временным паролем.');
        await loadUsers();
    } catch (error) {
        alert(error.message || 'Ошибка соединения');
    }
}
