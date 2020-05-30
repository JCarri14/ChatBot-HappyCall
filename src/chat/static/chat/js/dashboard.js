

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/control/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    addListItem(data.text);    
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector(".list-group").addEventListener("click",function(e) {
    // e.target is our targetted element.
    chat_id = e.target.innerHTML.split("_")[1]
    if(e.target && e.target.innerHTML != "None") {
        window.location.pathname = '/chat/control/' + chat_id + '/';
    }
});

document.getElementById("refresh-btn").addEventListener("click",function(e) {
    var e = document.querySelector(".list-group");   
    //e.firstElementChild can be used. 
    var child = e.lastElementChild;  
    while (child) { 
        e.removeChild(child); 
        child = e.lastElementChild; 
    }
    chatSocket.send(JSON.stringify({
        'request': 'update-conversations'
    }));
});

function addListItem(text) {
    var mssg = document.createElement("p");
    mssg.classList.add("list-group-item");
    mssg.classList.add("list-group-item-action");
    mssg.innerHTML = text;
    document.querySelector(".list-group").appendChild(mssg);
    var chat = document.querySelector(".list-group");
    chat.scrollTop = chat.scrollHeight;
}