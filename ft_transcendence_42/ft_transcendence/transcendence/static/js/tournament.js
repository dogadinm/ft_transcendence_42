(function () {
    let movingDown = false;
    let movingUp = false;

    function initializeGame() {
      const gameDataElement = document.getElementById("gameData");
      if (!gameDataElement) return;

          const tournamentId = gameDataElement.dataset.roomLobby;
        
          const username = document.getElementById("TournamentData").dataset.username;
          const spectatorsList = document.getElementById("spectators-list");
          const readyPlayersList = document.getElementById("ready-players-list");
          const readyPlayersTournamentList = document.getElementById("ready-tournament-players-list");
          const winnersList = document.getElementById("winners-list");
          // const readyButton = document.getElementById("ready-button");
          const readyButton = document.getElementById("readyButton");

          document.addEventListener('keydown', handleKeyDown);
          document.addEventListener('keyup', handleKeyUp);
        
          const wsProtocol = location.protocol === "https:" ? "wss" : "ws";
          const wsUrl = `ws://127.0.0.1:8000/ws/tournament/${tournamentId}/`;
          
          const canvas = document.getElementById("gameCanvas");
          const ctx = canvas.getContext("2d");
          
          const statusElement = document.getElementById("status");
          
          // Connect to WebSocket
          function connectWebSocket() {
            if (window.tournamentLobbySocket){
              window.tournamentLobbySocket.close();
            }
            window.tournamentLobbySocket = new WebSocket(wsUrl);
                    
          
            window.tournamentLobbySocket.onopen = () => {
              statusElement.textContent = "Connected!";
            };
          
            window.tournamentLobbySocket.onmessage = (event) => {
              const data = JSON.parse(event.data);
              console.log(data.type);
          
              if (data.type === "game_update") {
                fieldWidth = data.game_state.field.width;
                fieldHeight = data.game_state.field.height;
                paddleWidth = data.game_state.paddle.width;
                paddleHeight = data.game_state.paddle.height;
                // gameState = data.game_state;
                drawGame(data);
              } else if (data.type === "tournament_end") {
                statusElement.textContent = `Tournament Winner: ${data.champion}`;
                readyButton.disabled = false;
              }else if (data.type === "tournament_state") {
                updateTournamentState(data);
              }
            };
          
            window.tournamentLobbySocket.onclose = () => {
              statusElement.textContent = "Disconnected. Refresh to reconnect.";
            };
          }
          
          function sendMessage(message) {
              window.tournamentLobbySocket.send(JSON.stringify(message));
          }

          function sendReadySignal() {
            sendMessage({ action: "ready" });
          }
      
          
          // Draw game state on canvas
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
            ctx.fillRect(20, data.game_state.paddles.left.paddleY, paddleWidth, paddleHeight); // Left paddle
            ctx.fillRect(fieldWidth - 20 - paddleWidth, data.game_state.paddles.right.paddleY, paddleWidth, paddleHeight); // Right paddle
    
            // Draw ball
            ctx.beginPath();
            ctx.arc(data.game_state.ball.x, data.game_state.ball.y, 10, 0, Math.PI * 2);
            ctx.fill();
    
            // Draw score
            ctx.font = '20px Arial';
            ctx.fillStyle = 'white';
            const leftPlayer = data.game_state.players.left || "Left";
            const rightPlayer = data.game_state.players.right || "Right";
            const text = `${leftPlayer}: ${data.game_state.score.left}  ${'    ' + rightPlayer}: ${data.game_state.score.right}`;
            const textWidth = ctx.measureText(text).width;
            const centerX = fieldWidth / 2;
            const maxHalfWidth = fieldWidth / 2;
            const startX = Math.max(centerX - textWidth / 2, centerX - maxHalfWidth);
            ctx.fillText(text, startX, 20);
        }
          
          function updateTournamentState(state) {
            readyPlayersTournamentList.innerHTML = state.all_ready
                .map(player => `<li>${player}</li>`)
                .join("");
            spectatorsList.innerHTML = state.spectators
                .map(spectator => `<li>${spectator}</li>`)
                .join("");
        
            winnersList.innerHTML = state.round_winners
                .map(winner => `<li>${winner}</li>`)
                .join("");

            if (state.all_ready.includes(username) || state.all_ready.length === 4) {
              readyButton.style.display = "none";
            } else {
              readyButton.style.display = "block";
            }
            if (state.champion) {
              alert(state.champion);
              // const h2Element = document.createElement('h2');
              // h2Element.textContent = `Champion: ${state.champion}`;
              
              // document.body.appendChild(h2Element);
            }

            readyPlayersList.innerHTML = `
            <li>
              Left: ${state.current_players.left || "Waiting"} - 
              ${state.ready.left ? "Ready" : "Not Ready"}
              ${
                state.current_players.left === username
                  ? '<button class="ready-button" data-side="left">Ready</button>'
                  : ""
              }
            </li>
            <li>
              Right: ${state.current_players.right || "Waiting"} - 
              ${state.ready.right ? "Ready" : "Not Ready"}
              ${
                state.current_players.right === username
                  ? '<button class="ready-button" data-side="right">Ready</button>'
                  : ""
              }
            </li>
          `;
        
          document.querySelectorAll(".ready-button").forEach(button => {
            button.addEventListener("click", () => {
              sendMessage({ action: "ready_game" });
              const statusElement = document.getElementById('statusElement');
              statusElement.textContent = `You are ready!`;
              button.disabled = true;
            });
          });
          
        }

          function handleKeyDown(e) {
      
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
      
              if (e.key === 'w' && movingUp) {
                  movingUp = false;
                  sendMessage({ action: 'stop', direction: 'up' });
              }
              if (e.key === 's' && movingDown) {
                  movingDown = false;
                  sendMessage({ action: 'stop', direction: 'down' });
              }
          }
          
          // Initialize WebSocket connection
          document.getElementById("readyButton").addEventListener("click", sendReadySignal);
          connectWebSocket();
          function disconnectWebSocket() {
            if (window.tournamentLobbySocket) {
                window.tournamentLobbySocket.close(1000, "User disconnected"); // close with code 1000 (normal)
                console.log("Closing Lobby WebSocket...");
            }
            navigate('/');
        }
        document.getElementById("leaveLobbyButton").addEventListener("click", disconnectWebSocket);    
    }
    

    function reinitializeOnNavigation() {
      initializeGame();
    }


    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", reinitializeOnNavigation);
    } else {
        reinitializeOnNavigation();
    }

})();
