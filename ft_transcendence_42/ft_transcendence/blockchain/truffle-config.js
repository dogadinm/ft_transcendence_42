module.exports = {
  networks: {
    development: {
     host: "10.11.10.3",
     port: 7545,
     network_id: "5777",
    },
    dashboard: {
    }
  },
  compilers: {
    solc: {
      version: "0.8.13",
    }
  },
  db: {
    enabled: false,
    host: "127.0.0.1",
  }
};
