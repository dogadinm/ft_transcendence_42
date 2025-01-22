function navigateToDoublejack() {
      const doublejackInput = document.getElementById('doublejack-input').value.trim();

      if (doublejackInput) {
        if (doublejackInput.length < 1) {
          displayErrorMessage("Doublejack must be at least 3 characters long.");
          return;
        } else if (doublejackInput.length > 8) {
          displayErrorMessage("Doublejack cannot be more than 25 characters.");
          return;
        } else if (!/^[a-zA-Z0-9]+$/.test(doublejackInput)) {
          displayErrorMessage("Doublejack can only contain letters and digits.");
          return;
        }

        const formData = new FormData();
        formData.append('doublejack_name', doublejackInput);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        // Log the FormData object after appending all values
        fetch("/find_doublejack/", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                const url = `/doublejack_lobby/${data.doublejack_name}`;
                navigate(url);
            } else {
                displayErrorMessage(data.message || "Doublejack not found.");
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while checking the doublejack.");
        });
    } else {
        displayErrorMessage("Please enter a doublejack name.");
    }
}

function displayErrorMessage(message) {
    const errorElement = document.getElementById("error-message");
    errorElement.textContent = message;
    errorElement.style.color = "red";
}