export type TimerMode = 'countdown' | 'countup' | 'per-move'

export interface GameConfig {
	mode: TimerMode
	players: string[]
	colors: string[]
	timeLimitMs: number
	incrementMs: number
	boostCount: number
	boostSeconds: number
	autoPass: boolean
}

export interface PlayerState {
	name: string
	color: string
	totalMs: number
	moveMs: number
	boostsLeft: number
	isEliminated: boolean
}
