// frontend/vite.config.ts

import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      host: "0.0.0.0",
      port: Number(env.VITE_DEV_PORT || 5173),
      strictPort: true,

      proxy: {
        "/api": {
          target: env.VITE_DEV_API_PROXY || "${BACKEND_API_URL}",
          changeOrigin: true,
          secure: false,
        },
      },
    },

    preview: {
      host: "0.0.0.0",
      port: 4173,
    },
  };
});
