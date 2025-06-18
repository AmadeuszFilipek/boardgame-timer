
import ApiClient from './api_client.js';

function init() {
  console.log('init');

  let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
      timers: {0:"CountDownTimer", 1: "CountUpTimer", 2: "TimePerMoveTimer"},
      options: [{ text: 'Auto', value: 'radio1' },
                { text: 'Radio 3', value: 'radio2' }],
      autoPass: false,
      selectedTimer: 0,
      minutes: 1,
      seconds: 0,
      playerName: null,
      errorMessage: "",
      socket: null,
      localActivePlayerTime: 0, // Holds the locally calculated time for the active player
      serverTimeSnapshot: 0,    // Server time for active player at the moment of last sync
      lastSyncBrowserTime: 0,   // Browser's Date.now() at the moment of last sync
      jsTimerIntervalId: null,  // ID of the JavaScript interval for the local timer
      activePlayerData: null,   // Add a small helper to access active player's data easily
      appState: {
        version: 0,
        slug: ''
        }
      },

    // this is for other players, not creator of session
    async mounted() {
      if (this.appState.version > 0) {
        this.connectWebSocket();
        this.startJsTimer();
      }
    },

    computed: {
      getCreateSessionData: function() {
        if (this.timers[this.selectedTimer] === this.timers[0]) {
          var data = {
            "slug": this.appState.slug,
            "autoPass": false,
            "timer": this.timers[this.selectedTimer],
            "seconds": this.minutes * 60};
            return data;
        }  
        if (this.timers[this.selectedTimer] === this.timers[1]) {
          var data = {
            "slug": this.appState.slug,
            "autoPass": false,
            "timer": this.timers[this.selectedTimer],
            "seconds": 0};
            return data;
        }
        if (this.timers[this.selectedTimer] === this.timers[2]) {
          var data = {
            "slug": this.appState.slug,
            "autoPass": this.autoPass,
            "timer": this.timers[this.selectedTimer],
            "seconds": +this.seconds + +this.minutes * 60};
            return data;
        }
        return {};
      },
      isVisibleBar() {
        return this.appState.type !== this.timers[1];
      },
    },

    methods:{
      async dispatchReorder(e) {
        console.log(e);
        const dragged_player = e.moved.element.name
        const new_id = e.moved.newIndex;
        await this.api().movePlayer(this.appState.slug, dragged_player, new_id)
      },
      url() {
        return window.location.href;
      },
      copyLink() {
        let textField =  document.getElementById("session-url");
        textField.select();

        try {
          var successful = document.execCommand('copy');
        } catch (err) {  
        }
  
        window.getSelection().removeAllRanges();

        return successful;
      },
      isColoredBar(player) {
        if ((player.name === this.appState.activePlayer) && this.appState.active) {
          return "danger";
        } else {
          return "dark";
        }
      },
      isActiveBar(player) {
        return (player.name === this.appState.activePlayer) && this.appState.active;
      },
      getPlayerVariant(player) {
        if (player.name === this.appState.activePlayer) {
          return (this.appState.active) ? "outline-danger" : "outline-success";
        } else {
          return "outline-secondary";
        }
      },
      playerBaner(player) {
        let timeToDisplay = player.time;
        // The active player's time is updated by updateLocalTimerDisplay directly in appState.players
        // So, player.time already reflects the JS timer's value for the active player.

        var date = new Date(null);
        date.setSeconds(timeToDisplay);
        var result = date.toISOString().substr(11, 8);
        var name = player.name;
        return `${name} ${result}`;
      },
      onSubmit() {
        console.log('On submit');
      },
      api() {
        return new ApiClient();
      },
      setState(newState) {
        if (newState.version > this.appState.version) {
          this.appState = newState;
        }
      },
      async createSession() {
        if (this.appState.slug === null || this.appState.slug === '') {
          this.errorMessage = "Session name is empty."
          return 0
        }
        let newState = await this.api().createSession(this.getCreateSessionData);
        if (newState["status"] !== "error") {
          this.errorMessage = "";
          await this.getSession(); // Initial fetch to get the full state
          this.connectWebSocket();
          this.startJsTimer();
          window.history.pushState({}, null, `/sessions/${this.appState.slug}`);

        } else {
          this.errorMessage = newState["message"] 
        }
      },
      async getSession() {
        let newState = await this.api().getSession(this.appState.slug);

        this.setState(newState);
      },
      async addPlayer(playerName) {
        if (playerName === null || playerName === '') return 0 
        let newState = await this.api().addPlayer(this.appState.slug, playerName);
        
        if (newState["status"] !== "error") {
          this.errorMessage = "";
          this.playerName = null;
          // await this.getSession(); // WebSocket will update the state
        } else {
          this.errorMessage = newState["message"] 
        }
      },
      async togglePlayer(playerName) {
        let newState = await this.api().togglePlayer(this.appState.slug, playerName);
        
        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      async nextPlayer() {
        let newState = await this.api().nextPlayer(this.appState.slug);

        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      async previousPlayer() {
        let newState = await this.api().previousPlayer(this.appState.slug);

        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      async start() {
        let newState = await this.api().start(this.appState.slug);

        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      async stop() {
          let newState = await this.api().stop(this.appState.slug);
  
          if (newState["status"] !== "error") {
            // await this.getSession(); // WebSocket will update the state
          }
      },
      async shuffle() {
        let newState = await this.api().shuffle(this.appState.slug);

        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      async restart() {
        let newState = await this.api().restart(this.appState.slug);

        if (newState["status"] !== "error") {
          // await this.getSession(); // WebSocket will update the state
        }
      },
      connectWebSocket() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.socket.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/session/${this.appState.slug}/`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log("WebSocket connection established");
        };

        this.socket.onmessage = (event) => {
          console.log("WebSocket message received:", event.data);
          const newState = JSON.parse(event.data);
          this.setState(newState);
          this.startJsTimer(); // Reset and sync JS timer with new server state
        };

        this.socket.onclose = () => {
          console.log("WebSocket connection closed");
          // Optionally, you might want to attempt reconnection here or notify the user.
        };

        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          // Optionally, handle specific errors or notify the user.
        };
      },
      updateLocalTimerDisplay() {
        if (this.appState.active && this.appState.activePlayer && this.activePlayerData) {
          const elapsedSinceSync = (Date.now() - this.lastSyncBrowserTime) / 1000; // in seconds
          let newTime;
          if (this.appState.type === "CountUpTimer") {
            newTime = this.serverTimeSnapshot + elapsedSinceSync;
          } else { // For CountDownTimer and TimePerMoveTimer
            newTime = this.serverTimeSnapshot - elapsedSinceSync;
          }
          this.localActivePlayerTime = Math.max(0, newTime);

          const activeP = this.appState.players.find(p => p.name === this.appState.activePlayer);
          if (activeP) {
            activeP.time = this.localActivePlayerTime;
            if (this.appState.type !== "CountUpTimer" && this.appState.initialSeconds > 0) {
                activeP.ratio = this.localActivePlayerTime / this.appState.initialSeconds;
            } else if (this.appState.type === "CountUpTimer") {
                activeP.ratio = 0; // Or some other logic for count-up ratio
            } else {
                activeP.ratio = 0;
            }
          }
        }
      },
      startJsTimer() {
        clearInterval(this.jsTimerIntervalId);

        if (this.appState.active && this.appState.activePlayer) {
          this.activePlayerData = this.appState.players.find(p => p.name === this.appState.activePlayer);
          if (this.activePlayerData) {
            this.serverTimeSnapshot = this.activePlayerData.time;
            this.lastSyncBrowserTime = Date.now();
            this.localActivePlayerTime = this.activePlayerData.time;

            this.jsTimerIntervalId = setInterval(() => {
              this.updateLocalTimerDisplay();
            }, 100);
          } else {
            this.activePlayerData = null; // Should not happen if appState is consistent
          }
        } else {
          this.activePlayerData = null;
          this.localActivePlayerTime = 0;
        }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', init);

export default app;