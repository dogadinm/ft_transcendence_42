async function logOut() {
    try{
        const response = await fetch('/logout/', {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest", // AJAX-запрос
            },
        });
        const data = await response.json();

        if (response.ok) {
            if (data.redirect) {
                navigate(data.redirect);
            }
        } else {
            const errorMessage = data.error || "An error occurred.";
            document.getElementById("error-message").textContent = errorMessage;
        }
    } catch (error) {
        console.error("Error:", error);
    }
};