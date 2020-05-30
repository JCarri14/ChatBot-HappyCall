var lastInput = "";
const roomName = JSON.parse(document.getElementById('room-name').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (lastInput != data.message) {
        addListItem(data.message.sender, data.message.text);    
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('.container-submit').click();
    }
};

document.querySelector('.container-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    lastInput = message;
    addListItem("user-mssg", message);
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
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