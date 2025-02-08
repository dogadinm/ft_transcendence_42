// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0 <0.9.0;

contract MultisigTournament {

    // Struct definition
    struct Tournament {
        string tournament_id;
        uint256 game_id;
        string game_type;
        string loser_name;
        uint256 loser_score;
        string winner_name;
        uint256 winner_score;
        bool winnerApproved;
        bool loserApproved;
        address winner;
        address loser;
    }

    // Mapping to store games by tournament ID and game ID
    mapping(string => mapping(uint256 => Tournament)) public tournaments;

    event Approved(address user, string tournament_id, uint256 game_id);
    event GameWasFullyApproved(string tournament_id, uint256 game_id);
    event GameAdded(
        string tournament_id,
        uint256 game_id,
        string game_type,
        string loser_name,
        uint256 loser_score,
        string winner_name,
        uint256 winner_score,
		address winner,
		address loser
    );

    modifier onlyParticipants(string memory _tournament_id, uint256 _game_id) {
        Tournament memory game = tournaments[_tournament_id][_game_id];
        require(
            msg.sender == game.winner || msg.sender == game.loser,
            "Not a participant"
        );
        _;
    }

    // Function to approve a game
    function approve(string memory _tournament_id, uint256 _game_id) public onlyParticipants(_tournament_id, _game_id) {
        Tournament storage game = tournaments[_tournament_id][_game_id];
        if (msg.sender == game.winner) {
            game.winnerApproved = true;
        } else if (msg.sender == game.loser) {
            game.loserApproved = true;
        }
        emit Approved(msg.sender, _tournament_id, _game_id);
    }

	function execute(
    string memory _tournament_id,
    uint256 _game_id,
    string memory _game_type,
    string memory _loser_name,
    uint256 _loser_score,
    string memory _winner_name,
    uint256 _winner_score,
    address _winner,
    address _loser
) public onlyParticipants(_tournament_id, _game_id) returns (bool) {
    Tournament storage game = tournaments[_tournament_id][_game_id];
    
    // Check if both participants have approved
    if (game.winnerApproved && game.loserApproved) {
        // Add the game details
        tournaments[_tournament_id][_game_id] = Tournament(
            _tournament_id,
            _game_id,
            _game_type,
            _loser_name,
            _loser_score,
            _winner_name,
            _winner_score,
            game.winnerApproved,
            game.loserApproved,
            _winner,
            _loser
        );

        // Emit the executed event
        emit GameWasFullyApproved(_tournament_id, _game_id);
        return true; // Return true if executed successfully
    }
    
    return false; // Return false if approvals are not met
}


    // // Function to execute after both participants approve
    // function execute(
    //     string memory _tournament_id,
    //     uint256 _game_id,
    //     string memory _game_type,
    //     string memory _loser_name,
    //     uint256 _loser_score,
    //     string memory _winner_name,
    //     uint256 _winner_score,
    //     address _winner,
    //     address _loser
    // ) public onlyParticipants(_tournament_id, _game_id) {
    //     Tournament storage game = tournaments[_tournament_id][_game_id];
    //     require(game.winnerApproved && game.loserApproved, "Both users must approve");

    //     Call the addGame function
    //     addGame(
    //         _tournament_id,
    //         _game_id,
    //         _game_type,
    //         _loser_name,
    //         _loser_score,
    //         _winner_name,
    //         _winner_score,
    //         _winner,
    //         _loser
    //     );
    //     emit Executed(_tournament_id, _game_id);
    // }

	// function isApprovedGame(string memory _tournament_id, uint256 _game_id)
	// {

	// }

	// New function to check if the game is approved
    function getApproval(string memory _tournament_id, uint256 _game_id) public view returns (bool) {
        Tournament memory game = tournaments[_tournament_id][_game_id];
        return game.winnerApproved && game.loserApproved;
    }

    // Function to add a game
    function addGame(
        string memory _tournament_id,
        uint256 _game_id,
        string memory _game_type,
        string memory _loser_name,
        uint256 _loser_score,
        string memory _winner_name,
        uint256 _winner_score,
        address _winner,
        address _loser
    ) public {
        // Ensure the game doesn't already exist
        require(
            bytes(tournaments[_tournament_id][_game_id].tournament_id).length == 0,
            "Game already exists"
        );

        // Add the game to the mapping
        tournaments[_tournament_id][_game_id] = Tournament(
            _tournament_id,
            _game_id,
            _game_type,
            _loser_name,
            _loser_score,
            _winner_name,
            _winner_score,
            false,
            false,
            _winner,
            _loser
        );

        // Emit the GameAdded event
        emit GameAdded(
            _tournament_id,
            _game_id,
            _game_type,
            _loser_name,
            _loser_score,
            _winner_name,
            _winner_score,
			_winner,
			_loser
        );
    }

    // Function to retrieve game details
    function getGame(string memory _tournament_id, uint256 _game_id)
        public
        view
        returns (Tournament memory)
    {
        return tournaments[_tournament_id][_game_id];
    }

    // Function to retrieve all data of a tournament game
    function getTournamentInfo(string memory _tournament_id, uint256 _game_id)
        public
        view
        returns (Tournament memory)
    {
        return tournaments[_tournament_id][_game_id];
    }
}
