
import ApiClient from './api_client.js';

function init() {
  console.log('init');

  let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
      poll: false,
      playerName: null,
      appState: {
        version: 0,
        slug: ''
        }
      },

    // this is for other players, not creator of session
    async mounted() {
      console.log("In mounted method")
      if (this.appState.version > 0) {
        console.log(this.appState)
        this.startPolling();
      }
    },

    computed: {
      playerBaner: function(name) {
        // return full player name and time
        name + this.appState.players[name][time] / 60.

      },
      sortedPlayers: function() {
        // sort players by their ID
      }
    },

    methods:{
      api() {
        return new ApiClient();
      },
      setState(newState) {
        console.log("New state request")
        if (newState.version > this.appState.version) {
          console.log('Setting new state');
          this.appState = newState;
          console.log(this.appState);
        }
      },
      async createSession() {
        console.log("In createSession");
        let newState = await this.api().createSession(this.appState.slug);
        console.log(newState);
        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async getSession() {
        console.log("In getSession");
        let newState = await this.api().getSession(this.appState.slug);
        console.log(newState);

        this.setState(newState);
        window.history.pushState({}, null, `/sessions/${this.appState.slug}`);
        this.startPolling();
      },
      async addPlayer(playerName) {
        let newState = await this.api().addPlayer(this.appState.slug, playerName);
        
        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      refresh() {
        setTimeout(this.refresh, 5000);
        console.log('Refreshing');
      },
      startPolling() {
        if (!this.pool) {
          setTimeout(this.refresh(), 5000);
          this.poll = true
        }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', init);

export default app;