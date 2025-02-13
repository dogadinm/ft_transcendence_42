function navigateToProfile() {
    const usernameInput = document.getElementById('username-input').value.trim();
    const usernameButton = document.getElementById("username-button");

	if (usernameInput.length < 3) {
		displayErrorMessage("Tournament name must be at least 3 characters long.");
		return;
	} else if (usernameInput.length > 25) {
		displayErrorMessage("Tournament name cannot be more than 25 characters.");
		return;
	}

    const formData = new FormData();
    formData.append("username", usernameInput);
    formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/find_friend/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.exists) {
                const url = `/profile/${data.username}`;
                usernameButton.setAttribute("data-navigate", url);
                usernameButton.click();
            } else {
                displayErrorMessage(data.message || "User not found.");
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while checking the User.");
        });
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "red";
}