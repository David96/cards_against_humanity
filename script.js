
var ws, username,
    cardczar = false,
    initialized = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Content loaded');
    var form = document.getElementById('join');
    form.addEventListener('submit', function (event) {
        var data = new FormData(form);
        username = data.get('name');
        ws = new WebSocket("ws://127.0.0.1:6790/");
        ws.onopen = onOpen;
        ws.onmessage = onMessage;

        event.preventDefault();
    });
});

function onMessage(event) {
    data = JSON.parse(event.data);
    switch (data.type) {
        case 'state':
            console.log('Got state message');
            if (!initialized) {
                initGame();
            }
            renderState(data.state);
            break;
        case 'user':
            console.log('Got user message');
            createUserList(data.players);
            break;
        case 'message':
            console.log('Got message: ' + data.msg)
            addMessage(data.msg);
            break;
        case 'error':
            console.log('Got error: ' + data.msg)
            addMessage(data.msg, true);
            break
    }
}

function onCardClicked(event) {
    var card = event.target;
    var table = document.getElementById('table');
    if (table.contains(card)) {
        var cardList = card.parentNode.childNodes;
        var words = [];
        cardList.forEach((card) => {
            words.push(card.innerText);
        });
        ws.send(JSON.stringify({action: 'select_cards', cards: words}));
    } else {
        ws.send(JSON.stringify({action: 'play_cards', cards: [event.target.innerText]}));
    }
}

function createCard(text, black = false) {
    var card = document.createElement('button');
    card.addEventListener('click', onCardClicked);
    card.appendChild(document.createTextNode(text));
    card.className = "card";
    if (black) {
        card.classList.add("black");
    }
    return card;
}

function renderState(state) {
    var table = document.getElementById('table');
    var hand = document.getElementById('hand');
    table.innerHTML = '';
    hand.innerHTML = '';
    table.appendChild(createCard(state.current, true));
    state.table.forEach((cardList) => {
        var cardListElement = document.createElement('div');
        cardListElement.className = 'cardlist';
        cardList.forEach((card) => {
            cardListElement.appendChild(createCard(card));
        });
        table.appendChild(cardListElement);
    });
    state.hand.forEach((card) => {
        hand.appendChild(createCard(card));
    });
}

function addMessage(msg, is_error) {
    var messages = document.getElementById('messagelist'),
        message = document.createElement('li'),
        content = document.createTextNode(msg);
    if (is_error) {
        message.className = 'error';
    }
    message.appendChild(content);
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
}
function createUserList(users) {
    console.log('creating user list');
    var list = document.getElementById('userlist');
    list.innerText = '';
    users.forEach((user) => {
        var li = document.createElement('li');
        var text = user.name;
        if (user.cardczar) {
            text += " (Card Czar)";
        }
        text += " (" + user.score + ")";
        li.appendChild(document.createTextNode(text));
        list.appendChild(li);
    });
}

function onOpen() {
    console.log('setting name: ' + username);
    ws.send(JSON.stringify({action: "set_name", name: username}));
}

function initGame() {
    initialized = true;
    var form = document.getElementById('join');
    form.className = 'join hidden';
}
