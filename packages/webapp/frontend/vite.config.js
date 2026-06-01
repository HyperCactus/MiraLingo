import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      "/auth": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("proxyRes", (proxyRes) => {
            const setCookie = proxyRes.headers["set-cookie"];
            if (setCookie) {
              proxyRes.headers["access-control-expose-headers"] =
                (proxyRes.headers["access-control-expose-headers"] || "") +
                ", set-cookie, Set-Cookie";
            }
          });
        },
      },
      "/content": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/lookup": "http://127.0.0.1:8000",
      "/practice": "http://127.0.0.1:8000",
      "/settings": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/tts": "http://127.0.0.1:8000",
    },
  },
});