import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a standalone server.js for Docker production deployments.
  output: "standalone",
};

export default nextConfig;
