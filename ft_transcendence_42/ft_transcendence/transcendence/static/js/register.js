document.getElementById("register-form").addEventListener("submit", async function (event) {
    event.preventDefault();  // Prevent the default form submission

    const formData = new FormData(this);  // Collect form data
    try {
        // Make the AJAX request to submit the form data
        const response = await fetch("/register/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,  // CSRF token for protection
            },
        });

        const data = await response.json();  // Parse the JSON response

        // Clear any previous error messages
        const errorMessages = {
            username: document.getElementById("username-error"),
            email: document.getElementById("email-error"),
            password: document.getElementById("password-error"),
            confirmation: document.getElementById("confirmation-error"),
        };

        // Reset error messages
        Object.values(errorMessages).forEach((element) => element.textContent = "");

        if (response.ok) {
            // If the response is successful, redirect to the specified URL
            if (data.redirect) {
                navigate(data.redirect);
            }
        } else {
            // If there are errors, handle each one
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

            // If no specific error is found
            if (!data.error.username && !data.error.email && !data.error.password && !data.error.confirmation) {
                document.getElementById("error-message").textContent = "An unknown error occurred.";
            }
        }
    } catch (error) {
        console.error("Error:", error);  // Log any errors for debugging
    }
});