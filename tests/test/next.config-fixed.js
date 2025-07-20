/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['@xenova/transformers'],
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
  // Disable webpack cache to prevent cached errors
  webpack5: true,
  images: {
    domains: ['assets.aceternity.com'],
  },
};

module.exports = nextConfig;
