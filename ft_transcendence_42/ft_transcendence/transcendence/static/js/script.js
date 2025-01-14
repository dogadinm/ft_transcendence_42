function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(section => {
        section.classList.remove("active");
    });

    // Display selected section
    const section = document.getElementById(sectionId);
    section.classList.add("active");

    // Stop Pong game if switching to a different section
    if (sectionId !== 'pong-game-section') {
        stopPongGame();
    }
}

//async function navigate(url, updateProfile = false) {
//    try {
//        const response = await fetch(url, {
//            method: "GET",
//            headers: {
//                "X-Requested-With": "XMLHttpRequest",
//            },
//        });
//
//        if (response.ok) {
//            const html = await response.text();
//
//            const parser = new DOMParser();
//            const doc = parser.parseFromString(html, "text/html");
//
//            const newContent = doc.querySelector("#content");
//            const newProfileContent = doc.querySelector("#profile_content");
//
////            history.pushState(null, "", url);
//
//            updateUserLinks();
//
//            if (newContent) {
//                history.pushState(null, "", url);
//                document.querySelector("#content").innerHTML = newContent.innerHTML;
//
//            }
//            if (updateProfile && newProfileContent) {
//
//                document.querySelector("#profile_content").innerHTML = newProfileContent.innerHTML;
//                console.log(html)
//                executeScriptsInContent(html);
//            }
//
//
//            executeScriptsInContent(html);
//
//        } else {
//            console.error("Failed to fetch page:", response.status);
//        }
//    } catch (error) {
//        console.error("Error during navigation:", error);
//    }
//}

async function loadPage(url) {
    console.log("Loading page:", url);
    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest", // AJAX-запрос
            },
        });

        if (response.ok) {
            const html = await response.text();
//            document.getElementById("content").innerHTML = html;
//            history.pushState(null, "", url);

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newContent = doc.querySelector("#profile_content");
            history.pushState(null, "", url);


            if (newContent) {
                document.querySelector("#profile_content").innerHTML = newContent.innerHTML;
            } else {
                console.error("Content block not found.");
            }
            executeScriptsInContent(html);


        } else {
            console.error("Failed to load page:", response.status);
        }
    } catch (error) {
        console.error("Error loading page:", error);
    }
}

async function navigate(url) {
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
            const newContent = doc.querySelector("#content");
            history.pushState(null, "", url);
            updateUserLinks()

            if (newContent) {
                document.querySelector("#content").innerHTML = newContent.innerHTML;
            } else {
                console.error("Content block not found.");
            }
            executeScriptsInContent(html);
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

        const oldScripts = document.querySelectorAll("script");
        oldScripts.forEach(script => script.remove());
        document.body.appendChild(newScript);
    });
}

function removeOldScripts() {

    const oldScripts = document.querySelectorAll("script");

    const scriptsArray = Array.from(oldScripts);


    scriptsArray.forEach(script => {
        script.remove();
    });

    console.log("Removed scripts:", scriptsArray);
}