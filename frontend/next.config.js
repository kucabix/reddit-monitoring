/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use static export only when explicitly enabled (for deployment)
  ...(process.env.NEXT_EXPORT === "true" && { output: "export" }),
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
