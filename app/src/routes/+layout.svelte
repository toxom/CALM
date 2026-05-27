<script lang="ts">
	import '../app.css';
	import Header from '$lib/components/navigation/Header.svelte';
	import Sidebar from '$lib/components/navigation/Sidebar.svelte';
	import Footer from '$lib/components/navigation/Footer.svelte';
	import { currentView } from '$lib/stores/app';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
	
	function handleViewChange(view: 'query' | 'patterns' | 'config' | 'logs') {
		currentView.set(view);
	}
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="min-h-screen flex flex-col">
	<Header />
	<Sidebar selectedView={$currentView} onViewChange={handleViewChange} />
	<main class="flex-1 p-6 bg-gray-50 transition-all duration-300 ml-20">
		{@render children()}
	</main>
	<Footer />
</div>