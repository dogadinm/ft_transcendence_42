function startGame(role, roomName) {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${roomName}/${role}/`);

    let paddleY = 150;
    const isPlayer1 = role === 'player1';
    const isPlayer2 = role === 'player2';

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const { paddles, ball, score } = data;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';
        ctx.fillRect(10, paddles.left.paddleY, 10, 100);
        ctx.fillRect(780, paddles.right.paddleY, 10, 100);

        ctx.beginPath();
        ctx.arc(ball.x, ball.y, 10, 0, Math.PI * 2);
        ctx.fill();

        ctx.font = '20px Arial';
        ctx.fillText(`Player 1: ${score.player1}`, 20, 20);
        ctx.fillText(`Player 2: ${score.player2}`, 650, 20);
    };

    document.addEventListener('keydown', (e) => {
        if (isPlayer1 && (e.key === 'w' || e.key === 's')) {
            paddleY += (e.key === 'w' ? -10 : 10);
            socket.send(JSON.stringify({ side: 'left', paddleY }));
        } else if (isPlayer2 && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
            paddleY += (e.key === 'ArrowUp' ? -10 : 10);
            socket.send(JSON.stringify({ side: 'right', paddleY }));
        }
    });
}
