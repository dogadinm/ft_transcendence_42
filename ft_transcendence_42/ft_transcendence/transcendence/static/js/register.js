document.getElementById("register-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    try {

        const response = await fetch("/register/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
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
        console.error("Error:", error); // Обрабатываем исключения
    }
});