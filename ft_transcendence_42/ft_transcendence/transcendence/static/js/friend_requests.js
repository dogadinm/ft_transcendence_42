function initializeFriendRequestsScript() {
    console.log('Initializing friend requests script...');

    const requestsContainer = document.getElementById('friend-requests-container');
    console.log('Friend requests container:', requestsContainer);

    if (!requestsContainer) {
        console.error('Container not found!');
        return;
    }

    requestsContainer.addEventListener('click', function (e) {
        console.log('Click detected:', e.target);

        if (e.target.classList.contains('accept-request') || e.target.classList.contains('decline-request')) {
            const button = e.target;
            const action = button.classList.contains('accept-request') ? 'accept_request' : 'decline_request';
            const requestDiv = button.closest('.friend-request');

            if (!requestDiv) {
                console.error('Request div not found!');
                return;
            }

            const username = requestDiv.getAttribute('data-username');
            console.log('Action:', action, 'Username:', username);

            fetch('/friend_requests/', {
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
                    console.log('Response data:', data);

                    if (data.success) {
                        if (action === 'accept_request') {
                            alert('Friend request accepted.');
                        } else {
                            alert('Friend request declined.');
                        }

                        requestDiv.remove();
                    } else {
                        alert('Error processing the request.');
                    }
                })
                .catch((error) => {
                    console.error('Fetch error:', error);
                });
        }
    });
}

initializeFriendRequestsScript();