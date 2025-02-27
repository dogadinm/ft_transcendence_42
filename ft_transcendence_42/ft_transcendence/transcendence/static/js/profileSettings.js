function initializeSaveButton() {
    const tournamentInput = document.getElementById('tournament-nickname').value.trim();
    const photoInput = document.getElementById('photo').files[0];
    const descriptiontInput = document.getElementById('description').value.trim();

    const settingsButton = document.getElementById("save-button");

	if (tournamentInput.length < 3) {
		displayErrorMessage("Tournament nickname must be at least 3 characters long.");
		return;
	} else if (tournamentInput.length > 25) {
		displayErrorMessage("Tournament nickname cannot be more than 25 characters.");
		return;
	} else if (!/^[a-zA-Z0-9]+$/.test(tournamentInput)) {
        displayErrorMessage("Tournament name can only contain letters and digits.");
        return;
    }
    if (tournamentInput.length > 500) {
		displayErrorMessage("Description cannot be more than 500 characters.");
		return;
	}
    if (tournamentInput.length > 500) {
		displayErrorMessage("Description cannot be more than 500 characters.");
		return;
	}
    if (photoInput) {
        const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
        
        if (!allowedTypes.includes(photoInput.type)) {
            displayErrorMessage("Profile photo must be jpg, png or jpeg.");
            return;
        }
    }

    const formData = new FormData();
    formData.append("tournament_nickname", tournamentInput);
    formData.append("photo", photoInput);
    formData.append("description", descriptiontInput);
    formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/profile_settings/", {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => response.json())  // <- Здесь может быть проблема, если ответ не JSON
    .then(data => {
        console.log("Ответ сервера:", data);
        if (data.exists) {
            alert("Settings updated successfully.");
        } else {
            displayErrorMessage(data.message || "User not found.");
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
        displayErrorMessage("An error occurred while checking the User.");
    });
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "red";
}
