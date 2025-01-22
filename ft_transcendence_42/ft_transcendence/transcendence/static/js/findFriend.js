function navigateToProfile() {
    const usernameInput = document.getElementById('username-input').value.trim();

    if (usernameInput) {
        if (usernameInput.length < 3) {
            displayErrorMessage("Username must be at least 3 characters long.");
            return;
        } else if (usernameInput.length > 25) {
            displayErrorMessage("Username cannot be more than 25 characters.");
            return;
        } else if (!/^[a-zA-Z0-9]+$/.test(usernameInput)) {
            displayErrorMessage("Username can only contain letters and digits.");
            return;
        }

        const formData = new FormData();
        formData.append('username', usernameInput);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        fetch("/find_friend/", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                const url = `/profile/${data.username}`;
                navigate(url);
            } else {
                displayErrorMessage(data.message || "User not found.");
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while checking the username.");
        });
    } else {
        displayErrorMessage("Please enter a username.");
    }
}

function displayErrorMessage(message) {
    const errorElement = document.getElementById("error-message");
    errorElement.textContent = message;
    errorElement.style.color = "red";
}