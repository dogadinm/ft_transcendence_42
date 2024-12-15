// Establish WebSocket connection
id = 0;
const ws = new WebSocket(`ws://${window.location.host}/ws/doublejack/`);

// Set status message when WebSocket opens
ws.onopen = function(event) {
	document.getElementById('ws_status').textContent = 'Connected to WebSocket';
};

// Handle messages received from the WebSocket
ws.onmessage = function(event) {
	const data = JSON.parse(event.data);
	if (data && data.joined) {
		id = data.joined;
	}
	if (data && data.reset) {
		document.getElementById('buttons').innerHTML = '<button id="reset">RESET !</button>'
		document.getElementById('reset').onclick = function() {
			const message = {
				action: 'reset'  // This is the action we'll send to the WebSocket
			};
			ws.send(JSON.stringify(message));  // Send the action to WebSocket
		};
	}
	if (data && data.set) {
		document.getElementById('buttons').innerHTML = '<button id="hit">HIT !</button><button id="stay">STAY!</button>'
		document.getElementById('hit').onclick = function() {
			const message = {
				action: 'hit'  // This is the action we'll send to the WebSocket
			};
			ws.send(JSON.stringify(message));  // Send the action to WebSocket
		};
		document.getElementById('stay').onclick = function() {
			const message = {
				action: 'stay'  // This is the action we'll send to the WebSocket
			};
			ws.send(JSON.stringify(message));  // Send the action to WebSocket
		};
	}
	if (data && data.disable) {
		document.getElementById('buttons').innerHTML = '<p>Waiting for the other player...</p>'
	}
	if (data && data.color && data.role && id == data.role) {
		// Change the background color when a message is received
		document.body.style.backgroundColor = data.color;
	}
	if (data && data.name) {
		if (data.role) {
			if (id == data.role)
				document.getElementById('name').innerHTML = data.name;
			else if (id != data.role)
				document.getElementById('other_name').innerHTML = data.name;
		}
	}
	if (data && data.role && id == data.role) {

		document.getElementById('role').innerHTML = data.role;

	}
	if (data && 'points' in data) {
		if (data.role) {
			if (id == data.role)
				document.getElementById('points').innerHTML = data.points;
			else if (id != data.role)
				document.getElementById('other_points').innerHTML = data.points;
		}
	}
	if (data && 'status' in data) {
		if (data.role) {
			if (id == data.role)
				document.getElementById('my_status').innerHTML = data.status;
			else if (id != data.role)
				document.getElementById('other_status').innerHTML = data.status;
		}
	}
	if (data && data.hand) {
		const handElement = id == data.role
			? document.getElementById('hand')
			: document.getElementById('other_hand');

		// Clear any previous hand content
		handElement.innerHTML = '';

		// Split the data.hand string into chunks of 7 characters
		const cards = [];
		for (let i = 0; i < data.hand.length; i += 7) {
			cards.push(data.hand.substring(i, i + 7).trim());
		}

		// Reverse the cards array for the other hand
		if (id != data.role) {
			cards.reverse();
		}

		// Create image elements for each card in the hand
		cards.forEach(card => {
			const img = document.createElement('img');
			img.src = `/static/js/cards/${card}`; // Path to the images
			img.alt = card;
			img.style.width = '50px'; // Optional: Adjust image size
			img.style.margin = '5px'; // Optional: Add spacing between images
			// Rotate the cards upside down if it's the other_hand
			if (id != data.role) {
				img.style.transform = 'rotate(180deg)'; // Rotate the image
			}
			handElement.appendChild(img);
		});
	}

	if (data && data.score) {
		if (data.role) {
			if (id == data.role)
				document.getElementById('score').innerHTML = data.score;
			else if (id != data.role)
				document.getElementById('other_score').innerHTML = data.score;
		}
	}

	if (data && data.countdown) {

		document.getElementById('time').innerHTML = data.countdown;
	}
};

// Handle WebSocket error
ws.onerror = function(error) {
	console.error('WebSocket Error:', error);
	document.getElementById('ws_status').textContent = 'WebSocket Error';
};

// Handle WebSocket closure
ws.onclose = function(event) {
	document.getElementById('ws_status').textContent = 'WebSocket connection closed';
};

// Send a signal when the button is clicked
document.getElementById('join').onclick = function() {
	const message = {
		action: 'join'  // This is the action we'll send to the WebSocket
	};
	ws.send(JSON.stringify(message));  // Send the action to WebSocket
};
