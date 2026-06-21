<script lang="ts">
	import { goto } from '$app/navigation'
	import { onMount } from 'svelte'
	import type { GameConfig, TimerMode } from '$lib/types.js'
	import Sortable from 'sortablejs'

	const PALETTE = [
		'#c0474e', // terracotta
		'#3474c0', // blue
		'#2a9e6a', // emerald
		'#8450c0', // violet
		'#c07834', // amber
		'#1e9aaa', // teal
		'#b83480', // raspberry
		'#7a8a1e', // olive
	]

	function nextColor(used: string[]): string {
		return PALETTE.find((c) => !used.includes(c)) ?? PALETTE[used.length % PALETTE.length]
	}

	let mode = $state<TimerMode>('countdown')
	let players: string[] = $state(['Player 1', 'Player 2'])
	let playerColors: string[] = $state([PALETTE[0], PALETTE[1]])
	let playerIds: number[] = $state([0, 1])
	let nextId = 2
	let minutes: number = $state(10)
	let seconds: number = $state(0)
	let incrementSeconds: number = $state(0)
	let boostCount: number = $state(0)
	let boostSeconds: number = $state(30)

	function adjustBoostCount(delta: number) {
		boostCount = Math.max(0, Math.min(50, boostCount + delta))
	}
	let autoPass: boolean = $state(false)
	let hasSavedGame: boolean = $state(false)

	const showTimeInput = $derived(mode === 'countdown' || mode === 'per-move')
	const showAutoPass = $derived(mode === 'per-move')

	const presets = $derived(
		mode === 'per-move'
			? [{ label: '30s', m: 0, s: 30 }, { label: '1m', m: 1, s: 0 }, { label: '2m', m: 2, s: 0 }, { label: '3m', m: 3, s: 0 }, { label: '5m', m: 5, s: 0 }]
			: [{ label: '5m', m: 5, s: 0 }, { label: '10m', m: 10, s: 0 }, { label: '15m', m: 15, s: 0 }, { label: '20m', m: 20, s: 0 }, { label: '30m', m: 30, s: 0 }]
	)

	function applyPreset(p: { m: number; s: number }) {
		minutes = p.m
		seconds = p.s
	}

	function isPreset(p: { m: number; s: number }) {
		return minutes === p.m && seconds === p.s
	}

	function adjustMinutes(delta: number) {
		minutes = Math.max(0, Math.min(99, minutes + delta))
	}

	function adjustSeconds(delta: number) {
		const total = Math.max(0, minutes * 60 + seconds + delta)
		minutes = Math.min(99, Math.floor(total / 60))
		seconds = total % 60
	}

	onMount(() => {
		hasSavedGame = !!localStorage.getItem('gameState')
	})

	function addPlayer() {
		players = [...players, `Player ${players.length + 1}`]
		playerColors = [...playerColors, nextColor(playerColors)]
		playerIds = [...playerIds, nextId++]
	}

	function removePlayer(i: number) {
		if (players.length <= 2) return
		players = players.filter((_, idx) => idx !== i)
		playerColors = playerColors.filter((_, idx) => idx !== i)
		playerIds = playerIds.filter((_, idx) => idx !== i)
	}

	function startGame() {
		const validPlayers = players.map((p) => p.trim()).filter((p) => p.length > 0)
		if (validPlayers.length < 2) return

		localStorage.removeItem('gameConfig')
		localStorage.removeItem('gameState')

		const config: GameConfig = {
			mode,
			players: validPlayers,
			colors: playerColors.slice(0, validPlayers.length),
			timeLimitMs: (minutes * 60 + seconds) * 1000,
			incrementMs: mode === 'countdown' ? incrementSeconds * 1000 : 0,
			boostCount: mode === 'per-move' ? boostCount : 0,
			boostSeconds: mode === 'per-move' ? boostSeconds : 0,
			autoPass
		}
		sessionStorage.setItem('gameConfig', JSON.stringify(config))
		goto('/game')
	}

	function resumeGame() {
		goto('/game')
	}

	function shufflePlayers() {
		const paired = players.map((name, i) => ({ name, color: playerColors[i], id: playerIds[i] }))
		for (let i = paired.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1))
			;[paired[i], paired[j]] = [paired[j], paired[i]]
		}
		players = paired.map((p) => p.name)
		playerColors = paired.map((p) => p.color)
		playerIds = paired.map((p) => p.id)
	}

	let colorPickerIndex: number | null = $state(null)
	let playerListEl: HTMLElement | undefined = $state()

	$effect(() => {
		if (!playerListEl) return
		const sortable = Sortable.create(playerListEl, {
			animation: 150,
			handle: '.drag-handle',
			onEnd: (evt) => {
				const from = evt.oldIndex
				const to = evt.newIndex
				if (from === undefined || to === undefined || from === to) return
				colorPickerIndex = null
				const arr = [...players]
				const colorArr = [...playerColors]
				const idArr = [...playerIds]
				arr.splice(to, 0, arr.splice(from, 1)[0])
				colorArr.splice(to, 0, colorArr.splice(from, 1)[0])
				idArr.splice(to, 0, idArr.splice(from, 1)[0])
				players = arr
				playerColors = colorArr
				playerIds = idArr
			}
		})
		return () => sortable.destroy()
	})
</script>

<main>
	<h1>Boardgame Timer</h1>
	<p class="tagline">No more stalling the game</p>

	<section>
		<h2>Players</h2>
		<div bind:this={playerListEl}>
		{#each players as _, i (playerIds[i])}
			<div class="player-row">
				<span class="drag-handle">⠿</span>
				<button
					class="color-swatch-btn"
					style="background: {playerColors[i]}"
					onclick={() => colorPickerIndex = colorPickerIndex === i ? null : i}
					title="Change color"
				></button>
				<input
					type="text"
					bind:value={players[i]}
					placeholder="Player {i + 1}"
					style="color: {playerColors[i]}; border-color: {playerColors[i]};"
					enterkeyhint={i < players.length - 1 ? 'next' : 'done'}
					onkeydown={(e) => {
						if (e.key !== 'Enter') return
						e.preventDefault()
						const inputs = playerListEl?.querySelectorAll<HTMLInputElement>('input[type="text"]')
						if (!inputs) return
						const next = inputs[i + 1]
						if (next) next.focus()
						else (e.target as HTMLInputElement).blur()
					}}
				/>
				<button class="btn-remove" onclick={() => removePlayer(i)} disabled={players.length <= 2}>✕</button>
				{#if colorPickerIndex === i}
					<div class="color-picker">
						{#each PALETTE as color}
							<button
								class="color-option"
								class:selected={playerColors[i] === color}
								style="background: {color}"
								onclick={() => { playerColors[i] = color; colorPickerIndex = null }}
							></button>
						{/each}
					</div>
				{/if}
			</div>
		{/each}
		</div>
		<div class="player-actions">
			<button class="btn-add" onclick={addPlayer}>+ Add Player</button>
			<button class="btn-shuffle" onclick={shufflePlayers}>⇄ Shuffle</button>
		</div>
	</section>

	<section>
		<h2>Timer Mode</h2>
		<label>
			<input type="radio" bind:group={mode} value="countdown" />
			Countdown — each player has fixed total time
		</label>
		<label>
			<input type="radio" bind:group={mode} value="countup" />
			Count-up — track how long each player takes (no limit)
		</label>
		<label>
			<input type="radio" bind:group={mode} value="per-move" />
			Time per move — fixed time reset each turn
		</label>
	</section>

	{#if showTimeInput}
		<section>
			<h2>Time Limit</h2>
			<div class="time-presets">
				{#each presets as p}
					<button class="preset" class:active={isPreset(p)} onclick={() => applyPreset(p)}>{p.label}</button>
				{/each}
			</div>
			<div class="time-stepper">
				<div class="stepper-unit">
					<button class="stepper-btn" onclick={() => adjustMinutes(-1)}>−</button>
					<input type="number" bind:value={minutes} min="0" max="99" />
					<button class="stepper-btn" onclick={() => adjustMinutes(1)}>+</button>
					<span class="stepper-label">min</span>
				</div>
				<div class="stepper-unit">
					<button class="stepper-btn" onclick={() => adjustSeconds(-15)}>−</button>
					<input type="number" bind:value={seconds} min="0" max="59" />
					<button class="stepper-btn" onclick={() => adjustSeconds(15)}>+</button>
					<span class="stepper-label">sec</span>
				</div>
			</div>
		</section>
	{/if}

	{#if mode === 'countdown'}
		<section>
			<h2>Move Bonus</h2>
			<div class="time-presets">
				<button class="preset" class:active={incrementSeconds === 0} onclick={() => incrementSeconds = 0}>Off</button>
				{#each [5, 10, 15, 30] as s}
					<button class="preset" class:active={incrementSeconds === s} onclick={() => incrementSeconds = s}>{s}s</button>
				{/each}
			</div>
		</section>
	{/if}

	{#if showAutoPass}
		<section>
			<label>
				<input type="checkbox" bind:checked={autoPass} />
				Auto-pass turn when move time runs out
			</label>
		</section>
		<section>
			<h2>Time Boosts per Player</h2>
			<div class="stepper-unit">
				<button class="stepper-btn" onclick={() => adjustBoostCount(-1)}>−</button>
				<input type="number" bind:value={boostCount} min="0" max="50" oninput={(e) => boostCount = Math.min(50, Math.max(0, +(e.currentTarget as HTMLInputElement).value || 0))} />
				<button class="stepper-btn" onclick={() => adjustBoostCount(1)}>+</button>
				<span class="stepper-label">{boostCount === 0 ? 'off' : boostCount === 1 ? 'boost' : 'boosts'}</span>
			</div>
			{#if boostCount > 0}
				<h2 style="margin-top: 0.75rem">Boost Duration</h2>
				<div class="time-presets">
					{#each [15, 30, 45, 60] as s}
						<button class="preset" class:active={boostSeconds === s} onclick={() => boostSeconds = s}>{s}s</button>
					{/each}
				</div>
			{/if}
		</section>
	{/if}

	{#if hasSavedGame}
		<button class="btn-resume" onclick={resumeGame}>Resume Game →</button>
	{/if}

	<button class="btn-primary" onclick={startGame} disabled={players.filter((p) => p.trim()).length < 2}>
		Start New Game →
	</button>
</main>

<style>
	h1 {
		font-size: 1.75rem;
		font-weight: 800;
		margin: 0 0 0.25rem;
		letter-spacing: -0.02em;
	}

	.tagline {
		font-family: Georgia, 'Times New Roman', serif;
		font-style: italic;
		font-size: 0.95rem;
		color: #888;
		margin: 0 0 1.5rem;
	}

	section {
		margin-bottom: 1.5rem;
	}

	h2 {
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: #666;
		margin: 0 0 0.75rem;
	}


	.player-row {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.color-swatch-btn {
		width: 1.1rem;
		height: 1.1rem;
		padding: 0;
		border-radius: 50%;
		border: 2px solid rgba(0, 0, 0, 0.12);
		cursor: pointer;
		flex-shrink: 0;
		transition: transform 0.15s, border-color 0.15s;
	}

	.color-swatch-btn:hover {
		transform: scale(1.2);
		border-color: rgba(0, 0, 0, 0.3);
	}

	.color-picker {
		width: 100%;
		display: flex;
		gap: 0.4rem;
		flex-wrap: wrap;
		padding: 0.4rem 0 0.2rem 1.6rem;
	}

	.color-option {
		width: 1.6rem;
		height: 1.6rem;
		border-radius: 50%;
		border: 2.5px solid transparent;
		cursor: pointer;
		transition: transform 0.12s, border-color 0.12s;
	}

	.color-option:hover {
		transform: scale(1.15);
	}

	.color-option.selected {
		border-color: #000;
	}


	.drag-handle {
		cursor: grab;
		color: #bbb;
		font-size: 1.1rem;
		padding: 0 0.1rem;
		user-select: none;
		flex-shrink: 0;
	}

	.drag-handle:active {
		cursor: grabbing;
	}



	.player-actions {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.25rem;
	}

	.player-actions .btn-add {
		flex: 1;
	}

	.btn-shuffle {
		padding: 0.6rem 0.9rem;
		border: 2px solid #ddd;
		border-radius: 8px;
		background: white;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: border-color 0.15s;
		white-space: nowrap;
	}

	.btn-shuffle:hover {
		border-color: #000;
	}

	input[type='text'],
	input[type='number'] {
		border: 2px solid #ddd;
		border-radius: 8px;
		padding: 0.6rem 0.75rem;
		font-size: 1rem;
		background: white;
		transition: border-color 0.15s;
	}

	input[type='text']:focus,
	input[type='number']:focus {
		outline: none;
		border-color: #000;
	}

	input[type='text'] {
		flex: 1;
		min-width: 0;
	}

	.time-presets {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}

	.preset {
		padding: 0.45rem 0.9rem;
		border: 2px solid #ddd;
		border-radius: 99px;
		background: white;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: border-color 0.15s, background 0.15s, color 0.15s;
	}

	.preset:hover {
		border-color: #888;
	}

	.preset.active {
		border-color: #000;
		background: #000;
		color: #fff;
	}

	.time-stepper {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.stepper-unit {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.stepper-unit input[type='number'] {
		width: 3.5rem;
		text-align: center;
		font-size: 1.25rem;
		font-weight: 700;
		font-family: monospace;
		padding: 0.5rem 0.25rem;
		-moz-appearance: textfield;
	}

	.stepper-unit input[type='number']::-webkit-inner-spin-button,
	.stepper-unit input[type='number']::-webkit-outer-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	.stepper-btn {
		width: 2.25rem;
		height: 2.25rem;
		border: 2px solid #ddd;
		border-radius: 8px;
		background: white;
		font-size: 1.1rem;
		font-weight: 700;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: border-color 0.15s;
		flex-shrink: 0;
	}

	.stepper-btn:hover {
		border-color: #000;
	}

	.stepper-btn:active {
		background: #f0f0f0;
	}

	.stepper-label {
		font-size: 0.8rem;
		font-weight: 600;
		color: #888;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		min-width: 1.5rem;
	}


	label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0;
		cursor: pointer;
		font-size: 0.95rem;
	}

	.btn-remove {
		padding: 0.6rem 0.75rem;
		border: 2px solid #ddd;
		border-radius: 8px;
		background: white;
		color: #888;
		cursor: pointer;
		font-size: 0.9rem;
		transition: border-color 0.15s, color 0.15s;
	}

	.btn-remove:hover:not(:disabled) {
		border-color: #c00;
		color: #c00;
	}

	.btn-remove:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.btn-add {
		width: 100%;
		padding: 0.6rem 0.75rem;
		border: 2px dashed #ccc;
		border-radius: 8px;
		background: transparent;
		color: #555;
		cursor: pointer;
		font-size: 0.9rem;
		transition: border-color 0.15s, color 0.15s;
	}

	.btn-add:hover {
		border-color: #000;
		color: #000;
	}

	.btn-primary {
		display: block;
		width: 100%;
		padding: 1rem;
		font-size: 1.25rem;
		font-weight: 700;
		background: #000;
		color: #fff;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		margin-top: 0.75rem;
	}

	.btn-primary:hover:not(:disabled) {
		background: #222;
	}

	.btn-primary:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.btn-resume {
		display: block;
		width: 100%;
		padding: 1rem;
		font-size: 1.25rem;
		font-weight: 700;
		background: transparent;
		color: #000;
		border: 2px solid #000;
		border-radius: 12px;
		cursor: pointer;
		margin-top: 0.75rem;
	}

	.btn-resume:hover {
		background: #ebebeb;
	}
</style>
