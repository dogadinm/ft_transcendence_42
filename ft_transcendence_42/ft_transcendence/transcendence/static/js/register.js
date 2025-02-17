function register() {
    const registerButton = document.getElementById("register-button");

    const form = document.getElementById("register-form");
    const formData = new FormData(form);

    fetch("/register/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,  // CSRF token for protection
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.redirect) {
                const url = `${data.redirect}`;
                registerButton.setAttribute("data-navigate", url);
                registerButton.click();
                updateUserLinks();

            } else if (data.wallet_error) {
                displayErrorMessage(data.wallet_error);   
            } else {   
                const errorMessages = {
                    username: document.getElementById("username-error"),
                    email: document.getElementById("email-error"),
                    password: document.getElementById("password-error"),
                    confirmation: document.getElementById("confirmation-error"),
                };
                // Reset error messages
                Object.values(errorMessages).forEach((element) => element.textContent = "");
                if (data.error.username) {
                    errorMessages.username.textContent = data.error.username[0];
                }
                if (data.error.email) {
                    errorMessages.email.textContent = data.error.email[0];
                }
                if (data.error.password) {
                    errorMessages.password.textContent = data.error.password[0];
                }
                if (data.error.confirmation) {
                    errorMessages.confirmation.textContent = data.error.confirmation[0];
                }
                if (data.error.confirmation) {
                    errorMessages.confirmation.textContent = data.error.confirmation[0];
                }
    
    
                // If no specific error is found
                if (!data.error.username && !data.error.email && !data.error.password && !data.error.confirmation) {
                    document.getElementById("error-message").textContent = "An unknown error occurred.";
                }
            
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while registering");
        });
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "red";
}