(function () {
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
                x: (Game.botCanvas.width / 2) - 9,
                y: (Game.botCanvas.height / 2) - 9,
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
                x: side === 'left' ? 15 : Game.botCanvas.width - 33, // Position the paddles at the edges
                y: (Game.botCanvas.height / 2) - (180 / 2),
                score: 0,
                move: DIRECTION.IDLE,
                speed: 8
            };
        }
    };

    // The Game object with main game logic
    var Game = {
        initialize: function() {
            this.botCanvas = document.getElementById('botCanvas');
            this.context = this.botCanvas.getContext('2d');

            this.botCanvas.width = 1400;
            this.botCanvas.height = 1000;

            this.botCanvas.style.width = (this.botCanvas.width / 2) + 'px';
            this.botCanvas.style.height = (this.botCanvas.height / 2) + 'px';

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
                this.botCanvas.width / 2 - 350,
                this.botCanvas.height / 2 - 48,
                700,
                100
            );

            this.context.fillStyle = '#ffffff';
            this.context.fillText('Press any key to begin',
                this.botCanvas.width / 2,
                this.botCanvas.height / 2 + 15
            );
        },

    // End game and display message, launch restart button
    endGameMenu: function() {
        this.over = true;
        this.context.clearRect(0, 0, this.botCanvas.width, this.botCanvas.height);
        this.context.fillStyle = this.color;
        this.context.fillRect(0, 0, this.botCanvas.width, this.botCanvas.height);

        this.context.font = '50px Arial';
        this.context.fillStyle = '#ffffff';
        this.context.textAlign = 'center';
        this.context.fillText(this.winnerText, this.botCanvas.width / 2, this.botCanvas.height / 2 - 60);
        this.context.fillText("Restarting in 10 seconds...", this.botCanvas.width / 2, this.botCanvas.height / 2);

        setTimeout(() => {
            this.initialize();
        }, 10000);
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
                if (this.ball.x >= this.botCanvas.width - this.ball.width) this._resetTurn(this.player, this.paddle);
                if (this.ball.y <= 0) this.ball.moveY = DIRECTION.DOWN;
                if (this.ball.y >= this.botCanvas.height - this.ball.height) this.ball.moveY = DIRECTION.UP;

                if (this.player.move === DIRECTION.UP) this.player.y -= this.player.speed;
                if (this.player.move === DIRECTION.DOWN) this.player.y += this.player.speed;

                if (this._turnDelayIsOver() && this.turn) {
                    this.ball.moveX = this.turn === this.player ? DIRECTION.LEFT : DIRECTION.RIGHT;
                    this.ball.moveY = [DIRECTION.UP, DIRECTION.DOWN][Math.floor(Math.random() * 2)];
                    this.ball.y = Math.floor(Math.random() * this.botCanvas.height - 200) + 200;
                    this.turn = null;
                }

                if (this.player.y <= 0) this.player.y = 0;
                if (this.player.y >= this.botCanvas.height - this.player.height) this.player.y = this.botCanvas.height - this.player.height;

                if (this.ball.moveY === DIRECTION.UP) this.ball.y -= (this.ball.speed / 1.5);
                if (this.ball.moveY === DIRECTION.DOWN) this.ball.y += (this.ball.speed / 1.5);
                if (this.ball.moveX === DIRECTION.LEFT) this.ball.x -= this.ball.speed;
                if (this.ball.moveX === DIRECTION.RIGHT) this.ball.x += this.ball.speed;

                if (this.paddle.y > this.ball.y - (this.paddle.height / 2)) {
                    this.paddle.y -= this.paddle.speed / 1.5;
                } else if (this.paddle.y < this.ball.y - (this.paddle.height / 2)) {
                    this.paddle.y += this.paddle.speed / 1.5;
                }

                if (this.paddle.y >= this.botCanvas.height - this.paddle.height) this.paddle.y = this.botCanvas.height - this.paddle.height;
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
            this.context.clearRect(0, 0, this.botCanvas.width, this.botCanvas.height);

            this.context.fillStyle = this.color;
            this.context.fillRect(0, 0, this.botCanvas.width, this.botCanvas.height);

            this.context.fillStyle = '#ffffff';
            this.context.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
            this.context.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);

            if (this._turnDelayIsOver()) {
                this.context.fillRect(this.ball.x, this.ball.y, this.ball.width, this.ball.height);
            }

            for (let i = 0; i < this.botCanvas.height; i += 25) {
                this.context.fillRect((this.botCanvas.width / 2) - 1, i, 2, 20);
            }

            this.context.font = '40px Arial';  // Increase font size here
            this.context.textAlign = 'center';
            this.context.fillText(this.player.score.toString(), this.botCanvas.width / 2 - 50, 50);
            this.context.fillText(this.paddle.score.toString(), this.botCanvas.width / 2 + 50, 50);

            // Draw "You" and "Bot" labels with a larger font size
            this.context.font = '40px Arial';
            this.context.textAlign = 'left';
            this.context.fillText('You', 20, 40);
            this.context.textAlign = 'right';
            this.context.fillText('Bot', this.botCanvas.width - 20, 40);

            // Display winner message if the game is over
            if (this.over) {
                this.context.font = '50px Arial';
                this.context.textAlign = 'center';
                this.context.fillStyle = '#ffffff';
                this.context.fillText(this.winnerText, this.botCanvas.width / 2, this.botCanvas.height / 2);
            }
        }

    };

    Game.initialize();
})();