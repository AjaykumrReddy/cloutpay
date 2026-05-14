import { PUBLIC_API_BASE } from '$env/static/public';
import { writable, derived } from 'svelte/store';

// ── Types ─────────────────────────────────────────────────────────────────────
interface AuthState {
	token: string;
	display_name: string | null;
	share_token: string | null;
	city: string | null;
	state: string | null;
}

// ── Store ─────────────────────────────────────────────────────────────────────
function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState | null>(null);

	return {
		subscribe,
		init() {
			const raw = localStorage.getItem('cp_auth');
			if (raw) set(JSON.parse(raw));
		},
		setAuth(token: string, display_name: string | null, share_token: string | null) {
			const state = { token, display_name, share_token, city: null, state: null };
			localStorage.setItem('cp_auth', JSON.stringify(state));
			set(state);
		},
		setDisplayName(display_name: string) {
			update((s) => {
				if (!s) return s;
				const next = { ...s, display_name };
				localStorage.setItem('cp_auth', JSON.stringify(next));
				return next;
			});
		},
		setLocation(city: string | null, state: string | null) {
			update((s) => {
				if (!s) return s;
				const next = { ...s, city, state };
				localStorage.setItem('cp_auth', JSON.stringify(next));
				return next;
			});
		},
		clear() {
			localStorage.removeItem('cp_auth');
			set(null);
		}
	};
}

export const authStore = createAuthStore();
export const isLoggedIn = derived(authStore, ($s) => !!$s?.token);
export const displayName = derived(authStore, ($s) => $s?.display_name ?? null);
export const authToken = derived(authStore, ($s) => $s?.token ?? null);
export const shareToken = derived(authStore, ($s) => $s?.share_token ?? null);

// ── API calls ─────────────────────────────────────────────────────────────────
export async function sendOtp(phone: string): Promise<void> {
	const res = await fetch(`${PUBLIC_API_BASE}/auth/send-otp`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ phone })
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail ?? 'Failed to send OTP');
	}
}

export async function verifyOtp(
	phone: string,
	code: string
): Promise<{ token: string; is_new_user: boolean; display_name: string | null; share_token: string }> {
	const res = await fetch(`${PUBLIC_API_BASE}/auth/verify-otp`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ phone, code })
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail ?? 'Invalid OTP');
	}
	return res.json();
}

export async function updateProfile(
	token: string,
	display_name: string,
	city?: string | null,
	state?: string | null
): Promise<{ display_name: string; city: string | null; state: string | null }> {
	const res = await fetch(`${PUBLIC_API_BASE}/auth/update-profile`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ display_name, city: city || null, state: state || null })
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail ?? 'Failed to update profile');
	}
	return res.json();
}
