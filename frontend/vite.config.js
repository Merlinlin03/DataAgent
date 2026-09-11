import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    server: {
        host: '127.0.0.1',
        port: 5173,
        strictPort: true,
        allowedHosts: ['.trycloudflare.com'],
        proxy: {
            "/api": {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
                configure: (proxy) => {
                    proxy.on("proxyReq", (proxyReq) => {
                        proxyReq.setHeader("Cache-Control", "no-cache");
                        proxyReq.setHeader("Connection", "keep-alive");
                    });
                },
            },
        },
    },
});
