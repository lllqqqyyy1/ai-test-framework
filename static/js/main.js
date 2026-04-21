/**
 * AI 智能测试平台 - 完整前端交互逻辑
 * 包含:测试用例生成、脚本生成、测试执行、报告分析
 */

// 全局状态
let generatedCases = [];
let currentScriptId = null;
let currentScriptContent = '';
let currentTaskId = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initAllModules();
});

/**
 * 初始化所有模块
 */
function initAllModules() {
    initTabNavigation();
    initTestCaseModule();
    initTestScriptModule();
    initTestExecutionModule();
    initReportAnalysisModule();
}

/**
 * 获取 CSRF Token
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 显示全局消息
 */
function showMessage(message, type = 'success', duration = 5000) {
    const messageEl = document.getElementById('global-message');
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, duration);
}

/**
 * 显示/隐藏加载状态
 */
function showLoading(show, text = 'AI 正在处理,请稍候...') {
    const loadingEl = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    loadingText.textContent = text;
    loadingEl.style.display = show ? 'flex' : 'none';
}

// ==================== Tab 导航 ====================

function initTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // 更新按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 更新内容显示
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `tab-${tabId}`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// ==================== 模块 1: 测试用例生成 ====================

function initTestCaseModule() {
    const form = document.getElementById('generate-form');
    const clearBtn = document.getElementById('clear-btn');
    const saveBtn = document.getElementById('save-cases-btn');
    
    if (!form) {
        console.error('找不到 generate-form 元素');
        return;
    }
    
    // 阻止表单默认提交
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();
        console.log('测试用例表单提交已阻止,开始生成...');
        handleGenerateTestCase();
    });
    
    clearBtn.addEventListener('click', () => {
        form.reset();
        document.getElementById('tc-result-section').style.display = 'none';
        generatedCases = [];
    });
    saveBtn.addEventListener('click', handleSaveTestCases);
    
    console.log('测试用例生成模块已初始化');
}

async function handleGenerateTestCase() {
    console.log('handleGenerateTestCase 被调用');
    
    const inputTypeEl = document.getElementById('input-type');
    const providerEl = document.getElementById('tc-provider');
    const inputTextEl = document.getElementById('input-text');
    
    if (!inputTypeEl || !inputTextEl) {
        console.error('找不到表单元素');
        showMessage('页面元素加载失败,请刷新页面', 'error');
        return;
    }
    
    const inputType = inputTypeEl.value;
    const provider = providerEl.value;
    const inputText = inputTextEl.value.trim();
    
    console.log('表单数据:', { inputType, provider, inputText: inputText.substring(0, 50) + '...' });
    
    if (!inputText) {
        showMessage('请输入需求或接口描述', 'error');
        return;
    }
    
    showLoading(true, 'AI 正在生成测试用例...');
    setLoadingButton('generate-btn', true);
    
    try {
        const response = await fetch('/api/generate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                input_type: inputType,
                input: inputText,
                provider: provider
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            generatedCases = data.test_cases;
            displayTestCases(data.test_cases);
            showMessage(`成功生成 ${data.count} 个测试用例`);
        } else {
            showMessage(data.message || '生成失败', 'error');
        }
    } catch (error) {
        console.error('生成测试用例失败:', error);
        showMessage('网络错误,请稍后重试', 'error');
    } finally {
        showLoading(false);
        setLoadingButton('generate-btn', false);
    }
}

function displayTestCases(cases) {
    const resultSection = document.getElementById('tc-result-section');
    const container = document.getElementById('cases-container');
    const caseCount = document.getElementById('case-count');
    
    container.innerHTML = '';
    caseCount.textContent = `共 ${cases.length} 个测试用例`;
    
    cases.forEach((caseItem, index) => {
        const card = document.createElement('div');
        card.className = 'case-card';
        card.innerHTML = `
            <h3>用例 ${index + 1}: ${escapeHtml(caseItem.title)}</h3>
            <div class="case-description">${escapeHtml(caseItem.description)}</div>
            <div class="case-steps">
                <h4>📝 测试步骤:</h4>
                <p>${escapeHtml(caseItem.test_steps)}</p>
            </div>
            <div class="case-expected">
                <h4>✅ 预期结果:</h4>
                <p>${escapeHtml(caseItem.expected_results)}</p>
            </div>
        `;
        container.appendChild(card);
    });
    
    resultSection.style.display = 'block';
}

async function handleSaveTestCases() {
    if (generatedCases.length === 0) {
        showMessage('没有可保存的测试用例', 'error');
        return;
    }
    
    const inputType = document.getElementById('input-type').value;
    const inputText = document.getElementById('input-text').value.trim();
    
    try {
        const response = await fetch('/api/save-test-case/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                test_cases: generatedCases,
                requirements: inputText,
                case_type: inputType === 'requirements' ? 'functional' : 'interface',
                priority: 'medium'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(data.message);
        } else {
            showMessage(data.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('保存失败:', error);
        showMessage('网络错误', 'error');
    }
}

// ==================== 模块 2: 测试脚本生成 ====================

function initTestScriptModule() {
    const form = document.getElementById('script-generate-form');
    const clearBtn = document.getElementById('clear-script-btn');
    const saveBtn = document.getElementById('save-script-btn');
    const executeBtn = document.getElementById('execute-script-btn');
    
    if (!form) {
        console.error('找不到 script-generate-form 元素');
        return;
    }
    
    // 阻止表单默认提交
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();
        console.log('表单提交已阻止,开始生成脚本...');
        handleGenerateScript();
    });
    
    clearBtn.addEventListener('click', () => {
        form.reset();
        document.getElementById('script-result-section').style.display = 'none';
        currentScriptId = null;
        currentScriptContent = '';
    });
    saveBtn.addEventListener('click', handleSaveScript);
    executeBtn.addEventListener('click', handleExecuteScript);
    
    console.log('测试脚本生成模块已初始化');
}

async function handleGenerateScript() {
    console.log('handleGenerateScript 被调用');
    
    const scriptNameEl = document.getElementById('script-name');
    const interfaceDocEl = document.getElementById('interface-doc');
    const providerEl = document.getElementById('ts-provider');
    
    if (!scriptNameEl || !interfaceDocEl) {
        console.error('找不到表单元素');
        showMessage('页面元素加载失败,请刷新页面', 'error');
        return;
    }
    
    const scriptName = scriptNameEl.value.trim();
    const interfaceDoc = interfaceDocEl.value.trim();
    const provider = providerEl.value;
    
    console.log('表单数据:', { scriptName, interfaceDoc: interfaceDoc.substring(0, 50) + '...', provider });
    
    if (!scriptName || !interfaceDoc) {
        showMessage('请填写完整信息', 'error');
        return;
    }
    
    showLoading(true, 'AI 正在生成测试脚本...');
    setLoadingButton('generate-script-btn', true);
    
    try {
        const response = await fetch('/api/generate-script/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                script_name: scriptName,
                interface_doc: interfaceDoc,
                provider: provider
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentScriptId = data.script_id;
            currentScriptContent = data.script_content;
            displayScript(data.script_content);
            showMessage('测试脚本生成成功');
        } else {
            showMessage(data.message || '生成失败', 'error');
        }
    } catch (error) {
        console.error('生成脚本失败:', error);
        showMessage('网络错误', 'error');
    } finally {
        showLoading(false);
        setLoadingButton('generate-script-btn', false);
    }
}

function displayScript(code) {
    const resultSection = document.getElementById('script-result-section');
    const codeDisplay = document.getElementById('script-code-display');
    
    codeDisplay.textContent = code;
    resultSection.style.display = 'block';
}

async function handleSaveScript() {
    if (!currentScriptId) {
        showMessage('请先生成脚本', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save-script/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                script_id: currentScriptId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('脚本已保存到文件');
        } else {
            showMessage(data.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('保存失败:', error);
        showMessage('网络错误', 'error');
    }
}

async function handleExecuteScript() {
    if (!currentScriptId) {
        showMessage('请先生成脚本', 'error');
        return;
    }
    
    showLoading(true, '测试正在执行...');
    
    try {
        const response = await fetch('/api/execute-test/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                script_id: currentScriptId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentTaskId = data.task_id;
            displayExecutionResult(data.result);
            showMessage('测试执行完成');
            
            // 自动切换到测试执行 Tab
            document.querySelector('[data-tab="test-execution"]').click();
        } else {
            showMessage(data.message || '执行失败', 'error');
        }
    } catch (error) {
        console.error('执行失败:', error);
        showMessage('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

function displayExecutionResult(result) {
    const resultSection = document.getElementById('execution-result');
    
    document.getElementById('stat-total').textContent = result.total || 0;
    document.getElementById('stat-passed').textContent = result.passed || 0;
    document.getElementById('stat-failed').textContent = result.failed || 0;
    document.getElementById('stat-duration').textContent = `${(result.duration || 0).toFixed(1)}s`;
    
    resultSection.style.display = 'block';
}

// ==================== 模块 3: 测试执行 ====================

function initTestExecutionModule() {
    const refreshBtn = document.getElementById('refresh-scripts-btn');
    const viewReportBtn = document.getElementById('view-report-btn');
    const analyzeBtn = document.getElementById('analyze-report-btn');
    
    refreshBtn.addEventListener('click', loadScriptsList);
    viewReportBtn.addEventListener('click', handleViewReport);
    analyzeBtn.addEventListener('click', () => {
        if (currentTaskId) {
            document.querySelector('[data-tab="report-analysis"]').click();
            document.getElementById('task-select').value = currentTaskId;
        }
    });
}

async function loadScriptsList() {
    try {
        const response = await fetch('/api/script-list/');
        const data = await response.json();
        
        if (data.success) {
            displayScriptsList(data.scripts);
        } else {
            showMessage('加载失败', 'error');
        }
    } catch (error) {
        console.error('加载脚本列表失败:', error);
        showMessage('网络错误', 'error');
    }
}

function displayScriptsList(scripts) {
    const container = document.getElementById('scripts-list');
    
    if (scripts.length === 0) {
        container.innerHTML = '<p class="empty-tip">暂无可用脚本</p>';
        return;
    }
    
    container.innerHTML = scripts.map(script => `
        <div class="list-item" onclick="selectScript(${script.id})">
            <div class="list-item-title">${escapeHtml(script.name)}</div>
            <div class="list-item-meta">
                <span class="status-badge status-${script.status}">${script.status}</span>
                <span>${script.created_at}</span>
            </div>
        </div>
    `).join('');
}

function selectScript(scriptId) {
    currentScriptId = scriptId;
    showMessage(`已选择脚本 #${scriptId}`);
    
    // 自动执行
    handleExecuteScriptById(scriptId);
}

async function handleExecuteScriptById(scriptId) {
    showLoading(true, '测试正在执行...');
    
    try {
        const response = await fetch('/api/execute-test/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ script_id: scriptId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentTaskId = data.task_id;
            displayExecutionResult(data.result);
            showMessage('测试执行完成');
        } else {
            showMessage(data.message || '执行失败', 'error');
        }
    } catch (error) {
        console.error('执行失败:', error);
        showMessage('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

function handleViewReport() {
    showMessage('报告文件已生成,请查看服务器 test_reports 目录', 'success');
}

// ==================== 模块 4: 报告分析 ====================

function initReportAnalysisModule() {
    const loadTasksBtn = document.getElementById('load-tasks-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    loadTasksBtn.addEventListener('click', loadTasksList);
    analyzeBtn.addEventListener('click', handleAnalyzeReport);
}

async function loadTasksList() {
    try {
        const response = await fetch('/api/task-list/');
        const data = await response.json();
        
        if (data.success) {
            displayTasksList(data.tasks);
        } else {
            showMessage('加载失败', 'error');
        }
    } catch (error) {
        console.error('加载任务列表失败:', error);
        showMessage('网络错误', 'error');
    }
}

function displayTasksList(tasks) {
    const select = document.getElementById('task-select');
    select.innerHTML = '<option value="">-- 请选择 --</option>';
    
    tasks.forEach(task => {
        const option = document.createElement('option');
        option.value = task.id;
        option.textContent = `${task.script_name} - ${task.status} (${task.passed}/${task.total})`;
        select.appendChild(option);
    });
    
    showMessage(`已加载 ${tasks.length} 个测试任务`);
}

async function handleAnalyzeReport() {
    const taskId = document.getElementById('task-select').value;
    const provider = document.getElementById('ra-provider').value;
    
    if (!taskId) {
        showMessage('请选择测试任务', 'error');
        return;
    }
    
    showLoading(true, 'AI 正在分析报告...');
    
    try {
        const response = await fetch('/api/analyze-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                task_id: parseInt(taskId),
                provider: provider
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAnalysisResult(data.analysis);
            showMessage('报告分析完成');
        } else {
            showMessage(data.message || '分析失败', 'error');
        }
    } catch (error) {
        console.error('分析失败:', error);
        showMessage('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

function displayAnalysisResult(analysis) {
    const resultSection = document.getElementById('analysis-result');
    const contentEl = document.getElementById('analysis-content');
    
    // 简单的 Markdown 转 HTML
    const html = simpleMarkdownToHtml(analysis);
    contentEl.innerHTML = html;
    
    resultSection.style.display = 'block';
}

function simpleMarkdownToHtml(text) {
    // 简化版 Markdown 转换
    return text
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// ==================== 工具函数 ====================

function setLoadingButton(btnId, loading) {
    const btn = document.getElementById(btnId);
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    if (loading) {
        btn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
