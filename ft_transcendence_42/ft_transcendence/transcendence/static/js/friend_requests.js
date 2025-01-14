document.addEventListener('DOMContentLoaded', function () {
    const requestsContainer = document.getElementById('friend-requests-container');
    console.log(requestsContainer)
    // Обработчик кнопок Accept/Reject
    requestsContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('accept-request') || e.target.classList.contains('decline-request')) {
            const button = e.target;
            const action = button.classList.contains('accept-request') ? 'accept_request' : 'decline_request';
            const requestDiv = button.closest('.friend-request');
            const username = requestDiv.getAttribute('data-username');

            // Отправка AJAX-запроса
            fetch('', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: new URLSearchParams({
                    action: action,
                    sender_request: username,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        if (action === 'accept_request') {
                            alert('Friend request accepted.');
                        } else {
                            alert('Friend request declined.');
                        }
                        // Удаление запроса из интерфейса
                        requestDiv.remove();
                    } else {
                        alert('Error processing the request.');
                    }
                })
                .catch((error) => console.error('Error:', error));
        }
    });
});