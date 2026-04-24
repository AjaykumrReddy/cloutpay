import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info';

interface Toast {
	id: number;
	message: string;
	type: ToastType;
}

const { subscribe, update } = writable<Toast[]>([]);

let counter = 0;

function add(message: string, type: ToastType = 'info', duration = 3500) {
	const id = ++counter;
	update((t) => [...t, { id, message, type }]);
	setTimeout(() => remove(id), duration);
}

function remove(id: number) {
	update((t) => t.filter((toast) => toast.id !== id));
}

export const toast = {
	subscribe,
	success: (msg: string) => add(msg, 'success'),
	error: (msg: string) => add(msg, 'error', 4500),
	info: (msg: string) => add(msg, 'info'),
};
