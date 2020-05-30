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
    console.log(data);
    if (data.messages) {
        for (message of data.messages) {
            addListItem(message.sender, message.text);    
        }
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