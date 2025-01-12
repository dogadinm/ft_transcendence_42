// Import the WinnerStorage contract artifact
const WinnerStorage = artifacts.require("WinnerStorage");

module.exports = function (deployer) {
  // Deploy the WinnerStorage contract
  deployer.deploy(WinnerStorage, 42);
};
