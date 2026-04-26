<script lang="ts">
	import { onMount } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import { authStore, isLoggedIn } from '$lib/auth';
	import { toast } from '$lib/toast';
	import Toast from '$lib/Toast.svelte';
	import { goto } from '$app/navigation';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

	function logout() {
		authStore.clear();
		mobileMenuOpen = false;
		toast.info('Logged out');
		// once logout redirect to home
		goto('/');
	}

	function closeMenu() {
		mobileMenuOpen = false;
	}

	function toggleMenu() {
		mobileMenuOpen = !mobileMenuOpen;
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
		<a href="/" class="logo" onclick={closeMenu}>CloutPay</a>

		<div class="nav-links desktop-links">
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

		<button
			class="menu-toggle"
			type="button"
			aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
			aria-expanded={mobileMenuOpen}
			onclick={toggleMenu}
		>
			<span class:open={mobileMenuOpen}></span>
			<span class:open={mobileMenuOpen}></span>
			<span class:open={mobileMenuOpen}></span>
		</button>

		{#if mobileMenuOpen}
			<div class="mobile-menu">
				<div class="mobile-menu-glow"></div>
				{#if $isLoggedIn}
					<a href="/" class="mobile-link" onclick={closeMenu}>
						<span class="mobile-label">Home</span>
						<span class="mobile-meta">Back to the board</span>
					</a>
					<a href="/history" class="mobile-link" onclick={closeMenu}>
						<span class="mobile-label">History</span>
						<span class="mobile-meta">Your contributions</span>
					</a>
					<a href="/profile" class="mobile-link" onclick={closeMenu}>
						<span class="mobile-label">Profile</span>
						<span class="mobile-meta">Edit your display name</span>
					</a>
					<button class="mobile-link danger" type="button" onclick={logout}>
						<span class="mobile-label">Logout</span>
						<span class="mobile-meta">End this session</span>
					</button>
				{:else}
					<a href="/" class="mobile-link" onclick={closeMenu}>
						<span class="mobile-label">Home</span>
						<span class="mobile-meta">Explore the live board</span>
					</a>
					<a href="/login" class="mobile-link primary-link" onclick={closeMenu}>
						<span class="mobile-label">Login</span>
						<span class="mobile-meta">Track your rank and profile</span>
					</a>
				{/if}
			</div>
		{/if}
	</nav>

	{@render children()}
	<Toast />
</div>

<style>
	:global(html, body) {
		max-width: 100%;
		overflow-x: hidden;
	}

	.app-shell {
		min-height: 100vh;
		overflow-x: clip;
	}

	.nav {
		position: fixed;
		top: 18px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 100;
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: min(1120px, calc(100vw - 32px));
		padding: 12px 18px 12px 22px;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.03)),
			rgba(9, 9, 9, 0.66);
		backdrop-filter: blur(18px) saturate(145%);
		-webkit-backdrop-filter: blur(18px) saturate(145%);
		border: 1px solid rgba(255, 255, 255, 0.08);
		box-shadow:
			0 14px 40px rgba(0, 0, 0, 0.28),
			inset 0 1px 0 rgba(255, 255, 255, 0.08);
		border-radius: 24px;
		box-sizing: border-box;
	}

	.logo {
		font-size: 1.28rem;
		font-weight: 900;
		letter-spacing: -0.03em;
		text-decoration: none;
		background: linear-gradient(90deg, #ff4d4d, #ffcc00);
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		text-shadow: 0 0 24px rgba(255, 153, 51, 0.18);
	}

	.nav-links {
		display: flex;
		gap: 10px;
		align-items: center;
	}

	.nav-btn {
		padding: 9px 16px;
		border-radius: 999px;
		border: 1px solid rgba(255, 255, 255, 0.08);
		background: rgba(255, 255, 255, 0.04);
		color: rgba(255, 255, 255, 0.88);
		font-size: 13px;
		font-weight: 600;
		letter-spacing: 0.01em;
		cursor: pointer;
		text-decoration: none;
		transition:
			background 0.22s ease,
			border-color 0.22s ease,
			transform 0.18s ease,
			box-shadow 0.22s ease,
			color 0.22s ease;
	}

	.nav-btn:hover {
		background: rgba(255, 255, 255, 0.08);
		border-color: rgba(255, 255, 255, 0.14);
		color: white;
		transform: translateY(-1px);
		box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
	}

	.nav-btn.primary {
		background: linear-gradient(90deg, #ff4d4d, #ffcc00);
		color: black;
		font-weight: 800;
		border: none;
		box-shadow: 0 10px 24px rgba(255, 153, 51, 0.22);
	}

	.nav-btn.primary:hover {
		background: linear-gradient(90deg, #ff5a5a, #ffd84d);
		color: black;
	}

	.menu-toggle {
		display: none;
		width: 44px;
		height: 44px;
		border-radius: 14px;
		border: 1px solid rgba(255, 255, 255, 0.08);
		background: rgba(255, 255, 255, 0.05);
		padding: 0;
		cursor: pointer;
		align-items: center;
		justify-content: center;
		flex-direction: column;
		gap: 5px;
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
	}

	.menu-toggle span {
		display: block;
		width: 18px;
		height: 2px;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.9);
		transition: transform 0.22s ease, opacity 0.22s ease;
	}

	.menu-toggle span.open:nth-child(1) {
		transform: translateY(7px) rotate(45deg);
	}

	.menu-toggle span.open:nth-child(2) {
		opacity: 0;
	}

	.menu-toggle span.open:nth-child(3) {
		transform: translateY(-7px) rotate(-45deg);
	}

	.mobile-menu {
		display: none;
	}

	@media (max-width: 900px) {
		.nav {
			top: 14px;
			width: min(1120px, calc(100vw - 20px));
			padding: 10px 12px 10px 16px;
			border-radius: 20px;
		}
	}

	@media (max-width: 820px) {
		.nav {
			top: 10px;
			width: calc(100vw - 16px);
			padding: 10px 12px;
			border-radius: 18px;
		}

		.desktop-links {
			display: none;
		}

		.menu-toggle {
			display: inline-flex;
		}

		.mobile-menu {
			position: absolute;
			top: calc(100% + 12px);
			right: 0;
			display: flex;
			flex-direction: column;
			gap: 8px;
			width: min(300px, 100%);
			padding: 14px;
			border-radius: 22px;
			background:
				linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03)),
				rgba(10, 10, 10, 0.9);
			border: 1px solid rgba(255, 255, 255, 0.08);
			box-shadow:
				0 18px 44px rgba(0, 0, 0, 0.34),
				inset 0 1px 0 rgba(255, 255, 255, 0.08);
			overflow: hidden;
		}

		.mobile-menu-glow {
			position: absolute;
			top: -40px;
			right: -10px;
			width: 120px;
			height: 120px;
			border-radius: 999px;
			background: radial-gradient(circle, rgba(255, 204, 0, 0.2), transparent 70%);
			filter: blur(16px);
			pointer-events: none;
		}

		.mobile-link {
			position: relative;
			z-index: 1;
			display: flex;
			flex-direction: column;
			gap: 3px;
			padding: 14px 16px;
			border-radius: 16px;
			border: 1px solid rgba(255, 255, 255, 0.06);
			background: rgba(255, 255, 255, 0.04);
			color: white;
			text-decoration: none;
			text-align: left;
			cursor: pointer;
		}

		.mobile-link.primary-link {
			background: linear-gradient(90deg, rgba(255, 77, 77, 0.92), rgba(255, 204, 0, 0.92));
			color: black;
			border: none;
		}

		.mobile-link.danger {
			background: rgba(255, 255, 255, 0.03);
		}

		.mobile-label {
			font-size: 14px;
			font-weight: 700;
			letter-spacing: 0.01em;
		}

		.mobile-meta {
			font-size: 12px;
			color: rgba(255, 255, 255, 0.58);
		}

		.primary-link .mobile-meta {
			color: rgba(0, 0, 0, 0.72);
		}

		.logo {
			font-size: 1.12rem;
		}
	}

	@media (max-width: 600px) {
		.mobile-menu {
			width: min(280px, 100%);
		}

		.mobile-link {
			padding: 13px 14px;
		}
	}
</style>
