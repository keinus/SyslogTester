// Syslog Parser Application JavaScript

const API_BASE_URL = 'http://localhost:8001';

// Example messages with FortiGate examples
const examples = {
    "3164": [
        // Standard RFC 3164 examples
        "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8",
        "<165>Aug 24 05:34:00 mymachine myproc[10]: %% It's time to make the do-nuts. %%",
        "<0>Oct 22 10:52:01 scapegoat sched[0]: That's All Folks!",
        // FortiGate RFC 3164 examples
        "<189>date=2024-08-20 time=14:30:45 devname=FortiGate-100E devid=FG100E1234567890 logid=0000000013 type=traffic subtype=forward level=notice vd=root eventtime=1724159445 srcip=192.168.1.100 srcname=client01 srcport=12345 srcintf=internal dstip=8.8.8.8 dstname=dns.google dstport=53 dstintf=wan1 policyid=5 policyname=internet_access service=DNS proto=17 action=accept policytype=policy duration=120 sentbyte=1024 rcvdbyte=2048 sentpkt=10 rcvdpkt=12 appcat=unscanned",
        "<133>date=2024-08-20 time=14:25:30 devname=FortiGate-100E devid=FG100E1234567890 logid=0001000014 type=utm subtype=virus level=warning vd=root eventtime=1724159130 srcip=192.168.1.50 srcname=workstation05 srcport=80 srcintf=internal dstip=malicious.example.com dstport=443 dstintf=wan1 policyid=3 service=HTTPS proto=6 action=blocked virus=Trojan.Generic filename=malware.exe quarskip=No-skip",
        "<134>date=2024-08-20 time=14:20:15 devname=FortiGate-100E devid=FG100E1234567890 logid=0100032001 type=event subtype=system level=information vd=root eventtime=1724158815 logdesc=Admin user authenticated user=admin srcip=192.168.1.10 ui=GUI action=login status=success reason=None msg=User admin logged in successfully from 192.168.1.10"
    ],
    "5424": [
        // Standard RFC 5424 examples
        "<34>1 2003-10-11T22:14:15.003Z mymachine su - ID47 - BOM'su root' failed for lonvick on /dev/pts/8",
        "<165>1 2021-08-24T05:34:00.000Z mymachine myproc 10 ID123 - %% It's time to make the do-nuts. %%",
        "<0>1 2021-10-22T10:52:01.000Z scapegoat sched 0 ID001 - That's All Folks!",
        // FortiGate RFC 5424 examples  
        "<189>1 2024-08-20T14:30:45.123Z FortiGate-100E fortigate 1001 0000000013 [fortinet@32473 devid=\"FG100E1234567890\" vd=\"root\" eventtime=\"1724159445\"] type=traffic subtype=forward level=notice srcip=192.168.1.100 dstip=8.8.8.8 action=accept",
        "<133>1 2024-08-20T14:25:30.456Z FortiGate-100E fortigate 2001 0001000014 [fortinet@32473 devid=\"FG100E1234567890\" vd=\"root\" eventtime=\"1724159130\"] type=utm subtype=virus level=warning srcip=192.168.1.50 action=blocked virus=Trojan.Generic",
        "<134>1 2024-08-20T14:20:15.789Z FortiGate-100E fortigate 3001 0100032001 [fortinet@32473 devid=\"FG100E1234567890\" vd=\"root\" eventtime=\"1724158815\"] type=event subtype=system level=information user=admin action=login status=success"
    ]
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

// Example management
function updateExamples() {
    const rfcVersion = document.getElementById('exampleRfcVersion').value;
    const container = document.getElementById('exampleMessages');
    const rfcExamples = examples[rfcVersion];
    
    container.innerHTML = '';
    
    // Add category headers for better organization
    const categories = {
        '3164': ['Standard Examples', 'FortiGate Examples'],
        '5424': ['Standard Examples', 'FortiGate Examples']
    };
    
    const categoryRanges = {
        '3164': [3, 6], // First 3 are standard, next 3 are FortiGate
        '5424': [3, 6]
    };
    
    let currentCategory = 0;
    rfcExamples.forEach((example, index) => {
        // Add category header
        if (index === 0 || index === categoryRanges[rfcVersion][0]) {
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'category-header';
            categoryHeader.innerHTML = `<h4>${categories[rfcVersion][currentCategory]}</h4>`;
            container.appendChild(categoryHeader);
            currentCategory++;
        }
        
        const div = document.createElement('div');
        div.className = 'example-item';
        div.onclick = () => useExample(rfcVersion, index);
        
        // Truncate long FortiGate messages for display
        let displayText = example;
        if (example.length > 150) {
            displayText = example.substring(0, 147) + '...';
        }
        
        div.innerHTML = `
            <div class="example-preview">${displayText}</div>
            ${example.length > 150 ? `<div class="example-tooltip" title="${example}">🔍 Click to use full message</div>` : ''}
        `;
        
        container.appendChild(div);
    });
}

function useExample(rfcVersion, index) {
    const inputMode = document.getElementById('inputMode').value;
    const exampleMessage = examples[rfcVersion][index];
    
    if (inputMode === 'raw') {
        document.getElementById('syslogMessage').value = exampleMessage;
        document.getElementById('rfcVersion').value = rfcVersion;
        showStatus(`Example ${index + 1} loaded successfully!`);
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
            showStatus(`Example ${index + 1} loaded as components!`);
        } else {
            // Switch to component mode and ask user
            const confirmSwitch = confirm('This example contains key=value data. Switch to Key-Value Components mode for better editing?');
            if (confirmSwitch) {
                document.getElementById('messageMode').value = 'components';
                toggleMessageMode();
                const components = parseMessageToComponents(messageContent);
                populateMessageComponents(components);
                showStatus(`Example ${index + 1} loaded in Components mode!`);
            } else {
                // Load as simple text
                document.getElementById('message').value = messageContent;
                showStatus(`Example ${index + 1} loaded as text!`);
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

// Message component management functions
function addMessageComponent(key = '', value = '') {
    const container = document.getElementById('messageComponents');
    const componentId = 'component_' + Date.now();
    
    const div = document.createElement('div');
    div.className = 'message-component';
    div.id = componentId;
    
    div.innerHTML = `
        <input type="text" placeholder="Key" value="${key}" class="component-key">
        <span>=</span>
        <input type="text" placeholder="Value" value="${value}" class="component-value">
        <button type="button" onclick="removeMessageComponent('${componentId}')" title="Remove component">
            ❌
        </button>
    `;
    
    container.appendChild(div);
}

function removeMessageComponent(componentId) {
    const component = document.getElementById(componentId);
    if (component) {
        component.remove();
    }
}

function getMessageFromComponents() {
    const components = document.querySelectorAll('.message-component');
    const pairs = [];
    
    components.forEach(component => {
        const key = component.querySelector('.component-key').value.trim();
        const value = component.querySelector('.component-value').value.trim();
        
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
    updateExamples();
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