<script lang="ts">
	import { goto } from '$app/navigation'
	import { onMount } from 'svelte'
	import type { GameConfig, TimerMode } from '$lib/types.js'

	let mode = $state<TimerMode>('countdown')
	let players: string[] = $state(['Player 1', 'Player 2'])
	let minutes: number = $state(10)
	let seconds: number = $state(0)
	let autoPass: boolean = $state(false)
	let hasSavedGame: boolean = $state(false)

	const showTimeInput = $derived(mode === 'countdown' || mode === 'per-move')
	const showAutoPass = $derived(mode === 'per-move')

	onMount(() => {
		hasSavedGame = !!localStorage.getItem('gameState')
	})

	function addPlayer() {
		players = [...players, `Player ${players.length + 1}`]
	}

	function removePlayer(i: number) {
		if (players.length <= 2) return
		players = players.filter((_, idx) => idx !== i)
	}

	function startGame() {
		const validPlayers = players.map((p) => p.trim()).filter((p) => p.length > 0)
		if (validPlayers.length < 2) return

		localStorage.removeItem('gameConfig')
		localStorage.removeItem('gameState')

		const config: GameConfig = {
			mode,
			players: validPlayers,
			timeLimitMs: (minutes * 60 + seconds) * 1000,
			autoPass
		}
		sessionStorage.setItem('gameConfig', JSON.stringify(config))
		goto('/game')
	}

	function resumeGame() {
		goto('/game')
	}
</script>

<main>
	<h1>Boardgame Timer</h1>

	<section>
		<h2>Players</h2>
		{#each players as _, i}
			<div>
				<input type="text" bind:value={players[i]} placeholder="Player {i + 1}" />
				<button onclick={() => removePlayer(i)} disabled={players.length <= 2}>Remove</button>
			</div>
		{/each}
		<button onclick={addPlayer}>+ Add Player</button>
	</section>

	<section>
		<h2>Timer Mode</h2>
		<label>
			<input type="radio" bind:group={mode} value="countdown" />
			Countdown — each player has fixed total time
		</label>
		<br />
		<label>
			<input type="radio" bind:group={mode} value="countup" />
			Count-up — track how long each player takes (no limit)
		</label>
		<br />
		<label>
			<input type="radio" bind:group={mode} value="per-move" />
			Time per move — fixed time reset each turn
		</label>
	</section>

	{#if showTimeInput}
		<section>
			<h2>Time Limit</h2>
			<input type="number" bind:value={minutes} min="0" max="99" style="width:4rem" /> min
			<input type="number" bind:value={seconds} min="0" max="59" style="width:4rem" /> sec
		</section>
	{/if}

	{#if showAutoPass}
		<section>
			<label>
				<input type="checkbox" bind:checked={autoPass} />
				Auto-pass turn when move time runs out
			</label>
		</section>
	{/if}

	{#if hasSavedGame}
		<button onclick={resumeGame}>Resume Game →</button>
	{/if}

	<button onclick={startGame} disabled={players.filter((p) => p.trim()).length < 2}>
		Start New Game →
	</button>
</main>
