// 等待页面DOM结构完全加载完成后执行

console.log("✅ script.js 执行了");

document.addEventListener('DOMContentLoaded', () => {
    // 初始化操作
    initEventListeners();
    // 加载国家列表
    loadCountries();
});


// 获取DOM元素
const sidebar = document.getElementById('sidebar');
const toggleButton = document.getElementById('toggleSidebar');
const committeeInput = document.getElementById('committeeInput');
const agendaInput = document.getElementById('agendaInput');
const committeeNameDisplay = document.getElementById('committee-name');
const agendaDisplay = document.getElementById('agenda-display');
const countryListContainer = document.getElementById('country-draggable-list');
const addCountryBtn = document.getElementById('add-country-btn');
const newCountryInput = document.getElementById('new-country-input');
const countrySearchInput = document.getElementById('country-search-input'); // 假设存在搜索输入框

// 存储数据
let tempAddedCountries = [];
let attendingCountries = [];
let allCountries = []; // 存储所有国家数据用于搜索

/**
 * 初始化所有事件监听器
 */
function initEventListeners() {
    // 导航栏切换
    toggleButton.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // 输入框事件
    committeeInput.addEventListener('input', updateCommitteeName);
    agendaInput.addEventListener('input', updateAgenda);
    addCountryBtn.addEventListener('click', addNewCountry);
    
    // 搜索事件
    if (countrySearchInput) {
        countrySearchInput.addEventListener('input', handleCountrySearch);
    }
}

/**
 * 更新会议及委员会名称
 */
function updateCommitteeName() {
    const committeeInputValue = committeeInput.value;
    committeeNameDisplay.textContent = committeeInputValue ? committeeInputValue : " ";
}

/**
 * 更新议题
 */
function updateAgenda() {
    const agendaInputValue = agendaInput.value;
    agendaDisplay.textContent = agendaInputValue ? `议题: ${agendaInputValue}` : "";
}

/**
 * 重置表单和顶栏内容
 */
function resetForm() {
    committeeInput.value = '';
    agendaInput.value = '';
    updateCommitteeName();
    updateAgenda();
}

/**
 * 添加新国家
 */
function addNewCountry() {
    const countryName = newCountryInput.value.trim();
    
    // 判断不重复添加
    if (countryName && !tempAddedCountries.some(item => item.name === countryName)) {
        const newCountry = {
            id: Date.now(),
            name: countryName,
            hasFlag: false,
            flag_url: "/static/flags/default.png"  // fallback 图像
        };

        // 添加到临时国家列表
        tempAddedCountries.push(newCountry);
        newCountryInput.value = '';

        renderTempCountries();  // 渲染左边临时列表

        // ✅ 同时添加到右侧应出席国家
        addToAttendingCountries(newCountry);
    }
}


/**
 * 渲染临时添加的国家
 */
function renderTempCountries() {
    const container = document.getElementById('temp-countries-container');
    if (!container) return;

    container.innerHTML = '';
    tempAddedCountries.forEach(country => {
        const item = document.createElement('div');
        item.className = 'temp-country';
        item.innerHTML = `
            <span>${country.name}</span>
            <button class="temp-remove-btn" data-id="${country.id}">×</button>
        `;
        container.appendChild(item);
    });

    // 绑定临时国家删除事件
    document.querySelectorAll('.temp-remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            tempAddedCountries = tempAddedCountries.filter(c => c.id !== id);
            renderTempCountries();
        });
    });
}

/**
 * 添加国家到参会列表
 * @param {Object} country - 国家对象
 */
function addCountryToAttending(country) {
    // 避免重复添加
    if (!attendingCountries.some(item => item.id === country.id)) {
        attendingCountries.push(country);
        renderAttendingCountries(); // 渲染参会列表
    }
}

/**
 * 渲染参会国家列表
 */
function renderAttendingCountries() {
    const container = document.getElementById('attending-countries');
    if (!container) {
        console.warn('未找到参会列表容器，请在HTML中添加 id="attending-countries" 的元素');
        return;
    }

    container.innerHTML = '';

    if (attendingCountries.length === 0) {
        container.innerHTML = '<div class="empty-attending">暂无参会国家</div>';
        return;
    }

    attendingCountries.forEach(country => {
        const item = document.createElement('div');
        item.className = 'attending-country-item';

        const flagSrc = country.flag_url || '';


        item.innerHTML = `
            <img src="${country.flag_url || '/static/flags/default.png'}" class="country-flag"
                onerror="this.src='/static/flags/default.png'" />
            <span>${country.name}</span>
            <button class="remove-btn" data-id="${country.id}">×</button>
        `;
        container.appendChild(item);
    });

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const countryId = parseInt(e.target.dataset.id);
            attendingCountries = attendingCountries.filter(item => item.id !== countryId);
            renderAttendingCountries();
        });
    });
}


/**
 * 从后端接口获取国家列表并渲染到页面
 */
async function loadCountries() {
    try {
        const response = await fetch('http://localhost:5000/api/countries');

        if (!response.ok) {
            throw new Error(`请求失败，状态码: ${response.status}`);
        }

        const result = await response.json();
        console.log("国家数据内容：", result);

        const data = result.data;  // ✅ 重点修复点：取出 data 字段里的数组！

        // 假设直接是数组 [{ name, flag_url }]
        allCountries = data.map((country, index) => ({
            id: index + 1,
            name: country.name,
            flag_url: country.flag_url || `/static/flags/default_flag.png`
        }));

        renderCountryList(allCountries);
    } catch (error) {
        countryListContainer.innerHTML = `
            <div class="error">
                加载失败，请检查后端服务是否运行<br>
                错误信息: ${error.message}
            </div>
        `;
        console.error('加载国家列表时发生错误:', error);
    }
}


/**
 * 渲染国家列表
 * @param {Array} countries - 要渲染的国家数组
 */
function renderCountryList(countries) {
      // 关键调试：看拿到多少个国家
    console.log('收到的国家数量：', countries.length); 

    if (countries.length > 0) {
        countryListContainer.innerHTML = '';
        countries.forEach(country => {
            const countryItem = document.createElement('div');
            countryItem.className = 'country-item';
            countryItem.dataset.countryId = country.id;

        const flagSrc = country.flag_url || '';


            countryItem.innerHTML = `
                <img src="${country.flag_url || '/static/flags/default.png'}" class="country-flag"
                    onerror="this.src='/static/flags/default.png'" />
                <span>${country.name}</span>
                <button class="add-btn country-add">+</button>
            `;

            // 为添加按钮绑定点击事件
            const addButton = countryItem.querySelector('.country-add');
            addButton.addEventListener('click', () => {
                addToAttendingCountries(country);
            });

            countryListContainer.appendChild(countryItem);
        });
    } else {
        countryListContainer.innerHTML = '<div class="no-data">未找到匹配的国家</div>';
    }
}

/**
 * 处理国家搜索
 */
function handleCountrySearch() {
    const searchTerm = countrySearchInput.value.trim().toLowerCase();
    
    if (!searchTerm) {
        renderCountryList(allCountries);
        return;
    }
    
    const filteredCountries = allCountries.filter(country => 
        country.name.toLowerCase().includes(searchTerm)
    );
    
    renderCountryList(filteredCountries);
}

/**
 * 将国家添加到参会列表（去重处理）
 * @param {Object} country - 要添加的国家对象
 */
function addToAttendingCountries(country) {
    const isAlreadyAdded = attendingCountries.some(item => item.id === country.id);
    if (!isAlreadyAdded) {
        attendingCountries.push(country);
        renderAttendingCountries();
        alert(`${country.name} 已添加到参会列表`);
    } else {
        alert(`${country.name} 已在参会列表中`);
    }
}
