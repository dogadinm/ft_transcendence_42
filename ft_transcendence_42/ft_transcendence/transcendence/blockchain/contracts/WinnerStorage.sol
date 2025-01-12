pragma solidity >=0.6.0 <0.9.0;

contract WinnerStorage {
    uint256 public score;

    // Event to emit when score is updated
    event scoreUpdated(uint256 oldscore, uint256 newscore);
	// Event to emit when user is added
	event userAdded();

	//Struct definition
	struct User {
		uint256 score;
		string	name;
		bool	winner;
	}

	//Array to store users
	User[] public users;

	//Mapping from name to score
	mapping(string => uint256) public nameToScore;

	//Maping from name to status
	mapping(string => bool) public nameToStatus;

    // Function to retrieve the score
    function retrieve() public view returns (uint256) {
        return score;
    }

	// Function to add users
	function addUser(string memory _name, uint256 _score, bool _winner) public {
		users.push(User(_score, _name, _winner));
		nameToScore[_name] = _score;
		nameToStatus[_name] = _winner;
		emit userAdded();
	}

	    // Function to store a score
    function storeScore(string memory _name, uint256 _score) public {
        uint256 oldscore = score; // Store the current score value
        score = oldscore + _score; // Update the score variable
		nameToScore[_name] = score;
        emit scoreUpdated(oldscore, score); // Emit the event
    }

	//Function to update winner status

}