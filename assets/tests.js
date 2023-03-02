/* eslint-env node */

// Create the `client_config` for tests, otherwise test console output is filled with
// `Client config is not yet available for key` messages
window.newsroom = {client_config: {debug: true}};

var testsContext = require.context('.', true, /[Ss]pec.(js|jsx)$/);

testsContext.keys().forEach(testsContext);
