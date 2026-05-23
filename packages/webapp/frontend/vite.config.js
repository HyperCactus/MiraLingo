import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      "/auth": "http://127.0.0.1:8000",
      "/content": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/practice": "http://127.0.0.1:8000",
    },
  },
});
