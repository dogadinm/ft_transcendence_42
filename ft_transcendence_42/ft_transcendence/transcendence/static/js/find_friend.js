function navigateToProfile() {
    const usernameInput = document.getElementById('username-input').value.trim();

    if (usernameInput) {
        const url = `/profile/${encodeURIComponent(usernameInput)}`; // Construct URL dynamically
        navigate(url); // Call loadPage to fetch and update the content
    } else {
        const errorMessage = "User not found.";
        document.getElementById("error-message").textContent = errorMessage;
    }
}