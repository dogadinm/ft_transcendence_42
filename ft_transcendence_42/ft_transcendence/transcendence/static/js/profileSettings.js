function initializeSaveButton() {
    console.log("Initializing save button...");

    const saveButton = document.getElementById("save-button");

    if (!saveButton) {
        console.error("Save button not found!");
        return;
    }

    saveButton.addEventListener("click", async (event) => {
        event.preventDefault();
        console.log("Save button clicked.");

        const form = document.getElementById("profile-settings-form");
        if (!form) {
            console.error("Form not found!");
            return;
        }

        const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
        if (!csrfTokenElement) {
            console.error("CSRF token not found.");
            return;
        }

        const csrfToken = csrfTokenElement.value;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Server response:", data);

                const feedback = document.getElementById("settings-feedback");
                if (feedback) {
                    feedback.style.display = "block";
                    feedback.textContent = data.message || "Settings updated successfully.";
                    feedback.className = "alert alert-success";
                }
            } else {
                const errorText = await response.text();
                console.error("Server error:", errorText);
                const parsedError = JSON.parse(errorText)
                const feedback = document.getElementById("settings-feedback");
                if (feedback) {
                    feedback.style.display = "block";
                    if (parsedError.errors.nickname) {
                      feedback.textContent = parsedError.errors.nickname[0];
                    } else if (parsedError.errors.photo) {
                      feedback.textContent = parsedError.errors.photo[0];
                    } else if (parsedError.errors.description) {
                      feedback.textContent = parsedError.errors.description[0];
                    } else {
                      feedback.textContent = "An unknown error occurred.";
                    }
                    feedback.className = "alert alert-danger";
                }
            }
        } catch (error) {
            console.error("Request failed:", error);

            const feedback = document.getElementById("settings-feedback");
            if (feedback) {
                feedback.style.display = "block";
                feedback.textContent = "An unexpected error occurred.";
                feedback.className = "alert alert-danger";
            }
        }
    });
}

initializeSaveButton();