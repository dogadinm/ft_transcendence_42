// Variables
let dealerSum = 0;
let yourSum = 0;

let dealerAceCount = 0;
let yourAceCount = 0;

let hidden;
let deck;

let canHit = true;

let playerWins = 0;
let dealerWins = 0;
let ties = 0; // To keep track of ties

// Initialize the game
window.onload = function () {
    document.getElementById("hit").addEventListener("click", hit);
    document.getElementById("stay").addEventListener("click", stay);
    document.getElementById("start-again").addEventListener("click", startAgain);
    document.getElementById("quit").addEventListener("click", quitGame);

    startGame();
};

// Build the deck
function buildDeck() {
    const values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
    const suits = ["C", "D", "H", "S"];
    deck = [];

    for (let suit of suits) {
        for (let value of values) {
            deck.push(`${value}-${suit}`);
        }
    }
}

// Shuffle the deck
function shuffleDeck() {
    for (let i = 0; i < deck.length; i++) {
        const j = Math.floor(Math.random() * deck.length);
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
}

// Start the game
function startGame() {
    dealerSum = yourSum = 0;
    dealerAceCount = yourAceCount = 0;
    canHit = true;

    buildDeck();
    shuffleDeck();

    hidden = deck.pop();
    dealerSum += getValue(hidden);
    dealerAceCount += checkAce(hidden);

    // Dealer's first card is hidden (back side)
    document.getElementById("dealer-cards").innerHTML = `<img id="hidden" src="./cards/BACK.png">`;

    // Dealer draws cards until sum >= 17
    while (dealerSum < 17) {
        const card = deck.pop();
        dealerSum += getValue(card);
        dealerAceCount += checkAce(card);
        const cardImg = createCardImage(card);
        document.getElementById("dealer-cards").append(cardImg);
    }

    // Player starts with 2 cards
    document.getElementById("your-cards").innerHTML = "";
    for (let i = 0; i < 2; i++) {
        const card = deck.pop();
        yourSum += getValue(card);
        yourAceCount += checkAce(card);
        const cardImg = createCardImage(card);
        document.getElementById("your-cards").append(cardImg);
    }

    document.getElementById("results").innerText = "";
    document.getElementById("results").className = "";
    document.getElementById("hit").disabled = false;
    document.getElementById("stay").disabled = false;

    updateScoreboard();
}

// Handle Hit button
function hit() {
    if (!canHit) return;

    const card = deck.pop();
    yourSum += getValue(card);
    yourAceCount += checkAce(card);
    const cardImg = createCardImage(card);
    document.getElementById("your-cards").append(cardImg);

    // Automatically handle the case where the player goes over 21 or hits 21
    if (reduceAce(yourSum, yourAceCount) > 21) {
        canHit = false;
        dealerWins++;
        updateScoreboard();
        displayResults("You Lose!");
        setTimeout(startGame, 1000); // Restart the game after 1 second
    } else if (yourSum === 21) {
        canHit = false;
        playerWins++;
        updateScoreboard();
        displayResults("You Win!");
        setTimeout(startGame, 1000); // Restart the game after 1 second
    }
}

// Handle Stay button
function stay() {
    dealerSum = reduceAce(dealerSum, dealerAceCount);
    yourSum = reduceAce(yourSum, yourAceCount);
    canHit = false;

    // Reveal the hidden card
    document.getElementById("hidden").src = `./cards/${hidden}.png`;

    let message = "";
    if (yourSum > 21) {
        message = "You Lose!";
        dealerWins++;
    } else if (dealerSum > 21 || yourSum > dealerSum) {
        message = "You Win!";
        playerWins++;
    } else if (yourSum < dealerSum) {
        message = "You Lose!";
        dealerWins++;
    } else {
        message = "It's a Tie!";
        ties++; // Increase tie count without ending the game
    }

    displayResults(message);
    updateScoreboard();

    // If it's a tie, reset the deck and re-deal the cards
    if (message === "It's a Tie!") {
        setTimeout(() => {
            startGame();
        }, 1000); // Restart after a short delay to show the result
    } else {
        setTimeout(startGame, 1000); // Restart after 1 second
    }
}

// Handle Start Again button
function startAgain() {
    playerWins = 0;
    dealerWins = 0;
    ties = 0; // Reset ties
    updateScoreboard();
    startGame();
}

// Handle Quit button
function quitGame() {
    document.getElementById("results").innerText = "Game Over! You Quit!";
    document.getElementById("results").className = "quit";
    document.getElementById("hit").disabled = true;
    document.getElementById("stay").disabled = true;
}

// Helper Functions
function createCardImage(card) {
    const img = document.createElement("img");
    img.src = `./cards/${card}.png`;
    return img;
}

function getValue(card) {
    const value = card.split("-")[0];
    return value === "A" ? 11 : isNaN(value) ? 10 : parseInt(value);
}

function checkAce(card) {
    return card.startsWith("A") ? 1 : 0;
}

function reduceAce(sum, aceCount) {
    while (sum > 21 && aceCount > 0) {
        sum -= 10;
        aceCount--;
    }
    return sum;
}

function displayResults(message) {
    const resultsEl = document.getElementById("results");
    resultsEl.innerText = message;
    resultsEl.className = "";
    resultsEl.classList.add(
        message.includes("Win") ? "win" : message.includes("Lose") ? "lose" : "tie"
    );
}

function updateScoreboard() {
    document.getElementById("player-score").innerText = `Player Wins: ${playerWins}`;
    document.getElementById("dealer-score").innerText = `Dealer Wins: ${dealerWins}`;
    document.getElementById("ties").innerText = `Ties: ${ties}`; // Show ties on the scoreboard
}
