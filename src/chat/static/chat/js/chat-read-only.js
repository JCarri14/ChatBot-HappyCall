var lastInput = "";
const roomName = JSON.parse(document.getElementById('room-name').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/control/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.message) {
        addListItem(data.message.sender, data.message.text);    
    }
    if (data.data) {
        treatIncomingData(data.data);
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};


function addListItem(className, text) {
    var mssgItem = document.createElement("li");
    mssgItem.classList.add(className);
    var mssg = document.createElement("p");
    mssg.innerHTML = text;
    mssgItem.appendChild(mssg);
    document.querySelector(".chat-messages ul").appendChild(mssgItem);
    var chat = document.querySelector(".chat-messages");
    chat.scrollTop = chat.scrollHeight;
}

function addSentimentItem(sentiment, value) {
    var mssgItem = document.createElement("li");
    mssgItem.classList.add("list-group-item");

    var mssgValue = document.createElement("b");
    mssgValue.appendChild(document.createTextNode(value));
    mssgItem.appendChild( document.createTextNode(sentiment + ": "));
    mssgItem.appendChild(mssgValue);

    document.querySelector("#witness_sentiments").appendChild(mssgItem);
}

function removeAllChilds(element) {
    var e = document.querySelector(element);   
    //e.firstElementChild can be used. 
    var child = e.lastElementChild;  
    while (child) { 
        e.removeChild(child); 
        child = e.lastElementChild; 
    }
}

function treatIncomingData(data) {
    for (var key in data) {
        console.log(data[key])
        if (Array.isArray(data[key])) {
            for (i in data[key]) {
                document.getElementById(key).innerHTML += data[key][i] + "<br>";
            }
        } else {
            if (typeof data[key] === "object") {
                if (key == "witness_sentiments") {
                    removeAllChilds("#witness_sentiments");
                    for (var k in data[key]) {
                        addSentimentItem(k, data[key][k]);
                    }
                }
            } else {
                document.getElementById(key).innerHTML = data[key];
            }
        }
    }
}