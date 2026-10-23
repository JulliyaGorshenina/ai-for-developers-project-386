import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "../spec/openapi/openapi.json",
  output: "src/api/generated",
  client: "@hey-api/client-fetch",
});
