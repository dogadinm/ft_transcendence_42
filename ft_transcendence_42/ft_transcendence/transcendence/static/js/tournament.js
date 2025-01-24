(function () {
    let movingDown = false;
    let movingUp = false;
    let isReady = false;


    const gameDataElement = document.getElementById("gameData");
    const room = gameDataElement.dataset.roomLobby;
    const url = `ws://${window.location.host}/ws/tournament/${room}/`;
    console.log(url)
    const chatSocket = new WebSocket(url);


    // Add event listeners for key events once
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data.type);


        switch (data.type) {
            case "connection":
                username = data.username;
                updateRoleDisplay(data.role);
                break;

            default:
                console.warn(`Unhandled message type: ${data.type}`);
        }
    };
})();