document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", async function (event) {
        const target = event.target;

        // Проверяем, есть ли действие у элемента
        if (target && target.dataset.action) {
            event.preventDefault();

            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
            if (!csrfToken) {
                console.error("CSRF token not found.");
                return;
            }

            const action = target.dataset.action;
            const username = target.dataset.username || "";

            const formData = new FormData();
            formData.append("action", action);
            formData.append("csrfmiddlewaretoken", csrfToken.value);

            if (username) {
                formData.append("sender_request", username);
            }

            try {
                const response = await fetch(window.location.href, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                });

                const contentType = response.headers.get("Content-Type");
                if (contentType && contentType.includes("application/json")) {
                    const data = await response.json();

                    if (data.success) {
                        // Обновляем HTML контент в контейнере действий
                        const actionsContainer = document.querySelector("#profile-actions-container");
                        const actionsContent = document.querySelector("#profile-actions-content");

                        if (actionsContent) {
                            actionsContent.innerHTML = data.html; // вставляем обновленный HTML
                        }

                        // Вставляем сообщение от сервера
                        const messageContainer = document.querySelector("#message-container");
                        if (messageContainer) {
                            messageContainer.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                        }
                    } else {
                        alert(data.message || "An error occurred.");
                    }
                } else {
                    console.error("Invalid response format. Expected JSON.");
                    const html = await response.text();
                    console.error(html);
                    alert("An unexpected error occurred.");
                }
            } catch (error) {
                console.error("Fetch error:", error);
                alert("An error occurred. Please try again.");
            }
        }
    });
});