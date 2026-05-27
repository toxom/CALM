<script lang="ts">
	import Toast from '$lib/components/navigation/Toast.svelte';
	import { results, clearResults } from '$lib/stores/results';
	
	function handleClearLogs() {
		if (confirm('Clear all logs?')) {
			clearResults();
		}
	}
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<div class="bg-white rounded-lg shadow-lg p-6">
		<div class="flex justify-between items-center mb-4">
			<h2 class="text-2xl font-bold text-gray-800">Results Log ({$results.length})</h2>
			<button
				onclick={handleClearLogs}
				class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
			>
				Clear Log
			</button>
		</div>
		
		{#if $results.length === 0}
			<p class="text-gray-500 text-center py-8">No results logged yet</p>
		{:else}
			<div class="space-y-4">
				{#each $results as result, index (index)}
					<div class="border border-gray-200 rounded-lg p-4">
						<div class="flex items-center gap-2 mb-3">
							{#if result.used_sdm}
								<span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
									System 1
								</span>
							{/if}
							{#if result.used_llm}
								<span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
									System 2
								</span>
							{/if}
							{#if result.processing_time_ms}
								<span class="ml-auto text-sm text-gray-500">
									{result.processing_time_ms.toFixed(2)}ms
								</span>
							{/if}
						</div>
						
						<div class="bg-gray-50 p-3 rounded">
							<p class="text-sm text-gray-800 line-clamp-3">{result.combined_answer || 'No answer'}</p>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<Toast />