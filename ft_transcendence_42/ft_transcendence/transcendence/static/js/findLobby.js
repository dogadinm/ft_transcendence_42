function navigateToLobby() {
    const lobbyInput = document.getElementById("lobby-input").value.trim();
    const lobbyButton = document.getElementById("lobby-button");

    if (lobbyInput.length < 3) {
        displayErrorMessage("Lobby must be at least 3 characters long.");
        return;
    } else if (lobbyInput.length > 25) {
        displayErrorMessage("Lobby cannot be more than 25 characters.");
        return;
    } else if (!/^[a-zA-Z0-9]+$/.test(lobbyInput)) {
        displayErrorMessage("Lobby can only contain letters and digits.");
        return;
    }

    const formData = new FormData();
    formData.append("lobby_name", lobbyInput);
    formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/find_lobby/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.exists) {
                const url = `/pong_lobby/${data.lobby_name}`;
                lobbyButton.setAttribute("data-navigate", url);
                lobbyButton.click();
            } else {
                displayErrorMessage(data.message || "Lobby not found.");
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while checking the lobby.");
        });
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "red";
}