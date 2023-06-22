/* eslint-env node */

// Create the `client_config` for tests, otherwise test console output is filled with
// `Client config is not yet available for key` messages
window.newsroom = {client_config: {debug: true}};

// populate section names with defaults
window.sectionNames = {
    home: 'Home',
    wire: 'Wire',
    agenda: 'Agenda',
    monitoring: 'Monitoring',
    saved: 'Saved / Watched',
};

const testsContext = require.context('.', true, /[Ss]pec.(ts|tsx)$/);

testsContext.keys().forEach(testsContext);
