document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Предотвращает стандартную отправку формы

    const formData = new FormData(this); // Собирает данные из формы
    try {
        const response = await fetch("/login/", {
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
        console.error("Error:", error);
    }
});