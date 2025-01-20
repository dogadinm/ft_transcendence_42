(function () {
    let movingDown = false;
    let movingUp = false;
    let isReady = false;


    const gameDataElement = document.getElementById("gameData");
    const room = gameDataElement.dataset.roomLobby;
    const url = `ws://${window.location.host}/ws/lobby/${room}/`;
    const chatSocket = new WebSocket(url);
    const chatGroupUrl = `ws://${window.location.host}/ws/chat_group/${room}/`;
    const chatGroupSocket = new WebSocket(chatGroupUrl);


    // Add event listeners for key events once
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data.type);


        switch (data.type) {
            case "connection":
                username = data.username;
                updateRoleDisplay(data.role);
                break;

            case "game_over":
                alert(data.winner);
                break;

            case "lobby_state":
                updateLobbyState(data.state);

                // Determine role based on lobby state
                const { left, right } = data.state;

                if (username === left.name) {
                    role = "left";
                } else if (username === right.name) {
                    role = "right";
                } else {
                    role = "spectator";
                }

                updateRoleDisplay(role);
                break;
            case "redirect":
                console.log(data.room_lobby);
                navigate(`/pong_lobby/${data.room_lobby}/`);


            case "timer_start":
                startCountdown(data.countdown);
                break;

            case `game_update_${room}`:
                fieldWidth = data.field.width;
                fieldHeight = data.field.height;
                paddleWidth = data.paddle.width;
                paddleHeight = data.paddle.height;

                drawGame(data);
                break;

            case "error":
                alert(data.lobby_message); // Display error message as an alert
                break;

            default:
                console.warn(`Unhandled message type: ${data.type}`);
        }
    };

    function sendReadySignal() {
        sendMessage({ action: "ready" });
    }

    function assignRole(newRole) {
        sendMessage({ action: "assign_role", role: newRole });
    }

    function leaveRole() {
        sendMessage({ action: "leave" });
    }

    function sendMessage(message) {
        chatSocket.send(JSON.stringify(message));
    }

    function updateRoleDisplay(role) {
        const roleElement = document.getElementById("role");
        const roleText = role === "left" || role === "right" ? `Player (${role})` : "Spectator";
        roleElement.innerText = `You are: ${roleText}`;
    }

        function startCountdown(seconds) {
        const timerElement = document.getElementById("timer");

        // Initialize the timer display
        timerElement.innerText = `Game starts in: ${seconds} seconds`;

        // Countdown interval
        const countdown = setInterval(() => {
            seconds -= 1;

            if (seconds > 0) {
                timerElement.innerText = `Game starts in: ${seconds} seconds`;
            } else {
                clearInterval(countdown); // Stop the timer
                timerElement.innerText = "Starting game...";
            }
        }, 1000);
    }

    function updateLobbyState(state) {
        const playerList = document.getElementById("players");
        const spectatorList = document.getElementById("spectators");

        // Update players with ready status
        const left = state.left.name
            ? `${state.left.name} ${state.left.ready ? "(Ready)" : ""}`
            : "Available";
        const right = state.right.name
            ? `${state.right.name} ${state.right.ready ? "(Ready)" : ""}`
            : "Available";

        playerList.innerHTML = `
            Player left: ${left}<br>
            Player right: ${right}
        `;

        // Update spectators list
        spectatorList.innerHTML = state.spectators.join("<br>");
    }

    function startCountdown(seconds) {
        const timerElement = document.getElementById("timer");
        timerElement.innerText = `Game starts in: ${seconds} seconds`;

        const countdown = setInterval(() => {
            seconds -= 1;
            timerElement.innerText = `Game starts in: ${seconds} seconds`;

            if (seconds <= 0) {
                clearInterval(countdown);
                timerElement.innerText = "Starting game...";
            }
        }, 1000);
    }

    function handleKeyDown(e) {
        if (role !== "left" && role !== "right") {
            return;
        }

        if (e.key === 'w' && !movingUp) {
            movingUp = true;
            sendMessage({ action: 'move', direction: 'up' });
        }
        if (e.key === 's' && !movingDown) {
            movingDown = true;
            sendMessage({ action: 'move', direction: 'down' });
        }
    }

    function handleKeyUp(e) {
        if( role !== "left" && role !== "right" ){
            return;
        }

        if (e.key === 'w' && movingUp) {
            movingUp = false;
            sendMessage({ action: 'stop', direction: 'up' });
        }
        if (e.key === 's' && movingDown) {
            movingDown = false;
            sendMessage({ action: 'stop', direction: 'down' });
        }
    }

    function drawGame(data) {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = fieldWidth;
        canvas.height = fieldHeight;

        ctx.clearRect(0, 0, fieldWidth, fieldHeight);

        // Set background color to green
        ctx.fillStyle = '#1abc9c';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw intermittent vertical line at the middle
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        const lineHeight = 20;
        const gap = 10;

        for (let y = 0; y < canvas.height; y += lineHeight + gap) {
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, y);
            ctx.lineTo(canvas.width / 2, y + lineHeight);
            ctx.stroke();
        }

        // Draw paddles
        ctx.fillStyle = 'white';
        ctx.fillRect(20, data.paddles.left.paddleY, paddleWidth, paddleHeight); // Left paddle
        ctx.fillRect(fieldWidth - 20 - paddleWidth, data.paddles.right.paddleY, paddleWidth, paddleHeight); // Right paddle

        // Draw ball
        ctx.beginPath();
        ctx.arc(data.ball.x, data.ball.y, 10, 0, Math.PI * 2);
        ctx.fill();

        // Draw score
        ctx.font = '20px Arial';
        ctx.fillStyle = 'white';
        const leftPlayer = data.players.left || "Left";
        const rightPlayer = data.players.right || "Right";
        const text = `${leftPlayer}: ${data.score.left}  ${'    ' + rightPlayer}: ${data.score.right}`;
        const textWidth = ctx.measureText(text).width;
        const centerX = fieldWidth / 2;
        const maxHalfWidth = fieldWidth / 2;
        const startX = Math.max(centerX - textWidth / 2, centerX - maxHalfWidth);
        ctx.fillText(text, startX, 20);
    }

    chatGroupSocket.onmessage = function (a) {
        const chat_data = JSON.parse(a.data);
        console.log(chat_data.type)
        switch (chat_data.type) {
            case `chat_message_${room}`:
                if (Array.isArray(chat_data.messages)) {
                    updateChatMessages(chat_data.messages);
                } else {
                   appendChatMessage(chat_data.message);
               }
               break;

          default:
               console.warn(`Unhandled chat message type: ${chat_data.type}`);
       }
    };

    function sendChatMessage() {
        const input = document.getElementById("chat-input");
        const message = input.value.trim();
        if (message) {
            chatGroupSocket.send(JSON.stringify({ action: "massege", message }));
            input.value = "";
        }
    }

    function updateChatMessages(messages) {
        const chatBox = document.getElementById("chat-box");
        chatBox.innerHTML = "";
        messages.forEach(appendChatMessage);
    }

    function appendChatMessage(message) {
        const chatBox = document.getElementById("chat-box");
        const messageElement = document.createElement("div");
        messageElement.className = "chat-message";
        messageElement.innerHTML = `
            <div>
                <img src="${message.photo}" alt="Photo" style="width: 30px; height: 30px; border-radius: 50%;">
                <strong>${message.sender}</strong>:
            </div>
            <div>${message.message}</div>
            <div style="font-size: 0.8em; color: gray;">${message.time}</div>
        `;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    function disconnectWebSocket() {
    if (chatSocket) {
        chatSocket.close(1000, "User disconnected"); // close with code 1000 (normal)
        console.log("Closing Lobby WebSocket...");
    }
    
    if (chatGroupSocket) {
        chatGroupSocket.close(1000, "User disconnected");
        console.log("Closing Chat WebSocket...");
    }
    navigate('/');
}

    document.getElementById("assignRightButton").addEventListener("click", () => assignRole("right"));
    document.getElementById("assignLeftButton").addEventListener("click", () => assignRole("left"));
    document.getElementById("readyButton").addEventListener("click", sendReadySignal);
    document.getElementById("leaveRoleButton").addEventListener("click", leaveRole);
    document.getElementById("leaveLobbyButton").addEventListener("click", disconnectWebSocket);
    document.getElementById("sendMessage").addEventListener("click", sendChatMessage);

})();