(function () {
  const gameDataElement = document.getElementById("gameData");
  const currentUser = gameDataElement.dataset.currentUser;
  let currentChat = null;
  let chatSocket = null;

  function openChat(type, name) {
    if (type !== "private") return;

    if (chatSocket) chatSocket.close();

    currentChat = { type, name };
    document.getElementById("chat-header").innerText = `Chat with: ${name}`;
    document.getElementById("messages").innerHTML = "";

    const wsPath = `ws://${window.location.host}/ws/chat_privet/${name}/`;
    chatSocket = new WebSocket(wsPath);

    chatSocket.onmessage = function (e) {
      const data = JSON.parse(e.data);
      console.log(data);

      if (data.type === "chat" || data.type === "chat_history") {
        const messages = document.getElementById("messages");

        (data.messages || [data]).forEach((msg) => {
          const msgClass = msg.sender === currentUser ? "message-right" : "message-left";
          messages.insertAdjacentHTML(
            "beforeend",
            `<div class="message ${msgClass}">${renderMessageContent(msg.message)}</div>`
          );
        });

        messages.scrollTop = messages.scrollHeight;
      }
    };
  }

  function renderMessageContent(message) {
    return message.startsWith("/pong_lobby")
      ? `<button class="invite-button" data-url="${message}">🔗 Pong invite</button>`
      : `<p>${message}</p>`;
  }

  document.addEventListener("click", (event) => {
    if (event.target.classList.contains("invite-button")) {
      event.preventDefault();
      const url = event.target.dataset.url;
      console.log("Navigating to:", url);
      navigate(url);
    }
  });

  document.querySelectorAll(".friend-item").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      openChat(link.dataset.type, link.dataset.name);
    });
  });

  document.getElementById("message-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const messageInput = document.getElementById("message-input").value.trim();

    if (!messageInput || !currentChat) return;

    chatSocket.send(JSON.stringify({ action: "message", message: messageInput }));
    document.getElementById("message-form").reset();
  });

  document.getElementById("game-invite-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("chat-header").textContent.split(": ")[1];
    console.log(name);
    chatSocket.send(JSON.stringify({ invite: "invite", friend: name }));
  });
})();