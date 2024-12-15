
const socket = new WebSocket(`ws://${window.location.host}/ws/game/{{ room_name }}/`);

let paddleY = 150;
const paddleHeight = 100;
const fieldHeight = 400;
const paddleSpeed = 3;

let movingUp = false;
let movingDown = false;

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === 'role_assignment') {
        document.getElementById('roleInfo').innerText = `You are ${data.role}`;
        if (data.role === 'player1' || data.role === 'player2') {
            document.addEventListener('keydown', handleKeyDown);
            document.addEventListener('keyup', handleKeyUp);
            requestAnimationFrame(gameLoop);
        }
    } else if (data.type === 'game_update') {
        drawGame(data);
    }
};

function handleKeyDown(e) {
    if (e.key === 'w') movingUp = true;
    if (e.key === 's') movingDown = true;
}

function handleKeyUp(e) {
    if (e.key === 'w') movingUp = false;
    if (e.key === 's') movingDown = false;
}

function gameLoop() {
    if (movingUp) paddleY -= paddleSpeed;
    if (movingDown) paddleY += paddleSpeed;

    paddleY = Math.max(0, Math.min(fieldHeight - paddleHeight, paddleY));

    socket.send(JSON.stringify({ paddleY }));

    requestAnimationFrame(gameLoop);
}

function drawGame(data) {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillRect(10, data.paddles.left.paddleY, 10, 100);
    ctx.fillRect(780, data.paddles.right.paddleY, 10, 100);

    ctx.beginPath();
    ctx.arc(data.ball.x, data.ball.y, 10, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = '20px Arial';
    ctx.fillText(`Player 1: ${data.score.player1}`, 20, 20);
    ctx.fillText(`Player 2: ${data.score.player2}`, 650, 20);
}
