document.addEventListener('DOMContentLoaded', function() {
    const parserTypeSelect = document.getElementById('parserType');
    const methodSelect = document.getElementById('methodSelect');
    const submitBtn = document.getElementById('submitBtn');
    
    let parserInfo = {};
    
    // Инициализация
    document.getElementById('methodSection').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    
    // Обработчики событий
    parserTypeSelect.addEventListener('change', loadParserInfo);
    methodSelect.addEventListener('change', updateMethodParams);
    submitBtn.addEventListener('click', startParsing);
    
    async function loadParserInfo() {
        const parserType = parserTypeSelect.value;
        if (!parserType) {
            document.getElementById('methodSection').classList.add('hidden');
            return;
        }
        
        try {
            const response = await fetch(`/parse/info/${parserType}`);
            parserInfo = await response.json();
            
            renderParams('parserParamsContainer', parserInfo.init_params);
            populateMethods();
            
            document.getElementById('methodSection').classList.remove('hidden');
            updateMethodParams();
        } catch (error) {
            console.error('Error loading parser info:', error);
        }
    }
    
    function populateMethods() {
        methodSelect.innerHTML = '';
        
        if (!parserInfo.methods) return;
        
        for (const [method, info] of Object.entries(parserInfo.methods)) {
            const option = document.createElement('option');
            option.value = method;
            option.textContent = `${method} - ${info.description || 'No description'}`;
            methodSelect.appendChild(option);
        }
    }
    
    function updateMethodParams() {
        const method = methodSelect.value;
        if (!method) return;
        
        document.getElementById('methodName').textContent = method;
        document.getElementById('methodDescription').textContent = 
            parserInfo.methods[method]?.description || 'Описание отсутствует';
        
        renderParams('methodParamsContainer', parserInfo.methods[method].params);
        validateForm();
    }
    
    function renderParams(containerId, params) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        if (!params) return;
        
        for (const [paramName, paramInfo] of Object.entries(params)) {
            const group = document.createElement('div');
            group.className = 'param-group';
            
            const label = document.createElement('label');
            label.textContent = `${paramName} (${paramInfo.type})`;
            label.className = paramInfo.optional ? '' : 'required';
            group.appendChild(label);
            
            if (paramInfo.type === 'bool') {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `param_${paramName}`;
                checkbox.checked = paramInfo.default || false;
                group.appendChild(checkbox);
            } 
            else if (paramInfo.type === 'file') {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.id = `param_${paramName}`;
                fileInput.accept = paramInfo.extensions.join(',');
                fileInput.required = !paramInfo.optional;
                group.appendChild(fileInput);
                
                const allowed = document.createElement('p');
                allowed.textContent = `Допустимые расширения: ${paramInfo.extensions.join(', ')}`;
                group.appendChild(allowed);
            }
            else {
                const input = document.createElement('input');
                input.type = paramInfo.type === 'int' ? 'number' : 'text';
                input.id = `param_${paramName}`;
                input.value = paramInfo.default || '';
                input.required = !paramInfo.optional;
                input.addEventListener('input', validateForm);
                input.addEventListener('change', validateForm);
                group.appendChild(input);
            }
            
            const desc = document.createElement('p');
            desc.style = 'margin: 5px 0 0 0; font-size: 0.8em; color: #666;';
            desc.textContent = paramInfo.description || '';
            group.appendChild(desc);
            
            container.appendChild(group);
        }
    }
    
    function validateForm() {
        let isValid = true;
        
        // Проверяем обязательные параметры конструктора
        if (parserInfo.init_params) {
            for (const [param, info] of Object.entries(parserInfo.init_params)) {
                if (!info.optional && !checkParamValue(param, info.type)) {
                    isValid = false;
                    break;
                }
            }
        }
        
        // Проверяем обязательные параметры метода
        const method = methodSelect.value;
        if (method && parserInfo.methods && parserInfo.methods[method]) {
            for (const [param, info] of Object.entries(parserInfo.methods[method].params)) {
                if (!info.optional && !checkParamValue(param, info.type)) {
                    isValid = false;
                    break;
                }
            }
        }
        
        submitBtn.disabled = !isValid;
    }
    
    function checkParamValue(paramName, paramType) {
        const element = document.getElementById(`param_${paramName}`);
        if (!element) return false;
        
        if (element.type === 'file') {
            return element.files.length > 0;
        }
        if (element.type === 'checkbox') {
            return true;
        }
        return element.value.trim() !== '';
    }
    
    async function startParsing() {
        const parserType = parserTypeSelect.value;
        const method = methodSelect.value;
        
        const formData = new FormData();
        formData.append('parser_type', parserType);
        formData.append('method', method);
        
        // Собираем параметры конструктора
        const initParams = {};
        if (parserInfo.init_params) {
            for (const paramName in parserInfo.init_params) {
                initParams[paramName] = getParamValue(paramName, parserInfo.init_params[paramName].type);
            }
        }
        formData.append('init_params', JSON.stringify(initParams));
        
        // Собираем параметры метода
        const methodParams = {};
        if (method && parserInfo.methods && parserInfo.methods[method]) {
            for (const paramName in parserInfo.methods[method].params) {
                methodParams[paramName] = getParamValue(paramName, parserInfo.methods[method].params[paramName].type);
            }
        }
        formData.append('method_params', JSON.stringify(methodParams));
        
        // Добавляем файлы
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.files.length > 0) {
                formData.append(input.id.replace('param_', ''), input.files[0]);
            }
        });
        
        try {
            const response = await fetch('/parse/start', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const result = await response.json();
            document.getElementById('resultContent').textContent = JSON.stringify(result, null, 2);
            document.getElementById('result').classList.remove('hidden');
        } catch (error) {
            console.error('Error during parsing:', error);
            alert('Произошла ошибка при выполнении парсинга');
        }
    }
    
    function getParamValue(paramName, paramType) {
        const element = document.getElementById(`param_${paramName}`);
        if (!element) return null;
        
        if (paramType === 'bool') {
            return element.checked;
        }
        else if (paramType === 'int') {
            return parseInt(element.value) || 0;
        }
        else if (paramType === 'float') {
            return parseFloat(element.value) || 0.0;
        }
        else if (paramType === 'file') {
            return element.files[0]?.name || '';
        }
        return element.value;
    }
});