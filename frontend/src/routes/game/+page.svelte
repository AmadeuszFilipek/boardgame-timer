<script lang="ts">
	import { goto } from '$app/navigation'
	import { onMount, onDestroy } from 'svelte'
	import type { GameConfig, PlayerState } from '$lib/types.js'
	import { formatTime } from '$lib/format.js'

	let config: GameConfig | null = $state(null)
	let players: PlayerState[] = $state([])
	let activeIndex: number = $state(0)
	let running: boolean = $state(false)
	let finished: boolean = $state(false)

	let intervalId: ReturnType<typeof setInterval> | null = null
	let lastTickTime = 0
	let wakeLock: WakeLockSentinel | null = null
	let audioCtx: AudioContext | null = null
	let warnedMs: Set<number>[] = []
	let lastWarnedSecond = -1

	function getAudioCtx(): AudioContext | null {
		if (!('AudioContext' in window)) return null
		try {
			if (!audioCtx) audioCtx = new AudioContext()
			if (audioCtx.state === 'suspended') audioCtx.resume()
			return audioCtx
		} catch {
			return null
		}
	}

	// Two-note ascending chime: soft sine with quick attack and long decay
	function playGentleBeep() {
		const ctx = getAudioCtx()
		if (!ctx) return
		try {
			const notes = [659, 988] // E5 → B5
			notes.forEach((freq, i) => {
				const osc = ctx.createOscillator()
				const gain = ctx.createGain()
				osc.connect(gain)
				gain.connect(ctx.destination)
				osc.type = 'sine'
				osc.frequency.value = freq
				const t = ctx.currentTime + i * 0.2
				gain.gain.setValueAtTime(0, t)
				gain.gain.linearRampToValueAtTime(0.13, t + 0.015)
				gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6)
				osc.start(t)
				osc.stop(t + 0.6)
			})
		} catch { /* fail silently */ }
	}

	// Urgent tick: pitch rises each second (5→1) for building tension
	function playUrgentTick(second: number) {
		const ctx = getAudioCtx()
		if (!ctx) return
		try {
			// second goes 5→1, freq goes 440→880
			const freq = 440 * Math.pow(2, (5 - second) / 4)
			const t = ctx.currentTime

			// body: sine at full freq
			const osc = ctx.createOscillator()
			const gain = ctx.createGain()
			osc.connect(gain)
			gain.connect(ctx.destination)
			osc.type = 'sine'
			osc.frequency.setValueAtTime(freq * 1.5, t)
			osc.frequency.exponentialRampToValueAtTime(freq, t + 0.04)
			gain.gain.setValueAtTime(0.35, t)
			gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12)
			osc.start(t)
			osc.stop(t + 0.12)

			// click layer: very short square burst for punch
			const click = ctx.createOscillator()
			const clickGain = ctx.createGain()
			click.connect(clickGain)
			clickGain.connect(ctx.destination)
			click.type = 'square'
			click.frequency.value = freq * 2
			clickGain.gain.setValueAtTime(0.06, t)
			clickGain.gain.exponentialRampToValueAtTime(0.001, t + 0.03)
			click.start(t)
			click.stop(t + 0.03)
		} catch { /* fail silently */ }
	}

	function checkWarnings(remainingMs: number, playerIndex: number) {
		for (const t of [30000, 15000, 10000]) {
			if (remainingMs <= t && !warnedMs[playerIndex]?.has(t)) {
				warnedMs[playerIndex]?.add(t)
				playGentleBeep()
			}
		}
		if (remainingMs <= 5000 && remainingMs > 0) {
			const s = Math.ceil(remainingMs / 1000)
			if (s !== lastWarnedSecond) {
				lastWarnedSecond = s
				playUrgentTick(s)
			}
		}
	}
	let holding = $state(false)
	let holdTimeout: ReturnType<typeof setTimeout> | null = null

	function startHold() {
		holding = true
		holdTimeout = setTimeout(() => {
			holding = false
			endGame()
		}, 1500)
	}

	function cancelHold() {
		if (holdTimeout) {
			clearTimeout(holdTimeout)
			holdTimeout = null
		}
		holding = false
	}

	async function acquireWakeLock() {
		if (!('wakeLock' in navigator)) return
		try {
			wakeLock = await navigator.wakeLock.request('screen')
		} catch {
			// denied or unsupported — fail silently
		}
	}

	function releaseWakeLock() {
		wakeLock?.release()
		wakeLock = null
	}

	function handleVisibilityChange() {
		if (document.visibilityState === 'visible' && running) {
			acquireWakeLock()
		}
	}

	onMount(() => {
		document.addEventListener('visibilitychange', handleVisibilityChange)
		const savedConfig = localStorage.getItem('gameConfig')
		const savedState = localStorage.getItem('gameState')
		if (savedConfig && savedState) {
			config = JSON.parse(savedConfig) as GameConfig
			const s = JSON.parse(savedState)
			players = s.players
			activeIndex = s.activeIndex
			finished = s.finished
			warnedMs = s.players.map(() => new Set<number>())
			// always restore paused — time didn't tick while closed
			return
		}
		const raw = sessionStorage.getItem('gameConfig')
		if (!raw) {
			goto('/')
			return
		}
		config = JSON.parse(raw) as GameConfig
		players = initPlayers(config)
		warnedMs = config.players.map(() => new Set<number>())
	})

	$effect(() => {
		if (finished) saveState()
	})

	onDestroy(() => {
		if (intervalId) clearInterval(intervalId)
		releaseWakeLock()
		document.removeEventListener('visibilitychange', handleVisibilityChange)
	})

	function initPlayers(cfg: GameConfig): PlayerState[] {
		return cfg.players.map((name, i) => ({
			name,
			color: cfg.colors?.[i] ?? '#e0e0e0',
			totalMs: cfg.mode === 'countdown' ? cfg.timeLimitMs : 0,
			moveMs: cfg.timeLimitMs,
			boostsLeft: cfg.boostCount ?? 0,
			isEliminated: false
		}))
	}

	function tick() {
		const now = Date.now()
		const elapsed = now - lastTickTime
		lastTickTime = now

		const player = players[activeIndex]

		if (config!.mode === 'countup') {
			player.totalMs += elapsed
		} else if (config!.mode === 'countdown') {
			player.totalMs = Math.max(0, player.totalMs - elapsed)
			checkWarnings(player.totalMs, activeIndex)
			if (player.totalMs === 0) {
				player.isEliminated = true
				const alive = players.filter((p) => !p.isEliminated)
				if (alive.length <= 1) {
					stopTimer()
					finished = true
				} else {
					advanceToNextPlayer()
				}
				return
			}
		} else if (config!.mode === 'per-move') {
			player.moveMs = Math.max(0, player.moveMs - elapsed)
			player.totalMs += elapsed
			checkWarnings(player.moveMs, activeIndex)
			if (player.moveMs === 0) {
				if (player.boostsLeft > 0) {
					player.boostsLeft -= 1
					player.moveMs = (config!.boostSeconds ?? 30) * 1000
					warnedMs[activeIndex] = new Set()
					lastWarnedSecond = -1
					return
				}
				if (config!.autoPass) {
					advanceToNextPlayer()
				} else {
					stopTimer()
				}
				return
			}
		}
	}

	function startTimer() {
		if (running) return
		running = true
		lastTickTime = Date.now()
		intervalId = setInterval(tick, 50)
		acquireWakeLock()
	}

	function saveState() {
		if (!config) return
		localStorage.setItem('gameConfig', JSON.stringify(config))
		localStorage.setItem('gameState', JSON.stringify({ players, activeIndex, finished }))
	}

	function stopTimer() {
		running = false
		if (intervalId) {
			clearInterval(intervalId)
			intervalId = null
		}
		releaseWakeLock()
		saveState()
	}

	function advanceToNextPlayer() {
		stopTimer()
		if (config?.mode === 'countdown' && (config.incrementMs ?? 0) > 0 && !players[activeIndex].isEliminated) {
			players[activeIndex].totalMs += config.incrementMs
		}
		if (config?.mode === 'per-move') {
			players[activeIndex].moveMs = config.timeLimitMs
		}
		let next = (activeIndex + 1) % players.length
		let checked = 0
		while (players[next].isEliminated && checked < players.length) {
			next = (next + 1) % players.length
			checked++
		}
		activeIndex = next
		lastWarnedSecond = -1
		if (config?.mode === 'per-move') {
			warnedMs[next] = new Set()
		}
		startTimer()
	}

	function selectPlayer(i: number) {
		if (finished || players[i].isEliminated) return
		if (i === activeIndex) {
			if (running) stopTimer()
			else startTimer()
		} else {
			stopTimer()
			if (config?.mode === 'per-move') {
				players[activeIndex].moveMs = config!.timeLimitMs
			}
			activeIndex = i
			startTimer()
		}
	}

	function passTurn() {
		if (finished) return
		advanceToNextPlayer()
	}

	function endGame() {
		stopTimer()
		localStorage.removeItem('gameConfig')
		localStorage.removeItem('gameState')
		goto('/')
	}

	function getDisplayTime(player: PlayerState): number {
		if (!config) return 0
		return config.mode === 'per-move' ? player.moveMs : player.totalMs
	}

	function modeLabel(mode: string): string {
		if (mode === 'countdown') return 'Countdown'
		if (mode === 'countup') return 'Count-up'
		return 'Time per Move'
	}
</script>

<main>
	{#if !config}
		<p>Loading...</p>
	{:else}
		<div class="players">
			{#each players as player, i}
				<button
					class="player"
					class:active={i === activeIndex}
					class:eliminated={player.isEliminated}
					class:paused={i === activeIndex && !running}
					style="--c: {player.color}"
					onclick={() => selectPlayer(i)}
					disabled={player.isEliminated}
				>
					<div class="name">{player.name}</div>
					<div class="time">{formatTime(getDisplayTime(player))}</div>
					{#if config.mode === 'per-move' && i === activeIndex}
						<div class="total">Total: {formatTime(player.totalMs)}</div>
					{/if}
					{#if config.mode === 'per-move' && (config.boostCount ?? 0) > 0}
						<div class="boosts">
							{#each Array(config.boostCount) as _, b}
								<span class="boost-dot" class:used={b >= player.boostsLeft}></span>
							{/each}
						</div>
					{/if}
					{#if player.isEliminated}
						<div class="tag tag-out">OUT</div>
					{:else if i === activeIndex}
						<div class="tag tag-turn">{running ? 'YOUR TURN' : 'PAUSED'}</div>
					{/if}
				</button>
			{/each}
		</div>

		<button class="next-btn" onclick={passTurn}>Next →</button>

		<div class="secondary-controls">
			<button
				class="end-btn"
				class:holding
				onpointerdown={startHold}
				onpointerup={cancelHold}
				onpointerleave={cancelHold}
				onpointercancel={cancelHold}
				oncontextmenu={(e) => e.preventDefault()}
			>✕ End Game</button>
		</div>
	{/if}
</main>

<style>
	.players {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin: 1rem 0;
	}

	.player {
		width: 100%;
		border: 2px solid color-mix(in srgb, var(--c) 30%, #e0e0e0);
		border-radius: 12px;
		padding: 0.75rem 1rem;
		text-align: center;
		background: white;
		cursor: pointer;
		transition: border-color 0.2s, background 0.2s, padding 0.2s;
	}

	.player.active {
		background: color-mix(in srgb, var(--c) 10%, white);
		border-color: var(--c);
		border-width: 3px;
		padding: 1.25rem 1rem;
	}

	.player.paused {
		background: color-mix(in srgb, var(--c) 6%, white);
		border-color: color-mix(in srgb, var(--c) 50%, #ccc);
	}

	.player.eliminated {
		opacity: 0.35;
		cursor: default;
	}

	.name {
		font-size: 0.9rem;
		font-weight: 700;
		margin-bottom: 0.2rem;
		color: var(--c);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.player.active .name {
		font-size: 1rem;
	}

	.time {
		font-size: 2rem;
		font-family: monospace;
		font-weight: bold;
		color: var(--c);
		line-height: 1.1;
	}

	.player.active .time {
		font-size: 4.5rem;
	}

	.total {
		font-size: 0.8rem;
		color: color-mix(in srgb, var(--c) 60%, #888);
		margin-top: 0.25rem;
	}

	.boosts {
		display: flex;
		justify-content: center;
		gap: 0.35rem;
		margin-top: 0.5rem;
	}

	.boost-dot {
		width: 0.55rem;
		height: 0.55rem;
		border-radius: 50%;
		background: var(--c);
		transition: opacity 0.2s, background 0.2s;
	}

	.boost-dot.used {
		background: transparent;
		outline: 1.5px solid color-mix(in srgb, var(--c) 40%, transparent);
	}

	.tag {
		display: inline-block;
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		padding: 0.2rem 0.6rem;
		border-radius: 99px;
		margin-top: 0.6rem;
	}

	.tag-turn {
		background: color-mix(in srgb, var(--c) 15%, transparent);
		color: var(--c);
	}

	.tag-out {
		background: #f0f0f0;
		color: #888;
	}

	.next-btn {
		display: block;
		width: 100%;
		padding: 1.1rem;
		font-size: 1.25rem;
		font-weight: 700;
		background: #111;
		color: #fff;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		margin-top: 0.5rem;
		letter-spacing: 0.02em;
	}

	.next-btn:active {
		background: #333;
	}

	.secondary-controls {
		display: flex;
		justify-content: center;
		margin-top: 0.75rem;
	}

	.end-btn {
		position: relative;
		overflow: hidden;
		cursor: pointer;
		user-select: none;
		padding: 0.5rem 1.25rem;
		border: 1.5px solid #ddd;
		border-radius: 8px;
		background: white;
		font-size: 0.875rem;
		color: #888;
	}

	.end-btn::after {
		content: '';
		position: absolute;
		inset: 0;
		background: rgba(200, 0, 0, 0.18);
		transform: scaleX(0);
		transform-origin: left;
	}

	.end-btn.holding::after {
		animation: hold-fill 1.5s linear forwards;
	}

	@keyframes hold-fill {
		to { transform: scaleX(1); }
	}
</style>
