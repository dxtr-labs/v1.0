/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['@xenova/transformers'],
  },
  images: {
    domains: ['images.unsplash.com', 'assets.aceternity.com'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'assets.aceternity.com',
        pathname: '/demos/**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    // Fixes for @xenova/transformers in browser environment
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
        stream: false,
        util: false,
        buffer: false,
        assert: false,
      };
      
      // Exclude Node.js specific modules from client bundle
      config.externals = config.externals || [];
      config.externals.push({
        'onnxruntime-node': 'onnxruntime-node',
        'sharp': 'sharp',
        'onnxruntime-common': 'onnxruntime-common'
      });
    }
    
    return config;
  },
}

module.exports = nextConfig
