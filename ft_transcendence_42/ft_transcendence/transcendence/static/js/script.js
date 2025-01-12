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
