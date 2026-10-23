import { defineConfig } from "@playwright/test";

/**
 * The app must be served from the built frontend (`frontend/dist`). Run
 * `frontend` build first; Playwright starts the FastAPI server which serves the
 * SPA and the API on one origin.
 */
export default defineConfig({
  testDir: "./e2e",
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:8011",
    trace: "on-first-retry",
  },
  webServer: {
    command: "python -m uvicorn app.main:app --app-dir backend --port 8011",
    url: "http://127.0.0.1:8011/api/health",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: { DB_PATH: "e2e.db" },
  },
});
