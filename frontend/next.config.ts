import type { NextConfig } from "next";

// `next dev` and `next build` write to separate folders, so building never breaks a running dev server.
const isDev = process.env.NODE_ENV !== "production";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  distDir: isDev ? ".next-dev" : ".next",
};
export default nextConfig;
