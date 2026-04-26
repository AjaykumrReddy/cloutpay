import { PUBLIC_API_BASE } from '$env/static/public';

const API_BASE = import.meta.env.PUBLIC_API_BASE;

export class AuthError extends Error {
	constructor() {
		super('Session expired. Please log in again.');
		this.name = 'AuthError';
	}
}

function authHeaders(token?: string | null): Record<string, string> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		'ngrok-skip-browser-warning': 'true'
	};
	if (token) headers['Authorization'] = `Bearer ${token}`;
	return headers;
}

async function apiFetch(input: string, init?: RequestInit): Promise<Response> {
	const res = await fetch(input, init);
	if (res.status === 401) throw new AuthError();
	return res;
}

export async function createOrder(amount: number, token?: string | null) {
	const res = await apiFetch(`${API_BASE}/payments/create-order`, {
		method: 'POST',
		headers: authHeaders(token),
		body: JSON.stringify({ amount })
	});
	if (!res.ok) throw new Error('Failed to create order');
	return res.json();
}

export async function getLeaderboard(period?: 'month') {
	const url = period ? `${API_BASE}/leaderboard?period=${period}` : `${API_BASE}/leaderboard`;
	const res = await apiFetch(url);
	if (!res.ok) throw new Error('Failed to fetch leaderboard');
	return res.json();
}

export async function getHistory(token: string, page = 1) {
	const res = await apiFetch(`${API_BASE}/payments/history?page=${page}`, {
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to fetch history');
	return res.json() as Promise<{ items: HistoryPayment[]; has_more: boolean; page: number }>;
}

export interface HistoryPayment {
	id: number;
	amount: number;
	user_name: string;
	payment_reference: string;
	created_at: string;
}

export async function getMySummary(token: string, period?: 'month') {
	const url = period ? `${API_BASE}/leaderboard/me?period=${period}` : `${API_BASE}/leaderboard/me`;
	const res = await apiFetch(url, { headers: authHeaders(token) });
	if (!res.ok) throw new Error('Failed to fetch your stats');
	return res.json();
}

export async function verifyPayment(data: Record<string, string>, token?: string | null) {
	const res = await apiFetch(`${API_BASE}/payments/verify-payment`, {
		method: 'POST',
		headers: authHeaders(token),
		body: JSON.stringify(data)
	});
	if (!res.ok) throw new Error('Payment verification failed');
	return res.json();
}
