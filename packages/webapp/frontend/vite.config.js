import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

const backendUrl = process.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      "/auth": {
        target: backendUrl,
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
      "/admin": backendUrl,
      "/content": backendUrl,
      "/health": backendUrl,
      "/lookup": backendUrl,
      "/practice": backendUrl,
      "/settings": {
        target: backendUrl,
        changeOrigin: true,
      },
      "/tts": backendUrl,
    },
  },
});