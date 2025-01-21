(function () {
  const gameDataElement = document.getElementById('gameData');
  const currentUser = gameDataElement.dataset.currentUser;
  const profileBaseUrl = gameDataElement.dataset.profileBaseUrl;
  let currentChat = null;

  if (chatSocket) {
    chatSocket.close();
  }

  function openChat(type, name) {
    if (chatSocket) {
      chatSocket.close();
    }

    currentChat = { type, name };

    if (type === "private") {
      document.getElementById('chat-header').innerText = `Chat with: ${name}`;
    } else {
      // Remove logic for group chats
      return;
    }

    document.getElementById('messages').innerHTML = '';

    const wsPath = `ws://${window.location.host}/ws/chat_privet/${name}/`;

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
              `
              <div class="message ${msgClass}">
                <p>${msg.message.startsWith('http') ? `<a href="${msg.message}" target="_blank">${msg.message}</a>` : msg.message}</p>
              </div>
            `
            );
          });
        } else {
          messages.insertAdjacentHTML(
            'beforeend',
            `
            <div class="message ${messageClass}"><p>${data.message.startsWith('http') ? `<a href="${data.message}" target="_blank">${data.message}</a>` : data.message}</p></div>
          `
          );
        }

        messages.scrollTop = messages.scrollHeight;
      }
    };

    chatSocket.onclose = function () {
      console.log('Chat socket closed');
    };
  }

  document.querySelectorAll('.friend-item').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const chatType = link.dataset.type;
      const chatName = link.dataset.name;
      if (chatType === "private") {
        openChat(chatType, chatName);
      }
    });
  });

  document.getElementById('message-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const messageInput = document.getElementById('message-input').value.trim();

    if (!messageInput || !currentChat) return;

    chatSocket.send(JSON.stringify({
      action: 'massege',
      message: messageInput
    }));
    document.getElementById('message-form').reset();
  });

  document.getElementById('game-invite-form').addEventListener('submit', (e) => {
    e.preventDefault();
    let a = document.getElementById('chat-header');
    let name = a.textContent.split(': ')[1]; // Extract username after "Chat with: "
    console.log(name); // Output: admin
    chatSocket.send(JSON.stringify({
      invite: 'invite',
      friend: name,
    }));
  });
})();