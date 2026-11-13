import type { NextConfig } from "next";

// Backend (starter_v0/server.py) runs locally; the browser only talks to this app.
const API_ORIGIN = process.env.API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // Do not gzip: compression buffers Server-Sent Events and breaks live streaming.
  compress: false,
  experimental: {
    // Agent tool calls can be slow; the dev proxy default would cut them off early.
    proxyTimeout: 5 * 60 * 1000,
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
