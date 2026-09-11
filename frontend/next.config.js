/** @type {import('next').NextConfig} */
const nextConfig = {
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
  }
}

module.exports = nextConfig
