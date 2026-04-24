import { PUBLIC_API_BASE } from '$env/static/public';

export async function createOrder(amount: number) {
	const res = await fetch(`${PUBLIC_API_BASE}/payments/create-order`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
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

export async function verifyPayment(data: Record<string, string>) {
	const res = await fetch(`${PUBLIC_API_BASE}/payments/verify-payment`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!res.ok) throw new Error('Payment verification failed');
	return res.json();
}
