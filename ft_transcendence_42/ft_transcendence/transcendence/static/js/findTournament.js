function navigateToTournament() {
	const tournamentInput = document.getElementById('tournament-input').value.trim();

	if (tournamentInput) {
		if (tournamentInput.length < 3) {
			displayErrorMessage("Tournament name must be at least 3 characters long.");
			return;
		} else if (tournamentInput.length > 25) {
			displayErrorMessage("Tournament name cannot be more than 25 characters.");
			return;
		} else if (!/^[a-zA-Z0-9]+$/.test(tournamentInput)) {
			displayErrorMessage("Tournament name can only contain letters and digits.");
			return;
		}

		const formData = new FormData();
		formData.append('tournament_name', tournamentInput);
		formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

		fetch("/find_tournament/", {
			method: "POST",
			body: formData,
		})
		.then(response => {
			// Check for status 403 (wallet data missing) or similar condition
			if (response.status === 403) {
				throw new Error("Wallet data is missing. Please bind your wallet first.");
			}
			return response.json();
		})
		.then(data => {
			if (data.exists) {
				const url = `/tournament/${data.tournament_name}`;
				navigate(url);
			} else {
				displayErrorMessage(data.message || "Tournament not found.");
			}
		})
		.catch(error => {
			displayErrorMessage(error.message || "An error occurred while checking the tournament.");
		});
	} else {
		displayErrorMessage("Please enter a tournament name.");
	}
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "red";
}


// function navigateToTournament() {
// 	const tournamentInput = document.getElementById('tournament-input').value.trim();

// 	if (tournamentInput) {
// 	  if (tournamentInput.length < 1) {
// 		displayErrorMessage("tournament must be at least 3 characters long.");
// 		return;
// 	  } else if (tournamentInput.length > 8) {
// 		displayErrorMessage("tournament cannot be more than 25 characters.");
// 		return;
// 	  } else if (!/^[a-zA-Z0-9]+$/.test(tournamentInput)) {
// 		displayErrorMessage("tournament can only contain letters and digits.");
// 		return;
// 	  }

// 	  const formData = new FormData();
// 	  formData.append('tournament_name', tournamentInput);
// 	  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

// 	  // Log the FormData object after appending all values
// 	  fetch("/find_tournament/", {
// 		  method: "POST",
// 		  body: formData,
// 	  })
// 	  .then(response => response.json())
// 	  .then(data => {
// 		  if (data.exists) {
// 			  const url = `/tournament/${data.tournament_name}`;
// 			  navigate(url);
// 		  } else {
// 			  displayErrorMessage(data.message || "tournament not found.");
// 		  }
// 	  })
// 	  .catch(() => {
// 		  displayErrorMessage("An error occurred while checking the tournament.");
// 	  });
//   } else {
// 	  displayErrorMessage("Please enter a tournament name.");
//   }
// }

// function displayErrorMessage(message) {
//   const errorElement = document.getElementById("error-message");
//   errorElement.textContent = message;
//   errorElement.style.color = "red";
// }