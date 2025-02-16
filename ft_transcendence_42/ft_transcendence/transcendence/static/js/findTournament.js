function navigateToTournament() {
    const tournamentInput = document.getElementById("tournament-input").value.trim();
    const tournamentButton = document.getElementById("tournament-button");

	if (tournamentInput.length < 3) {
		displayErrorMessage("Tournament name must be at least 3 characters long.");
		return;
	} else if (tournamentInput.length > 8) {
		displayErrorMessage("Tournament name cannot be more than 8 charaters.");
		return;
	} else if (!/^[a-zA-Z0-9]+$/.test(tournamentInput)) {
		displayErrorMessage("Tournament name can only contain letters and digits.");
		return;
	}

    const formData = new FormData();
    formData.append("tournament_name", tournamentInput);
    formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
    );

    fetch("/find_tournament/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.exists) {
                const url = `/tournament/${data.tournament_name}`;
                tournamentButton.setAttribute("data-navigate", url);
                tournamentButton.click();
            } else if (data.results){
                console.log(data.results)
                displayResults(data.results);
            }
            else {
                displayErrorMessage(data.message || "Lobby not found.");
            }
        })
        .catch(() => {
            displayErrorMessage("An error occurred while checking the lobby.");
        });
}

function displayErrorMessage(message) {
	const errorElement = document.getElementById("error-message");
	errorElement.textContent = message;
	errorElement.style.color = "#1abc9c";
}

// function displayResults(message) {
// 	const resultsElement = document.getElementById("results-message");
// 	resultsElement.textContent = message;
// 	resultsElement.style.color = "#1abc9c";
// }

// script.js - Function to display the results in a table
function displayResults(results) {
    const resultsElement = document.getElementById("results-message");
    
    // Create a table element
    const table = document.createElement('table');

    // Apply light lilac color to the table's background
    table.style.border = '1px solid #ddd';
    table.style.marginTop = '20px';
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.backgroundColor = '#D8B0D0'; // Light lilac background color
    
    // Define table headers based on your tuple data structure
    const headers = [
        'Tournament ID', 'Game ID', 'Game Type', 'Loser', 'Loser Score', 'Winner', 'Winner Score', 'Loser Signed', 'Verified', 'Winner Address', 'Loser Address'
    ];

    // Add a header row to the table
    const headerRow = table.insertRow();
    headers.forEach(header => {
        const cell = headerRow.insertCell();
        cell.textContent = header;
        cell.style.border = '1px solid black';
        cell.style.padding = '8px';
    });

    // Add rows for each result (converted tuple data to object)
    results.forEach(result => {
        const row = table.insertRow();
        result.forEach(value => {
            const cell = row.insertCell();
            cell.textContent = value;
            cell.style.border = '1px solid black';
            cell.style.padding = '8px';
        });
    });

    // Clear the previous content in the message element
    resultsElement.innerHTML = '';

    // Append the table to the results element
    resultsElement.appendChild(table);
}
