/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

const sw = self as unknown as ServiceWorkerGlobalScope

sw.addEventListener('install', () => sw.skipWaiting())
sw.addEventListener('activate', (e) => e.waitUntil(sw.clients.claim()))
sw.addEventListener('fetch', (e) => e.respondWith(fetch(e.request)))
