// Global Variables
var DIRECTION = {
    IDLE: 0,
    UP: 1,
    DOWN: 2,
    LEFT: 3,
    RIGHT: 4
};

var rounds = [5, 5, 3, 3, 2];
var colors = ['#1abc9c', '#2ecc71', '#3498db', '#8c52ff', '#9b59b6'];

// The ball object (the square that bounces back and forth)
var Ball = {
    new: function(incrementedSpeed) {
        return {
            width: 18,
            height: 18,
            x: (Game.canvas.width / 2) - 9,
            y: (Game.canvas.height / 2) - 9,
            moveX: DIRECTION.IDLE,
            moveY: DIRECTION.IDLE,
            speed: incrementedSpeed || 7
        };
    }
};

// The paddle object (paddles that move up and down)
var Paddle = {
    new: function(side) {
        return {
            width: 18,
            height: 180,
            x: side === 'left' ? 15 : Game.canvas.width - 33, // Position the paddles at the edges
            y: (Game.canvas.height / 2) - (180 / 2),
            score: 0,
            move: DIRECTION.IDLE,
            speed: 8
        };
    }
};

// The Game object with main game logic
var Game = {
    initialize: function() {
        this.canvas = document.querySelector('canvas');
        this.context = this.canvas.getContext('2d');

        this.canvas.width = 1400;
        this.canvas.height = 1000;

        this.canvas.style.width = (this.canvas.width / 2) + 'px';
        this.canvas.style.height = (this.canvas.height / 2) + 'px';

        this.player = Paddle.new('left');
        this.paddle = Paddle.new('right');
        this.ball = Ball.new();

        this.paddle.speed = 5;
        this.running = this.over = false;
        this.turn = this.paddle;
        this.timer = this.round = 0;
        this.color = colors[0];

        this.menu();
        this.listen();
    },

    // Display the start menu
    menu: function() {
        this.draw();

        this.context.font = '50px Arial';
        this.context.fillStyle = this.color;
        this.context.textAlign = 'center';

        this.context.fillRect(
            this.canvas.width / 2 - 350,
            this.canvas.height / 2 - 48,
            700,
            100
        );

        this.context.fillStyle = '#ffffff';
        this.context.fillText('Press any key to begin',
            this.canvas.width / 2,
            this.canvas.height / 2 + 15
        );
    },

// End game and display message, launch restart button
endGameMenu: function() {
    // Ensure the game loop stops
    this.over = true;

    // Clear the canvas
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw the background
    this.context.fillStyle = this.color;
    this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Display the winner message
    this.context.font = '50px Arial';
    this.context.fillStyle = '#ffffff';
    this.context.textAlign = 'center';
    this.context.fillText(this.winnerText, this.canvas.width / 2, this.canvas.height / 2 - 60);

    // Create and center the restart button below the winner text
    const restartButton = document.createElement('button');
    restartButton.textContent = 'Restart Game';
    restartButton.style.position = 'absolute';

    // Calculate the button's top position based on the canvas height and winner message
    const winnerTextHeight = 50; // Height of the winner text
    const winnerTextYPosition = this.canvas.height / 2 - 60;
    const buttonOffset = 5; // Space between the winner text and the button
    const buttonTop = winnerTextYPosition + winnerTextHeight + buttonOffset;

    restartButton.style.top = buttonTop + 'px';  // Positioning below the winner text
    restartButton.style.left = '50%';
    restartButton.style.transform = 'translateX(-50%)';
    restartButton.style.padding = '10px 20px';
    restartButton.style.fontSize = '16px';
    restartButton.style.cursor = 'pointer';
    restartButton.style.zIndex = '1000';

    // Append the button to the body
    document.body.appendChild(restartButton);

    // Restart the game when the button is clicked
    restartButton.addEventListener('click', () => {
        document.body.removeChild(restartButton); // Remove the button
        this.initialize(); // Restart the game
    });
},

    // Main game loop
    loop: function() {
        Game.update();
        Game.draw();

        if (!Game.over) requestAnimationFrame(Game.loop);
    },

    // Listen for keyboard input
    listen: function() {
        document.addEventListener('keydown', (event) => {
            if (Game.running === false) {
                Game.running = true;
                window.requestAnimationFrame(Game.loop);
            }

            if (event.keyCode === 38 || event.keyCode === 87) Game.player.move = DIRECTION.UP;
            if (event.keyCode === 40 || event.keyCode === 83) Game.player.move = DIRECTION.DOWN;
        });

        document.addEventListener('keyup', () => {
            Game.player.move = DIRECTION.IDLE;
        });
    },

    // Update positions and states
    update: function() {
        if (!this.over) {
            if (this.ball.x <= 0) this._resetTurn(this.paddle, this.player);
            if (this.ball.x >= this.canvas.width - this.ball.width) this._resetTurn(this.player, this.paddle);
            if (this.ball.y <= 0) this.ball.moveY = DIRECTION.DOWN;
            if (this.ball.y >= this.canvas.height - this.ball.height) this.ball.moveY = DIRECTION.UP;

            if (this.player.move === DIRECTION.UP) this.player.y -= this.player.speed;
            if (this.player.move === DIRECTION.DOWN) this.player.y += this.player.speed;

            if (this._turnDelayIsOver() && this.turn) {
                this.ball.moveX = this.turn === this.player ? DIRECTION.LEFT : DIRECTION.RIGHT;
                this.ball.moveY = [DIRECTION.UP, DIRECTION.DOWN][Math.floor(Math.random() * 2)];
                this.ball.y = Math.floor(Math.random() * this.canvas.height - 200) + 200;
                this.turn = null;
            }

            if (this.player.y <= 0) this.player.y = 0;
            if (this.player.y >= this.canvas.height - this.player.height) this.player.y = this.canvas.height - this.player.height;

            if (this.ball.moveY === DIRECTION.UP) this.ball.y -= (this.ball.speed / 1.5);
            if (this.ball.moveY === DIRECTION.DOWN) this.ball.y += (this.ball.speed / 1.5);
            if (this.ball.moveX === DIRECTION.LEFT) this.ball.x -= this.ball.speed;
            if (this.ball.moveX === DIRECTION.RIGHT) this.ball.x += this.ball.speed;

            if (this.paddle.y > this.ball.y - (this.paddle.height / 2)) {
                this.paddle.y -= this.paddle.speed / 1.5;
            } else if (this.paddle.y < this.ball.y - (this.paddle.height / 2)) {
                this.paddle.y += this.paddle.speed / 1.5;
            }

            if (this.paddle.y >= this.canvas.height - this.paddle.height) this.paddle.y = this.canvas.height - this.paddle.height;
            if (this.paddle.y <= 0) this.paddle.y = 0;

            if (this.ball.x - this.ball.width <= this.player.x && this.ball.x >= this.player.x - this.player.width) {
                if (this.ball.y <= this.player.y + this.player.height && this.ball.y + this.ball.height >= this.player.y) {
                    this.ball.moveX = DIRECTION.RIGHT;
                }
            }

            if (this.ball.x - this.ball.width <= this.paddle.x && this.ball.x >= this.paddle.x - this.paddle.width) {
                if (this.ball.y <= this.paddle.y + this.paddle.height && this.ball.y + this.ball.height >= this.paddle.y) {
                    this.ball.moveX = DIRECTION.LEFT;
                }
            }
        }
    },

    // Reset the ball position and update the score. Check for the winning condition.
    _resetTurn: function(victor, loser) {
        this.ball = Ball.new(this.ball.speed);
        this.turn = loser;
        this.timer = (new Date()).getTime();

        victor.score++;

        // Check if the game has a winner
        if (victor.score >= 1) {
            this.over = true; // Stop the game loop
            this.winnerText = victor === this.player ? 'You won!' : 'Bot won!'; // Set the winner message
            this.endGameMenu(); // Call endGameMenu to display both the message and the button
        }
    },

    // Delay before the next turn
    _turnDelayIsOver: function() {
        return ((new Date()).getTime() - this.timer >= 1000);
    },

    // Render the game objects
    draw: function() {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.context.fillStyle = this.color;
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.context.fillStyle = '#ffffff';
        this.context.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        this.context.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);

        if (this._turnDelayIsOver()) {
            this.context.fillRect(this.ball.x, this.ball.y, this.ball.width, this.ball.height);
        }

        for (let i = 0; i < this.canvas.height; i += 25) {
            this.context.fillRect((this.canvas.width / 2) - 1, i, 2, 20);
        }

        this.context.font = '40px Arial';  // Increase font size here
        this.context.textAlign = 'center';
        this.context.fillText(this.player.score.toString(), this.canvas.width / 2 - 50, 50);
        this.context.fillText(this.paddle.score.toString(), this.canvas.width / 2 + 50, 50);

        // Draw "You" and "Bot" labels with a larger font size
        this.context.font = '40px Arial';
        this.context.textAlign = 'left';
        this.context.fillText('You', 20, 40);
        this.context.textAlign = 'right';
        this.context.fillText('Bot', this.canvas.width - 20, 40);

        // Display winner message if the game is over
        if (this.over) {
            this.context.font = '50px Arial';
            this.context.textAlign = 'center';
            this.context.fillStyle = '#ffffff';
            this.context.fillText(this.winnerText, this.canvas.width / 2, this.canvas.height / 2);
        }
    }

};

Game.initialize();