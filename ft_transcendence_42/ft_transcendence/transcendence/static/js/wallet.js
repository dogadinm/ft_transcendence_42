function  connectWallet() {
	const wallInput = document.getElementById('wallet-input').value.trim();
	const keyInput = document.getElementById('private_key').value.trim();

	if (wallInput && keyInput) {
	  if (wallInput.length < 1) {
		displayErrorMessage("Lobby must be at least 3 characters long.");
		return;
	  } else if (lobbyInput.length > 8) {
		displayErrorMessage("Lobby cannot be more than 25 characters.");
		return;
	  } else if (!/^[a-zA-Z0-9]+$/.test(wallInput)) {
		displayErrorMessage("Lobby can only contain letters and digits.");
		return;
	  }

	  const formData = new FormData();
	  formData.append('wallet', wallInput);
	  formData.append('key', keyInput);
	  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

	  // Log the FormData object after appending all values
	  fetch("/bind_wallet/", {
		  method: "POST",
		  body: formData,
	  })
	  .then(response => response.json())
	  .then(data => {
		  if (data.exists) {
			  const url = `/tournament/`;
			  navigate(url);
		  } else {
			  displayErrorMessage(data.message || "Lobby not found.");
		  }
	  })
	  .catch(() => {
		  displayErrorMessage("An error occurred while checking the lobby.");
	  });
  } else {
	  displayErrorMessage("Please enter a lobby name.");
  }
}

function displayErrorMessage(message) {
  const errorElement = document.getElementById("error-message");
  errorElement.textContent = message;
  errorElement.style.color = "red";
}