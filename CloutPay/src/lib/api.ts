import { PUBLIC_API_BASE } from '$env/static/public';

function authHeaders(token?: string | null): Record<string, string> {
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	if (token) headers['Authorization'] = `Bearer ${token}`;
	return headers;
}

export async function createOrder(amount: number, token?: string | null) {
	const res = await fetch(`${PUBLIC_API_BASE}/payments/create-order`, {
		method: 'POST',
		headers: authHeaders(token),
		body: JSON.stringify({ amount })
	});
	if (!res.ok) throw new Error('Failed to create order');
	return res.json();
}

export async function getLeaderboard() {
	const res = await fetch(`${PUBLIC_API_BASE}/leaderboard`);
	if (!res.ok) throw new Error('Failed to fetch leaderboard');
	return res.json();
}

export async function getHistory(token: string) {
	const res = await fetch(`${PUBLIC_API_BASE}/payments/history`, {
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to fetch history');
	return res.json();
}

export async function verifyPayment(data: Record<string, string>, token?: string | null) {
	const res = await fetch(`${PUBLIC_API_BASE}/payments/verify-payment`, {
		method: 'POST',
		headers: authHeaders(token),
		body: JSON.stringify(data)
	});
	if (!res.ok) throw new Error('Payment verification failed');
	return res.json();
}
