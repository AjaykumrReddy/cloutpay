<script lang="ts">
	import { onMount } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import { authStore, isLoggedIn } from '$lib/auth';
	import { toast } from '$lib/toast';
	import Toast from '$lib/Toast.svelte';

	let { children } = $props();

	function logout() {
		authStore.clear();
		toast.info('Logged out');
	}

	onMount(() => {
		authStore.init();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app-shell">
	<nav class="nav">
		<a href="/" class="logo">CloutPay</a>
		<div class="nav-links">
			{#if $isLoggedIn}
				<a href="/" class="nav-btn">Home</a>
				<a href="/history" class="nav-btn">History</a>
				<a href="/profile" class="nav-btn">Profile</a>
				<button class="nav-btn" onclick={logout}>Logout</button>
			{:else}
				<a href="/" class="nav-btn">Home</a>
				<a href="/login" class="nav-btn primary">Login</a>
			{/if}
		</div>
	</nav>

	{@render children()}
	<Toast />
</div>

<style>
	.app-shell {
		min-height: 100vh;
	}

	.nav {
		position: fixed;
		top: 0;
		right: 0;
		left: 0;
		z-index: 100;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px 32px;
		background: rgba(8, 8, 8, 0.82);
		backdrop-filter: blur(12px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
		box-sizing: border-box;
	}

	.logo {
		font-size: 1.2rem;
		font-weight: 800;
		text-decoration: none;
		background: linear-gradient(90deg, #ff4d4d, #ffcc00);
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.nav-links {
		display: flex;
		gap: 8px;
	}

	.nav-btn {
		padding: 7px 16px;
		border-radius: 999px;
		border: 1px solid rgba(255, 255, 255, 0.12);
		background: rgba(255, 255, 255, 0.05);
		color: white;
		font-size: 13px;
		cursor: pointer;
		text-decoration: none;
		transition: background 0.2s ease;
	}

	.nav-btn:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.nav-btn.primary {
		background: linear-gradient(90deg, #ff4d4d, #ffcc00);
		color: black;
		font-weight: 700;
		border: none;
	}

	@media (max-width: 600px) {
		.nav {
			padding: 14px 18px;
		}

		.nav-links {
			gap: 6px;
			flex-wrap: wrap;
			justify-content: flex-end;
		}
	}
</style>
