(function () {
    const gameDataElement = document.getElementById('gameData');
    const currentUser =  gameDataElement.dataset.currentUser;
    const profileBaseUrl = gameDataElement.dataset.profileBaseUrl;
    let chatSocket = null;
    let currentChat = null;

    function openChat(type, name) {

        if (chatSocket) {
            chatSocket.close();
        }

        currentChat = { type, name };

        if (type === "private") {
            document.getElementById('chat-header').innerText = `Chat with: ${name}`;
        } else if (type === "group") {
            document.getElementById('chat-header').innerText = `Group: ${name}`;
        }

        document.getElementById('messages').innerHTML = '';

        const wsPath = type === "private"
            ? `ws://${window.location.host}/ws/chat_privet/${name}/`
            : `ws://${window.location.host}/ws/chat_group/${name}/`;

        chatSocket = new WebSocket(wsPath);

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            console.log(data)
            if (data.type === 'chat' || data.type === 'chat_history') {
                const messages = document.getElementById('messages');
                const messageClass = data.sender === currentUser ? 'message-right' : 'message-left';
                if (data.messages) {
                    data.messages.forEach((msg) => {

                        const msgClass = msg.sender === currentUser ? 'message-right' : 'message-left';
                        messages.insertAdjacentHTML(
                            'beforeend',
                            `<div class="message ${msgClass}"><p>${msg.message}</p></div>`
                        );
                    });
                } else {
                    if (type === "private") {
                        messages.insertAdjacentHTML(
                        'beforeend',
                        `<div class="message ${messageClass}"><p>${data.message}</p></div>`
                    );
                    } else if (type === "group") {
                        messages.insertAdjacentHTML(
                        'beforeend',
                        `<div class="message ${messageClass}"><p>${data.message.message}</p></div>`
                    );
                    }

                }
                messages.scrollTop = messages.scrollHeight;
            }
        };

        chatSocket.onclose = function () {
            console.log('Chat socket closed');
        };
    }

    document.querySelectorAll('.friend-item, .group-item').forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const chatType = link.dataset.type;
            const chatName = link.dataset.name;
            openChat(chatType, chatName);
        });
    });

    document.getElementById('message-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const messageInput = document.getElementById('message-input').value.trim();

        if (!messageInput || !currentChat) return;

        chatSocket.send(JSON.stringify({
            action: 'massege',
            message: messageInput }));
        document.getElementById('message-form').reset();
    });


    const statusSocket = new WebSocket(`ws://${window.location.host}/ws/status/`);

    statusSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data.type);

        if (data.type === 'user_status') {
            const friendItems = document.querySelectorAll('.friend-item');
            const onlineUsernames = new Set(data.users || []);

            friendItems.forEach((item) => {
                const name = item.dataset.name;
                const statusIndicator = item.querySelector('.status-indicator');

                if (onlineUsernames.has(name)) {
                    statusIndicator.classList.remove('offline');
                    statusIndicator.classList.add('online');
                    statusIndicator.style.backgroundColor = 'green';
                } else {
                    statusIndicator.classList.remove('online');
                    statusIndicator.classList.add('offline');
                    statusIndicator.style.backgroundColor = 'red';
                }
            });
        }
    };

    statusSocket.onclose = function () {
        console.log("Status WebSocket closed");
    };
})();