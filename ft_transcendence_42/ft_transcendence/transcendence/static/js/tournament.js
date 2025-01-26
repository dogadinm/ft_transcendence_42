(function () {
    let movingDown = false;
    let movingUp = false;


    document.addEventListener("DOMContentLoaded", () => {
        const gameDataElement = document.getElementById("gameData");
        const tournamentId = gameDataElement.dataset.roomLobby;
        // const wsUrl = `ws://127.0.0.1:8000/ws/tournament/${tournamentId}/`;
      
        const connectionStatus = document.getElementById("connection-status");
        const playersList = document.getElementById("players-list");
        const readyPlayersList = document.getElementById("ready-players-list");
        const teamsList = document.getElementById("teams-list");
        const winnersList = document.getElementById("winners-list");
        // const readyButton = document.getElementById("ready-button");

        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);
      
        const wsProtocol = location.protocol === "https:" ? "wss" : "ws";
        const roomName = "example_room"; // Replace with dynamic room name if needed
        const wsUrl = `ws://127.0.0.1:8000/ws/tournament/${tournamentId}/`;
        
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        
        const statusElement = document.getElementById("status");
        const readyButton = document.getElementById("readyBtn");
        
        let ws;
        let gameState = null;
        
        // Paddle movement states
        let paddleDirection = 0;
        
        // Connect to WebSocket
        function connectWebSocket() {
          ws = new WebSocket(wsUrl);
        
          ws.onopen = () => {
            statusElement.textContent = "Connected! Waiting for players...";
          };
        
          ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.type);
        
            if (data.type === "game_update") {
              gameState = data.game_state;
              drawGame();
            } else if (data.type === "tournament_end") {
              statusElement.textContent = `Tournament Winner: ${data.champion}`;
              readyButton.disabled = false;
            }else if (data.type === "tournament_state") {
              updateTournamentState(data);
            }
          };
        
          ws.onclose = () => {
            statusElement.textContent = "Disconnected. Refresh to reconnect.";
          };
        }
        
        function sendMessage(message) {
            ws.send(JSON.stringify(message));
        }

        function sendReadySignal() {
          sendMessage({ action: "ready_game" });
        }
    
        
        // Draw game state on canvas
        function drawGame() {
          if (!gameState) return;
        
          const { field, paddle, paddles, ball, players, score } = gameState;
        
          // Clear canvas
          ctx.clearRect(0, 0, field.width, field.height);
        
          // Draw field
          ctx.fillStyle = "#000";
          ctx.fillRect(0, 0, field.width, field.height);
        
          // Draw paddles
          ctx.fillStyle = "#FFF";
          ctx.fillRect(10, paddles.left.paddleY, paddle.width, paddle.height);
          ctx.fillRect(field.width - 20, paddles.right.paddleY, paddle.width, paddle.height);
        
          // Draw ball
          ctx.beginPath();
          ctx.arc(ball.x, ball.y, 8, 0, Math.PI * 2);
          ctx.fill();
        
          // Draw score
          ctx.font = "24px Arial";
          ctx.fillText(`Left (${players.left || "Waiting"}): ${score.left}`, 20, 30);
          ctx.fillText(`Right (${players.right || "Waiting"}): ${score.right}`, field.width - 250, 30);
        }
        
        // Handle ready button click
        readyButton.addEventListener("click", () => {
          ws.send(JSON.stringify({ action: "ready", side: "left" }));
          statusElement.textContent = "Ready! Waiting for the other player...";
          readyButton.disabled = true;
        });
        
        function updateTournamentState(state) {
          console.log(state);
      
          playersList.innerHTML = state.players_queue
              .map(player => `<li>${player}</li>`)
              .join("");
      
          spectatorsList.innerHTML = state.spectators
              .map(spectator => `<li>${spectator}</li>`)
              .join("");
      
          winnersList.innerHTML = state.round_winners
              .map(winner => `<li>${winner}</li>`)
              .join("");

          readyPlayersList.innerHTML = `
              <li>Left: ${state.current_players.left || "Waiting"} - ${state.ready.left ? "Ready" : "Not Ready"}</li>
              <li>Right: ${state.current_players.right || "Waiting"} - ${state.ready.right ? "Ready" : "Not Ready"}</li>
          `;
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
    });
    
})();