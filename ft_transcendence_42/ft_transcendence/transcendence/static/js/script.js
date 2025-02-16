if (!window.loadedScripts) {
    window.loadedScripts = new Set();
}
if (!window.chatSocket) {
    window.chatSocket = null;
}
if (!window.statusSocket) {
    window.statusSocket = null;
}
if (!window.lobbySocket) {
    window.lobbySocket = null;
}
if (!window.tournamentLobbySocket) {
    window.tournamentLobbySocket = null;
}
if (!window.isEventListenerAdded) {
    window.isEventListenerAdded = false;
}

async function navigate(url, addToHistory = true) {
    // console.log(window.lobbySocket)
    // console.log(window.tournamentLobbySocket)
    // if (window.chatSocket) {
    //     window.chatSocket.close();
    // }
    // if (window.lobbySocket) {
    //     window.lobbySocket.close();
    // }
    // if (window.tournamentLobbySocket) {
    //     window.tournamentLobbySocket.close();
    // }
    // console.log(window.lobbySocket)
    // console.log(window.tournamentLobbySocket)
    try {
        const response = await fetch(url, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });

        if (response.ok) {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newContent = doc.querySelector("#content");

            if (newContent) {
                document.querySelector("#content").innerHTML = newContent.innerHTML;
                executeScriptsInContent(html);
                // updateUserLinks();


                if (addToHistory) {
                    history.pushState(null, "", url);
                }
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

function executeScriptsInContent(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const scripts = doc.querySelectorAll("script");

    const exceptions = ["tournament.js", "pongLobby.js", "chat.js", "pongScript.js"];

    scripts.forEach(script => {
        const src = script.src;

        if (src) {
            const isException = exceptions.some(exception => src.includes(exception));

            if (!isException && window.loadedScripts.has(src)) {
                // console.log(`Script ${src} is already loaded.`);
                return;
            }

            if (!isException) {
                window.loadedScripts.add(src);
            }
        }

        const newScript = document.createElement("script");
        if (src) {
            newScript.src = src;
            newScript.async = true;
        } else {
            newScript.text = script.textContent;
        }

        document.body.appendChild(newScript);
    });
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

// function startStatus() {
//     if (window.statusSocket && window.statusSocket.readyState === WebSocket.OPEN) {
//         console.log("WebSocket connection is already open.");
//         return;
//     }

//     if (window.statusSocket) {
//         window.statusSocket.close();
//     }

//     window.statusSocket = new WebSocket(`ws://${window.location.host}/ws/status/`);

//     window.statusSocket.onmessage = function (e) {
//         const data = JSON.parse(e.data);
//         console.log(data.type);

//         if (data.type === 'user_status') {
//             const friendItems = document.querySelectorAll('.friend-item');
//             const onlineUsernames = new Set(data.users || []);

//             friendItems.forEach((item) => {
//                 const name = item.dataset.name;
//                 const statusIndicator = item.querySelector('.status-indicator');

//                 if (statusIndicator) {
//                     if (onlineUsernames.has(name)) {
//                         statusIndicator.style.backgroundColor = 'green'; 
//                     } else {
//                         statusIndicator.style.backgroundColor = 'red'; 
//                     }
//                 }
//             });
//         }
//     };

//     window.statusSocket.onclose = function () {
//         console.log("WebSocket connection closed. Reconnecting...");
//         setTimeout(startStatus, 3000);
//     };

//     window.statusSocket.onerror = function (error) {
//         console.error("WebSocket error:", error);
//     };
// }

// document.addEventListener("DOMContentLoaded", function () {
//     if (!window.statusSocket || window.statusSocket.readyState !== WebSocket.OPEN) {
//         startStatus();
//     }
// });


function handleNavigation(event) {
    const target = event.target.closest("[data-navigate]");
    if (target) {
        event.preventDefault();
        const url = target.getAttribute("data-navigate");
        navigate(url);
    }
}

window.addEventListener("popstate", () => {
    navigate(location.pathname, false);
});

function setupEventListeners() {
    if (window.isEventListenerAdded) return;
    window.isEventListenerAdded = true;

    document.addEventListener("click", (event) => {
        const link = event.target.closest("a.ajax-link");
        if (link && event.target.tagName === "A") {
            event.preventDefault();
            navigate(link.href);
        }
    });

    document.addEventListener("click", (event) => {
        const target = event.target.closest("[data-navigate]");
        if (target) {
            event.preventDefault();
            const url = target.getAttribute("data-navigate");
            navigate(url);
        }
    });
}

document.addEventListener("DOMContentLoaded", setupEventListeners);