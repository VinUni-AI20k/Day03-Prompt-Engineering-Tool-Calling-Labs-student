import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: `npm run dev` (port 5173) proxies /api to the FastAPI backend on 8000.
// Prod: `npm run build` -> dist/, served by ui/server.py on the same port as the API.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
