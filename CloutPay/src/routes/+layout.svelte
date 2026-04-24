<script lang="ts">
	import { onMount } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import { authStore } from '$lib/auth';
	import Toast from '$lib/Toast.svelte';

	let { children } = $props();

	onMount(() => {
		authStore.init();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
<Toast />
