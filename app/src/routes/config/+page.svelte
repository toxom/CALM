<script lang="ts">
	import Toast from '$lib/components/navigation/Toast.svelte';
	import { currentMode } from '$lib/stores/app';
	import { setMode } from '$lib/api/client';
	import { showToast } from '$lib/stores/toast';
	
	async function handleModeChange(mode: 'binary' | 'ternary') {
		try {
			await setMode(mode);
			currentMode.set(mode);
			showToast(`Mode switched to: ${mode.toUpperCase()}`, 'success');
		} catch (error) {
			showToast('Failed to change mode', 'error');
		}
	}
</script>

<div class="max-w-4xl mx-auto space-y-6">
	<div class="bg-white rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold mb-6 text-gray-800">Configuration</h2>
		
		<div class="space-y-6">
			<div>
				<h3 class="text-lg font-semibold mb-3 text-gray-700">SDM Mode</h3>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                    onclick={() => handleModeChange('binary')}
                    class="p-4 border-2 rounded-lg transition {$currentMode === 'binary' ? 'border-purple-600 bg-purple-50' : 'border-gray-200 hover:border-purple-300'}"
                >
                    <div class="text-xl mb-2">🔲</div>
                    <div class="font-semibold">Binary Mode</div>
                    <div class="text-sm text-gray-600 mt-1">0/1 activation</div>
                </button>

                <button
                    onclick={() => handleModeChange('ternary')}
                    class="p-4 border-2 rounded-lg transition {$currentMode === 'ternary' ? 'border-purple-600 bg-purple-50' : 'border-gray-200 hover:border-purple-300'}"
                >
                    <div class="text-xl mb-2">◬</div>
                    <div class="font-semibold">Ternary Mode</div>
                    <div class="text-sm text-gray-600 mt-1">-1/0/1 activation</div>
                </button>
				</div>
			</div>
			
			<div class="border-t pt-6">
				<h3 class="text-lg font-semibold mb-3 text-gray-700">Current Settings</h3>
				<div class="bg-gray-50 p-4 rounded-lg">
					<div class="flex justify-between py-2">
						<span class="text-gray-600">Active Mode:</span>
						<span class="font-semibold text-purple-700">{$currentMode.toUpperCase()}</span>
					</div>
					<div class="flex justify-between py-2">
						<span class="text-gray-600">API Endpoint:</span>
						<span class="font-mono text-sm">http://localhost:8000</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<Toast />