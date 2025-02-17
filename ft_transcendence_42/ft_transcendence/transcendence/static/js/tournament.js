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
          const readyButton = document.getElementById("readyButton");
          const statusElement = document.getElementById("status");
          const canvas = document.getElementById("tournamentCanvas");
          const ctx = canvas.getContext("2d");
  
          const wsProtocol = location.protocol === "https:" ? "wss" : "ws";
          const wsUrl = `${wsProtocol}://127.0.0.1:8000/ws/tournament/${tournamentId}/`;
          

      
          // Event listeners for key controls
          document.addEventListener('keydown', handleKeyDown);
          document.addEventListener('keyup', handleKeyUp);
  
          
        // WebSocket connection
        function connectWebSocket() {
            if (window.tournamentLobbySocket) {
                window.tournamentLobbySocket.close();
            }

            window.tournamentLobbySocket = new WebSocket(wsUrl);

            window.tournamentLobbySocket.onopen = () => {
                statusElement.textContent = "Connected!";
            };

            window.tournamentLobbySocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log(data.type);

                switch (data.type) {
                    case "game_update":
                        drawGame(data.game_state);
                        break;
                    case "tournament_end":
                        statusElement.textContent = `Tournament Winner: ${data.champion}`;
                        break;
                    case "tournament_state":
                        updateTournamentState(data);
                        break;
                    case "notification":
                          alert(data.massage);
                          break;
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
        function drawGame(gameState) {
          const { field, paddles, ball, players, score } = gameState;

          canvas.width = field.width;
          canvas.height = field.height;

          ctx.clearRect(0, 0, field.width, field.height);

          // Draw background
          ctx.fillStyle = '#1abc9c';
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          // Draw middle line
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
          ctx.fillRect(20, paddles.left.paddleY, 10, 100); // Left paddle
          ctx.fillRect(field.width - 30, paddles.right.paddleY, 10, 100); // Right paddle

          // Draw ball
          ctx.beginPath();
          ctx.arc(ball.x, ball.y, 10, 0, Math.PI * 2);
          ctx.fill();

          // Draw score
          ctx.font = '20px Arial';
          ctx.fillStyle = 'white';

          const leftPlayer = players.left || "Left";
          const rightPlayer = players.right || "Right";

          // Left player score
          const leftText = `${leftPlayer}: ${score.left}`;
          const leftTextWidth = ctx.measureText(leftText).width;
          const leftTextX = (field.width / 2) - leftTextWidth - 20;
          ctx.fillText(leftText, leftTextX, 20);

          // Right player score
          const rightText = `${rightPlayer}: ${score.right}`;
          const rightTextX = (field.width / 2) + 20;
          ctx.fillText(rightText, rightTextX, 20);
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
              alert(`Champion: ${state.champion}`);
            }

            readyPlayersList.innerHTML = `
              <h4>
                Left: ${state.current_players.left || "Waiting"} - 
                ${state.ready.left ? "Ready" : "Not Ready"}
                ${
                  state.current_players.left === username
                    ? '<button class="ready-button" data-side="left">Ready</button>'
                    : ""
                }
              </h4>
              <h4>
                Right: ${state.current_players.right || "Waiting"} - 
                ${state.ready.right ? "Ready" : "Not Ready"}
                ${
                  state.current_players.right === username
                    ? '<button class="ready-button" data-side="right">Ready</button>'
                    : ""
                }
              </h4>
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
      
        // Handle keyup events
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
          

      // Disconnect WebSocket
      function disconnectWebSocket() {
        if (window.tournamentLobbySocket) {
            window.tournamentLobbySocket.close(1000, "User disconnected");
            console.log("Closing Lobby WebSocket...");
        }
        navigate('/');
      }

      // Event listeners
      readyButton.addEventListener("click", sendReadySignal);
      document.getElementById("leaveLobbyButton").addEventListener("click", disconnectWebSocket);

      // Initialize WebSocket
      connectWebSocket();
    }

    // Reinitialize on navigation
    function reinitializeOnNavigation() {
        initializeGame();
    }

    // Initialize on DOM load
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", reinitializeOnNavigation);
    } else {
        reinitializeOnNavigation();
    }

})();
