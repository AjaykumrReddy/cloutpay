import type { PageServerLoad } from './$types';
import { env } from '$env/dynamic/private';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const apiBase = env.PUBLIC_API_BASE
	const shareToken = params.name;

	try {
		const res = await fetch(`${apiBase}/share/${shareToken}/stats`, {
			headers: { 'ngrok-skip-browser-warning': 'true' }
		});
		if (!res.ok) return { name: '', rank: null, total: 0, shareToken };
		const data = await res.json();
		return { name: data.display_name, rank: data.rank, total: data.total, shareToken };
	} catch {
		return { name: '', rank: null, total: 0, shareToken };
	}
};
