function navigateToTournament() {
    const tournamentInput = document.getElementById("tournament-input").value.trim();
    const tournamentButton = document.getElementById("tournament-button");

	if (tournamentInput.length < 3) {
		displayErrorMessage("Tournament name must be at least 3 characters long.");
		return;
	} else if (tournamentInput.length > 8) {
		displayErrorMessage("Tournament name cannot be more than 8 charaters.");
		return;
	} else if (!/^[a-zA-Z0-9]+$/.test(tournamentInput)) {
		displayErrorMessage("Tournament name can only contain letters and digits.");
		return;
	}

    const formData = new FormData();
    formData.append("tournament_name", tournamentInput);
    formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/find_tournament/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.exists) {
                const url = `/tournament/${data.tournament_name}`;
                tournamentButton.setAttribute("data-navigate", url);
                tournamentButton.click();
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