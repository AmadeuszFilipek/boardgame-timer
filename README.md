# Board Game Timer

> No more stalling the game.

A mobile-first PWA for timing turns in board games. Supports multiple timer modes, per-player color coding, and drag-and-drop player ordering.

## Timer modes

| Mode | How it works |
|---|---|
| **Countdown** | Each player has a fixed time budget for the whole game. Optional move bonus adds seconds after each turn. |
| **Count-up** | Tracks total time spent per player — no limit, just visibility. |
| **Time per Move** | Each player gets a fixed window per turn. Optional time boosts let a player extend a single turn when time runs out. |

## Features

- Player colors — choose from a curated palette, color-coded across setup and game views
- Drag-and-drop player reordering (touch and mouse)
- Audio cues — gentle chime at 30/15/10s remaining, urgent ticks in the final 5 seconds
- Screen wake lock — prevents phone from sleeping mid-game
- Resume on reload — game state persists in localStorage
- PWA — installable on mobile (add to home screen), hides browser chrome

## Tech stack

- [SvelteKit](https://svelte.dev) with Svelte 5 runes mode
- TypeScript
- [SortableJS](https://sortablejs.github.io/Sortable/) for touch drag-and-drop
- pnpm

## Running locally

```sh
cd frontend
pnpm install
pnpm dev
```

The dev server binds to all network interfaces (`--host`), so it's accessible from other devices on the same network at `http://<your-local-ip>:5173`.

## Building for production

```sh
cd frontend
pnpm build
pnpm preview
```

Deploy the `frontend/.svelte-kit` output using the appropriate [SvelteKit adapter](https://svelte.dev/docs/kit/adapters) for your hosting platform. HTTPS is required for the PWA install prompt and wake lock API.

## License

Copyright (c) 2026 Amadeusz Filipek — all rights reserved. See [LICENSE](LICENSE).
