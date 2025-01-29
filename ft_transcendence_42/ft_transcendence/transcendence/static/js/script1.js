window.addEventListener('popstate', (event) => {
    const state = event.state;
    if (state && state.url) {
        navigate(state.url, false); // Pass `false` to avoid pushing state again
    }
});

let chatSocket = null;
let statusSocket = null;
let lobbySocket  = null;
// let ws = null;

async function navigate(url, pushHistory = true) {

    if (statusSocket) {
        statusSocket.close();
    }

    if (chatSocket) {
        chatSocket.close();
    }
    // if (ws) {
    //     ws.close();
    // }

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (response.ok) {
            const html = await response.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            console.log(doc);
            const newContent = doc.querySelector("#content");
            
            if (newContent) {
                document.querySelector("#content").innerHTML = newContent.innerHTML;
                if (pushHistory) {
                history.pushState({ url: url }, "", url);
                }
                updateUserLinks();
                executeScriptsInContent(html);
            } else {
                console.error("Content block not found.");
            }
            
        } else {
            console.error("Failed to fetch page:", response.status);
        }
    } catch (error) {
        console.error("Error during navigation:", error);
    }
}


async function updateUserLinks() {
    try {
        const response = await fetch("/user-links/", {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (response.ok) {
            const html = await response.text();
            document.getElementById("user-links").innerHTML = html;
        } else {
            console.error("Failed to update user links:", response.status);
        }
    } catch (error) {
        console.error("Error updating user links:", error);
    }
}


function executeScriptsInContent(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const scripts = doc.querySelectorAll("script");

    scripts.forEach(script => {
        const newScript = document.createElement("script");
        newScript.src = script.src || '';
        newScript.text = script.textContent || script.innerText;
        //const oldScripts = document.querySelectorAll("script");
        //oldScripts.forEach(script => script.remove());
        removeOldScripts();
        document.body.appendChild(newScript);
    });
}

function removeOldScripts() {
    const oldScripts = document.querySelectorAll("script");
    oldScripts.forEach(script => {
        script.remove();
    });
    console.log("Removed scripts:", scriptsArray);
}

function startSatus() {
    if(statusSocket){
        statusSocket.close();
    }

    statusSocket = new WebSocket(`ws://${window.location.host}/ws/status/`);

    statusSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data.type);

        if (data.type === 'user_status') {
            const friendItems = document.querySelectorAll('.friend-item');
            const onlineUsernames = new Set(data.users || []);

            friendItems.forEach((item) => {
                const name = item.dataset.name;
                const statusIndicator = item.querySelector('.status-indicator');

                if (onlineUsernames.has(name)) {
                    statusIndicator.classList.remove('offline');
                    statusIndicator.classList.add('online');
                    statusIndicator.style.backgroundColor = 'green';
                } else {
                    statusIndicator.classList.remove('online');
                    statusIndicator.classList.add('offline');
                    statusIndicator.style.backgroundColor = 'red';
                }
            });
        }
    };
}
startSatus();
