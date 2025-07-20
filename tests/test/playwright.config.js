// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  timeout: 60000,
  expect: {
    timeout: 15000
  },
  workers: 1,
  reporter: 'list',
  use: {
    actionTimeout: 15000,
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
  },
});
