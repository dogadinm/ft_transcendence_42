// function initializeSaveButton() {
//     console.log("Initializing save button...");

//     const saveButton = document.getElementById("save-button");

//     if (!saveButton) {
//         console.error("Save button not found!");
//         return;
//     }

//     saveButton.addEventListener("click", async (event) => {
//         event.preventDefault();
//         console.log("Save button clicked.");

//         const form = document.getElementById("profile-settings-form");
//         if (!form) {
//             console.error("Form not found!");
//             return;
//         }

//         const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
//         if (!csrfTokenElement) {
//             console.error("CSRF token not found.");
//             return;
//         }

//         const csrfToken = csrfTokenElement.value;
//         const formData = new FormData(form);

//         try {
//             fetch("/find_friend/", {
//                 method: "POST",
//                 body: formData,
//             })
//                 .then((response) => response.json())
//                 .then((data) => {
//                     if (data.exists) {
//                         const url = `/profile_settings/`;
//                         usernameButton.setAttribute("data-navigate", url);
//                         usernameButton.click();
//                     } else {
//                         displayErrorMessage(data.message || "User not found.");
//                     }
//                 })
//                 .catch(() => {
//                     displayErrorMessage("An error occurred while checking the User.");
//                 });
        

//             // const response = await fetch(form.action, {
//             //     method: "POST",
//             //     body: formData,
//             // });

//             if (response.ok) {
//                 const data = await response.json();
//                 console.log("Server response:", data);

//                 const feedback = document.getElementById("settings-feedback");
//                 if (feedback) {
//                     feedback.style.display = "block";
//                     feedback.textContent = data.message || "Settings updated successfully.";
//                     feedback.className = "alert alert-success";
//                 }
//             } else {
//                 const errorText = await response.text();
//                 console.error("Server error:", errorText);
//                 const parsedError = JSON.parse(errorText)
//                 const feedback = document.getElementById("settings-feedback");
//                 if (feedback) {
//                     feedback.style.display = "block";
//                     if (parsedError.errors.nickname) {
//                       feedback.textContent = parsedError.errors.nickname[0];
//                     } else if (parsedError.errors.photo) {
//                       feedback.textContent = parsedError.errors.photo[0];
//                     } else if (parsedError.errors.description) {
//                       feedback.textContent = parsedError.errors.description[0];
//                     } else {
//                       feedback.textContent = "An unknown error occurred.";
//                     }
//                     feedback.className = "alert alert-danger";
//                 }
//             }
//         } catch (error) {
//             console.error("Request failed:", error);

//             const feedback = document.getElementById("settings-feedback");
//             if (feedback) {
//                 feedback.style.display = "block";
//                 feedback.textContent = "An unexpected error occurred.";
//                 feedback.className = "alert alert-danger";
//             }
//         }
//     });
    

// }

function initializeSaveButton() {
    const tournamentInput = document.getElementById('tournament-nickname').value.trim();
    const photoInput = document.getElementById('photo');
    const descriptiontInput = document.getElementById('description').value.trim();

    const settingsButton = document.getElementById("save-button");

	if (tournamentInput.length < 3) {
		displayErrorMessage("Tournament name must be at least 3 characters long.");
		return;
	} else if (tournamentInput.length > 25) {
		displayErrorMessage("Tournament name cannot be more than 25 characters.");
		return;
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
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
            if (data.exists) {
                // const url = `/profile_settings/`;
                // settingsButton.setAttribute("data-navigate", url);
                // settingsButton.click();
                alert("Settings updated successfully.")
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
