document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
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

    const formData = new FormData(this);
    try {
        const response = await fetch("/login/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        });

        const data = await response.json();

        if (response.ok) {
            if (data.redirect) {
                console.log(data.redirect)
                navigate(data.redirect);
            }
        } else {
            const error = data.error || "An error occurred.";
            errorMessage.textContent = error;
        }
    } catch (error) {
        console.error("Error:", error);
        errorMessage.textContent = "Failed to send the login request.";
    }
});