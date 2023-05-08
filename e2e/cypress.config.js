const {defineConfig} = require('cypress');

module.exports.default = defineConfig({
    e2e: {
        baseUrl: "http://localhost:5050",
        video: false,
        viewportWidth: 1920,
        viewportHeight: 1080,
        retries: {
            runMode: 2,
            openMode: 0,
        }
    }
});
