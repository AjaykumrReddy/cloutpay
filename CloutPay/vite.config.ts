import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');
	const apiTarget = env.PUBLIC_API_BASE;

	return {
		plugins: [sveltekit()],
		server: {
			allowedHosts: true,
			proxy: apiTarget
				? {
						'/api': {
							target: apiTarget,
							changeOrigin: true,
							secure: true,
							rewrite: (path) => path.replace(/^\/api/, ''),
							headers: {
								'ngrok-skip-browser-warning': 'true'
							}
						}
					}
				: undefined
		}
	};
});
