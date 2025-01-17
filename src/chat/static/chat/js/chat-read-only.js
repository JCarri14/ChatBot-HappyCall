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

function createItem(parentName, name, value) {
    var item = document.createElement("li");
    item.classList.add("list-group-item");

    var itemValue = document.createElement("b");
    itemValue.setAttribute("id", parentName + "_" + name.toLowerCase());
    itemValue.appendChild(document.createTextNode(value));
    item.appendChild(document.createTextNode(name + ": "));
    item.appendChild(itemValue);
    return item;
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

function toCapitalCase(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
}

function appendItemsToList(container, parent, identifier, content) {

    if (Array.isArray(content)) {
        for (v in content) {
            if (Array.isArray(content[v])) {
                container.appendChild(createItem(parent, toCapitalCase(identifier), content[v].join("<br>")));
            } else {
                container.appendChild(createItem(parent, toCapitalCase(identifier), content[v]));
            }
        }
    } else {
        container.appendChild(createItem(parent, toCapitalCase(identifier), content[v]));
    }
}

function addListGroupItem(container, parentName, itemName, itemContent) {
    if (itemContent != null) {
        console.log(itemContent[itemName])
        if (Array.isArray(itemContent[itemName])) {
            container.appendChild(createItem(parentName, toCapitalCase(itemName), itemContent[itemName].join("<br>")));
        } else {
            container.appendChild(createItem(parentName, toCapitalCase(itemName), itemContent[itemName]));
        }
    }
}

function createBlock(title, content) {
    var block = document.createElement("div");
    block.classList.add("data-block");
    block.classList.add("mb-4");
    block.setAttribute("id", title.toLowerCase());

    var blockTitle = document.createElement("h4");
    blockTitle.appendChild(document.createTextNode(toCapitalCase(title)));

    var list = document.createElement("ul");
    list.classList.add("list-group");

    for (v in content) {
        addListGroupItem(list, title, v, content[v]);
    }
    
    block.appendChild(blockTitle);
    block.appendChild(list);
    document.querySelector(".data-box").appendChild(block);
}

function update_block(key, values) {
    var parent = document.querySelector(".data-box #" + key);
    if (parent == null) {
        createBlock(key, values);
        return;
    }

    for (v in values) {
        child = document.getElementById(key+"_"+v);
        if (child == null) {
            addListGroupItem(document.querySelector("#" + key + " .list-group"), key, v, values[v]);
        } else {
            if (Array.isArray(values[v])) {
                for (i in values[v]) {
                    child.innerHTML = '';
                    child.innerHTML += values[v][i] + "<br>";
                }
            } else {
                child.innerHTML = '';
                child.innerHTML = values[v];   
            }
        }
    }
}

function treatIncomingData(data) {
    for (item in data) {
        console.log(data[item]);
        if(data[item]) {
            update_block(item, data[item]);
        }
    }
}

/*
    for (var key in data) {
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

*/