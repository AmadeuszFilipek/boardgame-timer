const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.svg","manifest.webmanifest","robots.txt","service-worker.js"]),
	mimeTypes: {".svg":"image/svg+xml",".webmanifest":"application/manifest+json",".txt":"text/plain"},
	_: {
		client: {start:"_app/immutable/entry/start.D9xi_8Uq.js",app:"_app/immutable/entry/app.BLTcHlkK.js",imports:["_app/immutable/entry/start.D9xi_8Uq.js","_app/immutable/chunks/DMSZu2JM.js","_app/immutable/chunks/Bd2IXRPL.js","_app/immutable/entry/app.BLTcHlkK.js","_app/immutable/chunks/Bd2IXRPL.js","_app/immutable/chunks/kNaey6uv.js","_app/immutable/chunks/xihTtKlq.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-B3Rl-B68.js')),
			__memo(() => import('./chunks/1-W6RHaZT_.js')),
			__memo(() => import('./chunks/2-KfsetpdQ.js')),
			__memo(() => import('./chunks/3-BZGcAGfd.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/game",
				pattern: /^\/game\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();

const prerendered = new Set([]);

const base = "";

export { base, manifest, prerendered };
//# sourceMappingURL=manifest.js.map
