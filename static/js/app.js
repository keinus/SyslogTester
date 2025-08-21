// Syslog Parser Application JavaScript

const API_BASE_URL = 'http://localhost:8001';

// Examples from database
let examples = {
    "3164": [],
    "5424": []
};

// Utility functions
function showStatus(message, isError = false) {
    const statusContainer = document.getElementById('statusContainer');
    const statusMessage = document.getElementById('statusMessage');
    
    statusMessage.textContent = message;
    statusMessage.className = `status ${isError ? 'error' : 'success'}`;
    statusContainer.classList.remove('hidden');
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        statusContainer.classList.add('hidden');
    }, 5000);
}

function hideStatus() {
    document.getElementById('statusContainer').classList.add('hidden');
}

function hideResults() {
    document.getElementById('resultContainer').classList.add('hidden');
    document.getElementById('transmissionInfo').classList.add('hidden');
    document.getElementById('saveExampleSection').classList.add('hidden');
}

function setLoading(btnId, loaderId, textId, isLoading) {
    const btn = document.getElementById(btnId);
    const loader = document.getElementById(loaderId);
    const text = document.getElementById(textId);
    
    btn.disabled = isLoading;
    if (isLoading) {
        loader.classList.remove('hidden');
        text.textContent = text.textContent.replace('...', '') + '...';
    } else {
        loader.classList.add('hidden');
        text.textContent = text.textContent.replace('...', '');
    }
}

// Example management functions
async function loadExamples() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/examples/`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.examples) {
                examples["3164"] = data.examples.filter(ex => ex.rfc_version === "3164");
                examples["5424"] = data.examples.filter(ex => ex.rfc_version === "5424");
            }
        }
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

async function saveExample(name, description, rfcVersion, rawMessage) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/examples/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description,
                rfc_version: rfcVersion,
                raw_message: rawMessage
            })
        });
        
        const data = await response.json();
        if (data.success) {
            await loadExamples();
            updateExamples();
            showStatus(`Example "${name}" saved successfully!`);
        } else {
            showStatus(`Failed to save example: ${data.error}`, true);
        }
    } catch (error) {
        showStatus(`Error saving example: ${error.message}`, true);
    }
}

async function deleteExample(exampleId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/examples/${exampleId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            await loadExamples();
            updateExamples();
            showStatus('Example deleted successfully!');
        } else {
            showStatus(`Failed to delete example: ${data.error}`, true);
        }
    } catch (error) {
        showStatus(`Error deleting example: ${error.message}`, true);
    }
}

// Example management
function updateExamples() {
    const rfcVersion = document.getElementById('exampleRfcVersion').value;
    const container = document.getElementById('exampleMessages');
    const rfcExamples = examples[rfcVersion];
    
    container.innerHTML = '';
    
    // Show examples from database
    if (rfcExamples.length > 0) {        
        rfcExamples.forEach((example) => {
            const div = document.createElement('div');
            div.className = 'example-item';
            div.onclick = () => useExample(example);
            
            let displayText = example.raw_message;
            if (displayText.length > 150) {
                displayText = displayText.substring(0, 147) + '...';
            }
            
            div.innerHTML = `
                <div class="example-preview">
                    <strong>${example.name}</strong>
                    ${example.description ? `<br><small>${example.description}</small>` : ''}
                    <br>${displayText}
                </div>
                <div class="example-actions">
                    <button onclick="event.stopPropagation(); deleteExample(${example.id})" class="delete-btn" title="Delete example">🗑️</button>
                    ${example.raw_message.length > 150 ? '<span class="example-tooltip" title="' + example.raw_message + '">🔍</span>' : ''}
                </div>
            `;
            
            container.appendChild(div);
        });
    } else {
        // Show message when no examples available
        const noExamples = document.createElement('div');
        noExamples.className = 'no-examples';
        noExamples.innerHTML = `
            <p style="text-align: center; color: #6b7280; padding: 20px;">
                No examples available for RFC ${rfcVersion}.<br>
                Create messages and save them as examples to see them here.
            </p>
        `;
        container.appendChild(noExamples);
    }
}

function useExample(example) {
    const inputMode = document.getElementById('inputMode').value;
    const exampleMessage = example.raw_message;
    const rfcVersion = example.rfc_version;
    
    if (inputMode === 'raw') {
        document.getElementById('syslogMessage').value = exampleMessage;
        document.getElementById('rfcVersion').value = rfcVersion;
        showStatus(`Example "${example.name}" loaded successfully!`);
    } else {
        // Parse the example and fill component fields
        document.getElementById('rfcVersion').value = rfcVersion;
        toggleRfcFields();
        
        // Extract message part from syslog format
        const messageContent = extractMessageFromSyslog(exampleMessage, rfcVersion);
        const messageMode = document.getElementById('messageMode').value;
        
        if (messageMode === 'components') {
            // Parse message into components
            const components = parseMessageToComponents(messageContent);
            populateMessageComponents(components);
            showStatus(`Example "${example.name}" loaded as components!`);
        } else {
            // Switch to component mode and ask user
            const confirmSwitch = confirm('This example contains key=value data. Switch to Key-Value Components mode for better editing?');
            if (confirmSwitch) {
                document.getElementById('messageMode').value = 'components';
                toggleMessageMode();
                const components = parseMessageToComponents(messageContent);
                populateMessageComponents(components);
                showStatus(`Example "${example.name}" loaded in Components mode!`);
            } else {
                // Load as simple text
                document.getElementById('message').value = messageContent;
                showStatus(`Example "${example.name}" loaded as text!`);
            }
        }
    }
}

// UI toggle functions
function toggleRfcFields() {
    const rfcVersion = document.getElementById('rfcVersion').value;
    const rfc3164Fields = document.getElementById('rfc3164Fields');
    const rfc5424Fields = document.getElementById('rfc5424Fields');
    
    if (rfcVersion === '5424') {
        rfc3164Fields.classList.add('hidden');
        rfc5424Fields.classList.remove('hidden');
    } else {
        rfc3164Fields.classList.remove('hidden');
        rfc5424Fields.classList.add('hidden');
    }
}

function toggleMessageMode() {
    const messageMode = document.getElementById('messageMode').value;
    const textSection = document.getElementById('textMessageSection');
    const componentSection = document.getElementById('componentMessageSection');
    
    if (messageMode === 'components') {
        textSection.classList.add('hidden');
        componentSection.classList.remove('hidden');
        // Add initial component if none exist
        if (document.getElementById('messageComponents').children.length === 0) {
            addMessageComponent();
        }
    } else {
        textSection.classList.remove('hidden');
        componentSection.classList.add('hidden');
    }
}

function toggleInputMode() {
    const inputMode = document.getElementById('inputMode').value;
    const rawSection = document.getElementById('rawInputSection');
    const componentSection = document.getElementById('componentInputSection');
    const generateButtons = document.querySelector('.button-group');
    const rawButtons = document.getElementById('rawModeButtons');
    
    if (inputMode === 'raw') {
        rawSection.classList.remove('hidden');
        componentSection.classList.add('hidden');
        generateButtons.classList.add('hidden');
        rawButtons.classList.remove('hidden');
    } else {
        rawSection.classList.add('hidden');
        componentSection.classList.remove('hidden');
        generateButtons.classList.remove('hidden');
        rawButtons.classList.add('hidden');
    }
}

// Result display functions
function showResults(data) {
    const resultContainer = document.getElementById('resultContainer');
    const parsedData = document.getElementById('parsedData');
    
    if (data.parsed_message) {
        const msg = data.parsed_message;
        let html = `
            <div class="data-item">
                <div class="data-label">RFC Version</div>
                <div class="data-value">${msg.rfc_version || 'Unknown'}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Priority</div>
                <div class="data-value">${msg.priority}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Facility</div>
                <div class="data-value">${msg.facility}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Severity</div>
                <div class="data-value">${msg.severity}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Timestamp</div>
                <div class="data-value">${msg.timestamp}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Hostname</div>
                <div class="data-value">${msg.hostname}</div>
            </div>
        `;
        
        // RFC specific fields
        if (msg.rfc_version === '5424') {
            html += `
                <div class="data-item">
                    <div class="data-label">Version</div>
                    <div class="data-value">${msg.version || 'N/A'}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">App Name</div>
                    <div class="data-value">${msg.app_name || 'N/A'}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Process ID</div>
                    <div class="data-value">${msg.proc_id || 'N/A'}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Message ID</div>
                    <div class="data-value">${msg.msg_id || 'N/A'}</div>
                </div>
                <div class="data-item" style="grid-column: 1 / -1;">
                    <div class="data-label">Structured Data</div>
                    <div class="data-value code-block">${msg.structured_data || 'N/A'}</div>
                </div>
            `;
        } else {
            html += `
                <div class="data-item">
                    <div class="data-label">Tag</div>
                    <div class="data-value">${msg.tag || 'N/A'}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">PID</div>
                    <div class="data-value">${msg.pid || 'N/A'}</div>
                </div>
            `;
        }
        
        html += `
            <div class="data-item" style="grid-column: 1 / -1;">
                <div class="data-label">Message</div>
                <div class="data-value">${msg.message}</div>
            </div>
        `;
        
        parsedData.innerHTML = html;
        resultContainer.classList.remove('hidden');
    }
}

function showTransmissionInfo(sentTo) {
    if (sentTo) {
        const transmissionInfo = document.getElementById('transmissionInfo');
        const transmissionDetails = document.getElementById('transmissionDetails');
        
        transmissionDetails.innerHTML = `
            <div class="data-item">
                <div class="data-label">Sent To</div>
                <div class="data-value">${sentTo}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Status</div>
                <div class="data-value">✅ Successfully Transmitted</div>
            </div>
        `;
        transmissionInfo.classList.remove('hidden');
    }
}

function showGeneratedMessage(generatedMessage) {
    if (generatedMessage) {
        const transmissionInfo = document.getElementById('transmissionInfo');
        const transmissionDetails = document.getElementById('transmissionDetails');
        
        transmissionDetails.innerHTML = `
            <div class="data-item" style="grid-column: 1 / -1;">
                <div class="data-label">Generated Message</div>
                <div class="data-value code-block">${generatedMessage}</div>
            </div>
        `;
        transmissionInfo.classList.remove('hidden');
    }
}


// Component input helper
function getMessageComponents() {
    const rfcVersion = document.getElementById('rfcVersion').value;
    const components = {
        rfc_version: rfcVersion
    };
    
    // Get priority, facility, severity
    const priority = document.getElementById('priority').value;
    const facility = document.getElementById('facility').value;
    const severity = document.getElementById('severity').value;
    
    if (priority) components.priority = parseInt(priority);
    if (facility) components.facility = parseInt(facility);
    if (severity) components.severity = parseInt(severity);
    
    // Get timestamp
    const timestamp = document.getElementById('timestamp').value.trim();
    if (timestamp) components.timestamp = timestamp;
    
    // Get hostname
    const hostname = document.getElementById('hostname').value.trim();
    if (hostname) components.hostname = hostname;
    
    // Get message based on message mode
    const messageMode = document.getElementById('messageMode').value;
    if (messageMode === 'components') {
        const componentMessage = getMessageFromComponents();
        if (componentMessage) components.message = componentMessage;
    } else {
        const message = document.getElementById('message').value.trim();
        if (message) components.message = message;
    }
    
    // RFC specific fields
    if (rfcVersion === '5424') {
        const appName = document.getElementById('appName').value.trim();
        const procId = document.getElementById('procId').value.trim();
        const msgId = document.getElementById('msgId').value.trim();
        const structuredData = document.getElementById('structuredData').value.trim();
        
        if (appName) components.app_name = appName;
        if (procId) components.proc_id = procId;
        if (msgId) components.msg_id = msgId;
        if (structuredData) components.structured_data = structuredData;
    } else {
        const tag = document.getElementById('tag').value.trim();
        const pid = document.getElementById('pid').value;
        
        if (tag) components.tag = tag;
        if (pid) components.pid = parseInt(pid);
    }
    
    return components;
}

// Save current example functionality
let lastGeneratedMessage = null;
let lastRfcVersion = null;

function saveCurrentExample() {
    const name = document.getElementById('exampleName').value.trim();
    const description = document.getElementById('exampleDescription').value.trim();
    
    if (!name) {
        showStatus('Please enter an example name', true);
        return;
    }
    
    if (!lastGeneratedMessage || !lastRfcVersion) {
        showStatus('No message to save. Please generate a message first.', true);
        return;
    }
    
    saveExample(name, description || null, lastRfcVersion, lastGeneratedMessage);
    
    // Clear the form
    document.getElementById('exampleName').value = '';
    document.getElementById('exampleDescription').value = '';
}

function showSaveExampleSection(generatedMessage, rfcVersion) {
    lastGeneratedMessage = generatedMessage;
    lastRfcVersion = rfcVersion;
    
    const saveSection = document.getElementById('saveExampleSection');
    saveSection.classList.remove('hidden');
}

// Message component management functions
function addMessageComponent(key = '', value = '') {
    const container = document.getElementById('messageComponents');
    const componentId = 'component_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
    
    const div = document.createElement('div');
    div.className = 'message-component';
    div.id = componentId;
    
    // Create elements separately to avoid event binding issues
    const keyInput = document.createElement('input');
    keyInput.type = 'text';
    keyInput.placeholder = 'Key';
    keyInput.value = key;
    keyInput.className = 'component-key';
    
    const equalSpan = document.createElement('span');
    equalSpan.textContent = '=';
    
    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.placeholder = 'Value';
    valueInput.value = value;
    valueInput.className = 'component-value';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'random-checkbox';
    checkbox.title = 'Generate random value';
    checkbox.addEventListener('change', function() {
        toggleRandomValue(componentId);
    });
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = '❌';
    removeButton.title = 'Remove component';
    removeButton.addEventListener('click', function() {
        removeMessageComponent(componentId);
    });
    
    // Append all elements
    div.appendChild(keyInput);
    div.appendChild(equalSpan);
    div.appendChild(valueInput);
    div.appendChild(checkbox);
    div.appendChild(removeButton);
    
    container.appendChild(div);
}

function removeMessageComponent(componentId) {
    const component = document.getElementById(componentId);
    if (component) {
        component.remove();
    }
}

// Random value generation functions
function generateRandomValue(key) {
    const keyLower = key.toLowerCase();
    
    // Common patterns for different types of values
    if (keyLower.includes('ip') || keyLower.includes('addr')) {
        return generateRandomIP();
    } else if (keyLower.includes('port')) {
        return Math.floor(Math.random() * 65536).toString();
    } else if (keyLower.includes('time') || keyLower.includes('date')) {
        return new Date().toISOString().slice(0, 19) + 'Z';
    } else if (keyLower.includes('id') || keyLower.includes('pid')) {
        return Math.floor(Math.random() * 99999 + 1).toString();
    } else if (keyLower.includes('size') || keyLower.includes('byte') || keyLower.includes('length')) {
        return Math.floor(Math.random() * 1048576 + 1).toString();
    } else if (keyLower.includes('status') || keyLower.includes('action')) {
        const actions = ['accept', 'deny', 'block', 'allow', 'success', 'failed'];
        return actions[Math.floor(Math.random() * actions.length)];
    } else if (keyLower.includes('level') || keyLower.includes('severity')) {
        const levels = ['info', 'warning', 'error', 'debug', 'notice'];
        return levels[Math.floor(Math.random() * levels.length)];
    } else if (keyLower.includes('type')) {
        const types = ['traffic', 'utm', 'event', 'system', 'security'];
        return types[Math.floor(Math.random() * types.length)];
    } else if (keyLower.includes('name') || keyLower.includes('user')) {
        const names = ['admin', 'user1', 'guest', 'operator', 'test'];
        return names[Math.floor(Math.random() * names.length)];
    } else {
        // Generic random string
        return 'random_' + Math.random().toString(36).substring(2, 10);
    }
}

function generateRandomIP() {
    return Math.floor(Math.random() * 256) + '.' +
           Math.floor(Math.random() * 256) + '.' +
           Math.floor(Math.random() * 256) + '.' +
           Math.floor(Math.random() * 256);
}

function toggleRandomValue(componentId) {
    const component = document.getElementById(componentId);
    if (!component) {
        console.error('Component not found:', componentId);
        return;
    }
    
    const checkbox = component.querySelector('.random-checkbox');
    const valueInput = component.querySelector('.component-value');
    const keyInput = component.querySelector('.component-key');
    
    if (!checkbox || !valueInput || !keyInput) {
        console.error('Component elements not found in:', componentId);
        return;
    }
    
    if (checkbox.checked) {
        valueInput.disabled = true;
        valueInput.style.backgroundColor = '#f3f4f6';
        valueInput.style.color = '#6b7280';
        
        // Generate random value based on key
        const key = keyInput.value.trim();
        if (key) {
            valueInput.value = generateRandomValue(key);
        } else {
            valueInput.value = 'random_' + Math.random().toString(36).substring(2, 10);
        }
    } else {
        valueInput.disabled = false;
        valueInput.style.backgroundColor = '';
        valueInput.style.color = '';
    }
}

function getMessageFromComponents() {
    const components = document.querySelectorAll('.message-component');
    const pairs = [];
    
    components.forEach(component => {
        const key = component.querySelector('.component-key').value.trim();
        const valueInput = component.querySelector('.component-value');
        const checkbox = component.querySelector('.random-checkbox');
        
        let value = valueInput.value.trim();
        
        // If random checkbox is checked, generate new random value
        if (checkbox.checked && key) {
            value = generateRandomValue(key);
            valueInput.value = value; // Update the display
        }
        
        if (key && value) {
            pairs.push(`${key}=${value}`);
        }
    });
    
    return pairs.join(' ');
}

// Syslog message extraction functions
function extractMessageFromSyslog(syslogMessage, rfcVersion) {
    try {
        if (rfcVersion === '5424') {
            // RFC 5424 format: <priority>version timestamp hostname app-name procid msgid structured-data msg
            // Example: <189>1 2024-08-20T14:30:45.123Z FortiGate-100E fortigate 1001 0000000013 [fortinet@32473 devid="FG100E1234567890"] type=traffic subtype=forward...
            
            const rfc5424Pattern = /^<\d+>\d+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:\[.*?\]\s+)?(.*)$/;
            const match = syslogMessage.match(rfc5424Pattern);
            if (match) {
                return match[1].trim();
            }
        } else {
            // RFC 3164 format: <priority>timestamp hostname tag[pid]: message
            // Example: <189>date=2024-08-20 time=14:30:45 devname=FortiGate-100E...
            
            // For FortiGate messages that start with date=, extract everything after priority
            if (syslogMessage.includes('date=')) {
                const priorityEndIndex = syslogMessage.indexOf('>') + 1;
                return syslogMessage.substring(priorityEndIndex).trim();
            }
            
            // Standard RFC 3164 format
            const rfc3164Pattern = /^<\d+>\w+\s+\d+\s+\d+:\d+:\d+\s+\S+\s+\S+:\s*(.*)$/;
            const match = syslogMessage.match(rfc3164Pattern);
            if (match) {
                return match[1].trim();
            }
            
            // Fallback: extract everything after hostname
            const fallbackPattern = /^<\d+>.*?\s+\S+\s+(.*)$/;
            const fallbackMatch = syslogMessage.match(fallbackPattern);
            if (fallbackMatch) {
                return fallbackMatch[1].trim();
            }
        }
        
        // If no pattern matches, return the original message
        return syslogMessage;
    } catch (error) {
        console.error('Error extracting message from syslog:', error);
        return syslogMessage;
    }
}

// Message parsing functions
function parseMessageToComponents(message) {
    const components = [];
    
    // Check if message contains key=value patterns
    const keyValuePattern = /(\w+)=([^\s]+)/g;
    const matches = [...message.matchAll(keyValuePattern)];
    
    if (matches.length > 0) {
        // Extract key=value pairs
        matches.forEach(match => {
            const key = match[1];
            let value = match[2];
            
            // Remove quotes if present
            value = value.replace(/^["']|["']$/g, '');
            
            components.push({ key, value });
        });
    } else {
        // If no key=value pairs found, treat as single message
        components.push({ key: 'message', value: message.trim() });
    }
    
    return components;
}

function clearMessageComponents() {
    const container = document.getElementById('messageComponents');
    container.innerHTML = '';
}

function populateMessageComponents(components) {
    clearMessageComponents();
    
    components.forEach(component => {
        addMessageComponent(component.key, component.value);
    });
}

// API call functions
async function generateAndSend() {
    const components = getMessageComponents();
    const server = document.getElementById('targetServer').value.trim();
    const port = parseInt(document.getElementById('targetPort').value);
    const protocol = document.getElementById('protocol').value;

    if (!server) {
        showStatus('Please enter target server', true);
        return;
    }

    if (!port || port < 1 || port > 65535) {
        showStatus('Please enter a valid port (1-65535)', true);
        return;
    }

    hideResults();
    hideStatus();
    setLoading('generateSendBtn', 'generateSendBtnLoader', 'generateSendBtnText', true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/syslog/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                components: components,
                target_server: server,
                target_port: port,
                protocol: protocol
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response:', data);

        if (data.success) {
            showStatus('Message generated and sent successfully!');
            showResults(data);
            if (data.generated_message) {
                showGeneratedMessage(data.generated_message);
                const rfcVersion = document.getElementById('rfcVersion').value;
                showSaveExampleSection(data.generated_message, rfcVersion);
            }
            if (data.sent_to) {
                showTransmissionInfo(data.sent_to);
            }
        } else {
            showStatus(data.error || 'Unknown error occurred', true);
        }
    } catch (error) {
        console.error('Request error:', error);
        showStatus(`Connection error: ${error.message}. Make sure backend is running on ${API_BASE_URL}`, true);
    } finally {
        setLoading('generateSendBtn', 'generateSendBtnLoader', 'generateSendBtnText', false);
    }
}

async function generateOnly() {
    const components = getMessageComponents();

    hideResults();
    hideStatus();
    setLoading('generateBtn', 'generateBtnLoader', 'generateBtnText', true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/syslog/generate-only`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(components)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response:', data);

        if (data.success) {
            showStatus('Message generated successfully!');
            showResults(data);
            if (data.generated_message) {
                showGeneratedMessage(data.generated_message);
                const rfcVersion = document.getElementById('rfcVersion').value;
                showSaveExampleSection(data.generated_message, rfcVersion);
            }
        } else {
            showStatus(data.error || 'Unknown error occurred', true);
        }
    } catch (error) {
        console.error('Request error:', error);
        showStatus(`Connection error: ${error.message}. Make sure backend is running on ${API_BASE_URL}`, true);
    } finally {
        setLoading('generateBtn', 'generateBtnLoader', 'generateBtnText', false);
    }
}

async function parseAndSend() {
    const message = document.getElementById('syslogMessage').value.trim();
    const server = document.getElementById('targetServer').value.trim();
    const port = parseInt(document.getElementById('targetPort').value);
    const protocol = document.getElementById('protocol').value;
    const rfcVersion = document.getElementById('rfcVersion').value;

    if (!message) {
        showStatus('Please enter a syslog message', true);
        return;
    }

    if (!server) {
        showStatus('Please enter target server', true);
        return;
    }

    if (!port || port < 1 || port > 65535) {
        showStatus('Please enter a valid port (1-65535)', true);
        return;
    }

    hideResults();
    hideStatus();
    setLoading('sendBtn', 'sendBtnLoader', 'sendBtnText', true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/syslog/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                raw_message: message,
                target_server: server,
                target_port: port,
                protocol: protocol,
                rfc_version: rfcVersion
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response:', data);

        if (data.success) {
            showStatus('Message parsed and sent successfully!');
            showResults(data);
            showTransmissionInfo(data.sent_to);
        } else {
            showStatus(data.error || 'Unknown error occurred', true);
        }
    } catch (error) {
        console.error('Request error:', error);
        showStatus(`Connection error: ${error.message}. Make sure backend is running on ${API_BASE_URL}`, true);
    } finally {
        setLoading('sendBtn', 'sendBtnLoader', 'sendBtnText', false);
    }
}

async function parseOnly() {
    const message = document.getElementById('syslogMessage').value.trim();
    const rfcVersion = document.getElementById('rfcVersion').value;

    if (!message) {
        showStatus('Please enter a syslog message', true);
        return;
    }

    hideResults();
    hideStatus();
    setLoading('parseBtn', 'parseBtnLoader', 'parseBtnText', true);

    try {
        const formData = new FormData();
        formData.append('raw_message', message);
        formData.append('rfc_version', rfcVersion);
        
        const response = await fetch(`${API_BASE_URL}/api/syslog/parse-only`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            showStatus('Message parsed successfully!');
            showResults(data);
        } else {
            showStatus(data.error || 'Unknown error occurred', true);
        }
    } catch (error) {
        showStatus(`Connection error: ${error.message}. Make sure backend is running on ${API_BASE_URL}`, true);
    } finally {
        setLoading('parseBtn', 'parseBtnLoader', 'parseBtnText', false);
    }
}


// Initialize application
window.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Syslog Parser Application Initialized');
    
    // Initialize UI
    loadExamples().then(() => {
        updateExamples();
    });
    toggleRfcFields();
    toggleInputMode();
    toggleMessageMode();
    
    // Set default values
    document.getElementById('facility').value = '4';
    document.getElementById('severity').value = '2';
    document.getElementById('message').value = 'Test message from Syslog Parser';
    
    // Test backend connection
    fetch(`${API_BASE_URL}/api/`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Backend connection successful:', data);
            showStatus('Backend connected successfully!');
        })
        .catch(error => {
            console.error('❌ Backend connection failed:', error);
            showStatus('⚠️ Backend connection failed. Make sure the server is running at ' + API_BASE_URL, true);
        });
    
    // Add event listeners for better UX
    document.getElementById('exampleRfcVersion').addEventListener('change', updateExamples);
    document.getElementById('rfcVersion').addEventListener('change', toggleRfcFields);
    document.getElementById('inputMode').addEventListener('change', toggleInputMode);
    document.getElementById('messageMode').addEventListener('change', toggleMessageMode);
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    if (document.getElementById('inputMode').value === 'raw') {
                        parseAndSend();
                    } else {
                        generateAndSend();
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    hideResults();
                    hideStatus();
                    break;
            }
        }
    });
    
    console.log('🎉 Application ready! Use Ctrl+Enter to send, Ctrl+R to reset');
});