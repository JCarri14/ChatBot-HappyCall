

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/control/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.message)
    addListItem(data.message.sender, data.message.text);    
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector(".list-group").addEventListener("click",function(e) {
    // e.target is our targetted element.
    console.log(e.target.innerHTML + " was clicked");
    if(e.target && e.target.innerHTML != "None") {
        window.location.pathname = '/dashboard/chat/control/' + e.target.innerHTML + '/';
    }
});

document.getElementById("refresh-btn").addEventListener("click",function(e) {
    console.log("Button clicked!")
    chatSocket.send(JSON.stringify({
        'request': 'update-conversations'
    }));
});

function addListItem(className, text) {
    var mssg = document.createElement("p");
    mssg.classList.add(className);
    mssg.innerHTML = text;
    document.querySelector(".list-group").appendChild(mssg);
    var chat = document.querySelector(".list-group");
    chat.scrollTop = chat.scrollHeight;
}