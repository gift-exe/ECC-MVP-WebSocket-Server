const output = document.getElementById("output");
const identifier = 'monitor_1'

function logMessage(message) {
    output.textContent += message + '\n';
}

function initWebSocket() {
    const websocket = new WebSocket('ws://ecc-ws-server.onecenter.ai/monitor');

    websocket.onopen = function(evt) {
        try {
            websocket.send(identifier)
            logMessage("Connected to WebSocket server");    
        } catch (error) {
            logMessage("Error Connecting to WebSocket server: ", error);    
        }
        
    };

    websocket.onmessage = function(evt) {
        console.log("New Message from server")
        console.log(evt)
        const message = JSON.parse(evt.data);
        console.log(message.message)
        logMessage(`From Phone: ${message.message.from_phone}, Question: ${message.message.question}, Answer: ${message.message.answer}`);
    };

    websocket.onerror = function(evt) {
        logMessage(`Error: ${evt.data}`);
    };

    websocket.onclose = function(evt) {
        logMessage("Disconnected from WebSocket server");
    };
}

window.onload = initWebSocket;
