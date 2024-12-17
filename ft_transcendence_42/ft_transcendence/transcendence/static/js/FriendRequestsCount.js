function updateFriendRequestsCount() {
    fetch('/api/friend_requests_count/')
        .then(response => response.json())
        .then(data => {
            const count = data.count;
            const profileLink = document.querySelector('a[href*="profile"]');
            if (profileLink) {
                let badge = document.getElementById('friend-requests-badge');

                if (count > 0) {
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.id = 'friend-requests-badge';
                        badge.style.cssText = `
                            background-color: red;
                            color: white;
                            border-radius: 50%;
                            padding: 5px 10px;
                            font-size: 14px;
                            margin-left: 5px;
                        `;
                        profileLink.appendChild(badge);
                    }
                    badge.textContent = count;
                } else if (badge) {
                    badge.remove();
                }
            } else {
                console.error('Profile link not found!');
            }
        })
        .catch(error => console.error('Error fetching friend requests count:', error));
}


document.addEventListener('DOMContentLoaded', function () {
    updateFriendRequestsCount();


    setInterval(updateFriendRequestsCount, 5000);
});
