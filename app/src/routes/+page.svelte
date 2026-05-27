<script lang="ts">
	import QueryEngine from '$lib/components/navigation/QueryEngine.svelte';
	import ResultList from '$lib/components/analysis/ResultList.svelte';
	import Toast from '$lib/components/navigation/Toast.svelte';
	import { results, addResult } from '$lib/stores/results';
	import { currentMode } from '$lib/stores/app';
	import { showToast } from '$lib/stores/toast';
	import { hybridQuery } from '$lib/api/client';
	
    async function handleQuery(query: string, useSystem2: boolean) {
        console.log('📨 handleQuery called:', { query, useSystem2, mode: $currentMode });
        try {
            const result = await hybridQuery(query, $currentMode, useSystem2); 
            console.log('📦 Received result:', result);
            addResult(result);
            showToast('Query processed successfully!');
        } catch (error) {
            console.error('💥 Query error:', error);
            showToast('Query failed: ' + (error as Error).message, 'error');
        }
    }
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<div class="sticky top-0 z-10 bg-gray-50 pb-6">
		<QueryEngine onQuery={handleQuery} />
	</div>
	<ResultList results={$results} />
</div>

<Toast />