// Import the TournamentScore contract artifact
const MultisigTournament = artifacts.require("MultisigTournament");

module.exports = function (deployer) {
  // Deploy the TournamentScore contract without hardcoding participant addresses
  deployer.deploy(MultisigTournament);
};
