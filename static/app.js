// Основные элементы интерфейса
const clickButton = document.getElementById('click-button');
const clicksElement = document.getElementById('clicks');
const clickPowerElement = document.getElementById('click-power');
const passiveIncomeElement = document.getElementById('passive-income');
const inventoryButton = document.getElementById('toggle-inventory');
const inventoryContainer = document.getElementById('inventory');

// Получаем user_id из URL
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id');

// Базовая функция отправки действий
async function sendAction(action, data = {}) {
    try {
        const response = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, ...data })
        });
        return await response.json();
    } catch (error) {
        console.error(`Error in ${action}:`, error);
        return null;
    }
}

// Обработка клика
clickButton.addEventListener('click', () => {
    const currentClicks = parseInt(clicksElement.textContent) || 0;
    const clickPower = parseInt(clickPowerElement.textContent) || 1;
    
    // Мгновенное обновление
    clicksElement.textContent = currentClicks + clickPower;
    
    // Отправка на сервер
    sendAction('click');
});

// Улучшение силы клика
document.getElementById('upgrade-click').addEventListener('click', async () => {
    const currentClicks = parseInt(clicksElement.textContent) || 0;
    const cost = parseInt(document.getElementById('click-cost').textContent) || 50;
    
    if (currentClicks >= cost) {
        const result = await sendAction('upgrade_click');
        if (result && !result.error) {
            clicksElement.textContent = result.clicks;
            clickPowerElement.textContent = result.click_power;
            document.getElementById('click-cost').textContent = 
                Math.floor(50 * Math.pow(1.5, result.click_power - 1));
        }
    }
});

// Улучшение пассивного дохода
document.getElementById('upgrade-passive').addEventListener('click', async () => {
    const currentClicks = parseInt(clicksElement.textContent) || 0;
    const cost = parseInt(document.getElementById('passive-cost').textContent) || 100;
    
    if (currentClicks >= cost) {
        const result = await sendAction('upgrade_passive');
        if (result && !result.error) {
            clicksElement.textContent = result.clicks;
            passiveIncomeElement.textContent = result.passive_income;
            document.getElementById('passive-cost').textContent = 
                Math.floor(100 * Math.pow(1.5, result.passive_income));
        }
    }
});

// Открытие бокса с питомцем
document.getElementById('box-button').addEventListener('click', async () => {
    const currentClicks = parseInt(clicksElement.textContent) || 0;
    
    if (currentClicks >= 500) {
        const result = await sendAction('box');
        if (result && result.success) {
            updateInventory(result.user_stats);
            const pet = result.pet_info;
            alert(`Вы получили питомца: ${pet.name}!\nМножитель клика: x${pet.click_multiplier}\nМножитель дохода: x${pet.passive_multiplier}\nРедкость: ${pet.rarity}`);
        }
    }
});

// Функции для питомцев
async function equipPet(pet) {
    const result = await sendAction('equip_pet', { pet });
    if (result && !result.error) {
        updateInventory(result);
        // Обновляем статистику сразу после экипировки
        loadStats();
    }
}

async function unequipPet(pet) {
    const result = await sendAction('unequip_pet', { pet });
    if (result && !result.error) {
        updateInventory(result);
        // Обновляем статистику сразу после снятия
        loadStats();
    }
}

// Обновление инвентаря
function updateInventory(data) {
    if (!data || !data.inventory) return;
    
    const petsElement = document.getElementById('equipped-pets');
    const equippedCount = document.getElementById('equipped-count');
    petsElement.innerHTML = '';
    
    equippedCount.textContent = data.equipped_pets ? data.equipped_pets.length : 0;
    
    data.inventory.forEach(pet => {
        const petCard = document.createElement('div');
        petCard.className = 'pet-card';
        petCard.dataset.pet = pet;
        
        const isEquipped = data.equipped_pets && data.equipped_pets.includes(pet);
        if (isEquipped) petCard.classList.add('equipped');
        
        fetch('/api/pets')
            .then(response => response.json())
            .then(pets => {
                const petInfo = pets[pet];
                petCard.innerHTML = `
                    <div class="pet-info">
                        🐾 ${pet}
                        <div class="pet-stats">
                            Множитель клика: x${petInfo.click_multiplier}
                            Множитель дохода: x${petInfo.passive_multiplier}
                            Редкость: ${petInfo.rarity}
                        </div>
                    </div>
                    <button onclick="${isEquipped ? 'unequipPet' : 'equipPet'}('${pet}')"
                            ${!isEquipped && data.equipped_pets && data.equipped_pets.length >= 2 ? 'disabled' : ''}>
                        ${isEquipped ? 'Снять' : 'Экипировать'}
                    </button>
                `;
            });
        
        petsElement.appendChild(petCard);
    });
}

// Переключение инвентаря
inventoryButton.addEventListener('click', () => {
    inventoryContainer.classList.toggle('active');
});

// Пассивный доход
setInterval(() => {
    const passiveIncome = parseInt(passiveIncomeElement.textContent) || 0;
    if (passiveIncome > 0) {
        const currentClicks = parseInt(clicksElement.textContent) || 0;
        clicksElement.textContent = currentClicks + passiveIncome;
        sendAction('passive_income');
    }
}, 1000);

// Начальная загрузка
async function loadStats() {
    try {
        const response = await fetch(`/api/stats?user_id=${userId}`);
        const data = await response.json();
        if (data) {
            clicksElement.textContent = data.clicks;
            clickPowerElement.textContent = data.click_power;
            passiveIncomeElement.textContent = data.passive_income;
            
            document.getElementById('click-cost').textContent = 
                Math.floor(50 * Math.pow(1.5, data.click_power - 1));
            document.getElementById('passive-cost').textContent = 
                Math.floor(100 * Math.pow(1.5, data.passive_income));
            
            updateInventory(data);
            
            // Автоматически сохраняем каждые 30 секунд
            setInterval(() => {
                sendAction('stats', data);
            }, 30000);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Загружаем статистику при старте
loadStats(); 