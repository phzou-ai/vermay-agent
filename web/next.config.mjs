const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  turbopack: {
    root: process.cwd()
  },
  async redirects() {
    return [
      {
        source: "/",
        destination: "/agent",
        permanent: false
      }
    ]
  }
}

export default nextConfig
