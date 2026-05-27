<script lang="ts">
	import Toast from '$lib/components/navigation/Toast.svelte';
	import { listPatterns, clearPatterns, storePattern } from '$lib/api/client';
	import { currentMode } from '$lib/stores/app';
	import { showToast } from '$lib/stores/toast';
	import { onMount } from 'svelte';
	
	let patterns = $state<any[]>([]);
	let newPatternText = $state('');
	let loading = $state(false);
	let fileInput: HTMLInputElement;
	
	async function loadPatterns() {
		loading = true;
		try {
			const data = await listPatterns();
			patterns = data.patterns;
		} catch (error) {
			showToast('Failed to load patterns', 'error');
		} finally {
			loading = false;
		}
	}
	
	async function handleStorePattern() {
		if (!newPatternText.trim()) return;
		
		try {
			await storePattern(newPatternText, $currentMode);
			showToast('Pattern stored successfully!');
			newPatternText = '';
			loadPatterns();
		} catch (error) {
			showToast('Failed to store pattern', 'error');
		}
	}
	
	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) {
			showToast(`Processing ${file.name}...`, 'info');
			// TODO: Implement file processing
		}
	}
	
	function triggerFileUpload(type: string) {
		fileInput.accept = type === 'pdf' ? '.pdf' : 
		                   type === 'csv' ? '.csv,.xlsx' : 
		                   type === 'doc' ? '.doc,.docx' : '.txt';
		fileInput.click();
	}
	
	async function handleClearPatterns() {
		if (!confirm('Clear all patterns?')) return;
		
		try {
			await clearPatterns();
			showToast('All patterns cleared');
			patterns = [];
		} catch (error) {
			showToast('Failed to clear patterns', 'error');
		}
	}
	
	onMount(() => {
		loadPatterns();
	});
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<!-- File Upload Section -->
	<div class="bg-white rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold mb-4 text-gray-800">Upload & Store from Files</h2>
		<div class="flex gap-2 flex-wrap">
			<button onclick={() => triggerFileUpload('pdf')} class="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition">
				📄 Upload PDF
			</button>
			<button onclick={() => triggerFileUpload('csv')} class="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition">
				📊 Upload CSV/Excel
			</button>
			<button onclick={() => triggerFileUpload('doc')} class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition">
				📝 Upload Doc
			</button>
			<button onclick={() => triggerFileUpload('txt')} class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
				📃 Upload Text
			</button>
		</div>
		<input 
			type="file" 
			bind:this={fileInput}
			onchange={handleFileSelect}
			class="hidden"
		/>
	</div>

	<!-- Manual Pattern Entry -->
	<div class="bg-white rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold mb-4 text-gray-800">Store New Pattern Manually</h2>
		<div class="space-y-4">
			<textarea
				bind:value={newPatternText}
				placeholder="Enter text to store as a pattern..."
				class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
				rows="3"
			></textarea>
			<button
				onclick={handleStorePattern}
				class="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-800 text-white rounded-lg hover:from-purple-700 hover:to-purple-900 transition font-semibold"
			>
				Store Pattern
			</button>
		</div>
	</div>

	<!-- Stored Patterns List -->
	<div class="bg-white rounded-lg shadow-lg p-6">
		<div class="flex justify-between items-center mb-4">
			<h2 class="text-2xl font-bold text-gray-800">Stored Patterns ({patterns.length})</h2>
			<button
				onclick={handleClearPatterns}
				class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
			>
				Clear All
			</button>
		</div>
		
		{#if loading}
			<p class="text-gray-500 text-center py-8">Loading patterns...</p>
		{:else if patterns.length === 0}
			<p class="text-gray-500 text-center py-8">No patterns stored yet</p>
		{:else}
			<div class="space-y-3">
				{#each patterns as pattern, idx (pattern.pattern_id || idx)}
					<div class="border border-gray-200 rounded-lg p-4">
						<p class="text-gray-800 font-medium">{pattern.text}</p>
						<div class="mt-2 text-sm text-gray-500">
							ID: {pattern.pattern_id} | Mode: {pattern.mode}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<Toast />