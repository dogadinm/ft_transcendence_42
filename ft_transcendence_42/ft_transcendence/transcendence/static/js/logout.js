async function logOut() {
    try{
        const logOutButton = document.getElementById("logout-button");
        const response = await fetch('/logout/', {
            method: "GET",     
        });
        const data = await response.json();

        if (response.ok) {
            if (data.redirect) {
                logOutButton.setAttribute("data-navigate", data.redirect);
                logOutButton.click();
                updateUserLinks();
                // updateCSRFToken();
            }
        } else {
            const errorMessage = data.error || "An error occurred.";
            document.getElementById("error-message").textContent = errorMessage;
        }
    } catch (error) {
        console.error("Error:", error);
    }
};