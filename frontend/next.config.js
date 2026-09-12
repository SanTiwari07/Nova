/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**'
      }
    ]
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*' // Proxy to Backend
      },
      {
        source: '/assets/:path*',
        destination: 'http://127.0.0.1:8000/assets/:path*' // Proxy to Backend Assets
      }
    ]
  },
  eslint: {
    ignoreDuringBuilds: true
  }
}

module.exports = nextConfig
