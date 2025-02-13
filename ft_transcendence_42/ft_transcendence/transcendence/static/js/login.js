async function login() {
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();
        const loginButton = document.getElementById("login-button");
        const errorMessage = document.getElementById("error-message");

        // Clear previous errors
        errorMessage.textContent = "";

        // Basic client-side validation
        if (username.length < 3) {
            errorMessage.textContent = "Username must be at least 3 characters long.";
            return;
        }
        if (password.length < 6) {
            errorMessage.textContent = "Password must be at least 6 characters long.";
            return;
        }

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        formData.append(
            "csrfmiddlewaretoken",
            document.querySelector("[name=csrfmiddlewaretoken]").value
        );
        try {
            const response = await fetch("/login/", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                if (data.redirect) {
                    loginButton.setAttribute("data-navigate", data.redirect);
                    loginButton.click();
                    updateUserLinks();
                    // updateCSRFToken();
                }
            } else {
                errorMessage.textContent = data.error;
            }
        } catch (error) {
            console.error("Error:", error);
            errorMessage.textContent = "Failed to send the login request.";
        }
}
