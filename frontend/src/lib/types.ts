export type TimerMode = 'countdown' | 'countup' | 'per-move'

export interface GameConfig {
	mode: TimerMode
	players: string[]
	timeLimitMs: number
	autoPass: boolean
}

export interface PlayerState {
	name: string
	totalMs: number
	moveMs: number
	isEliminated: boolean
}
