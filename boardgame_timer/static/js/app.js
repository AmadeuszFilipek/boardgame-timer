
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
      console.log(this.appState);
      if (this.appState.version > 0) {
        console.log(this.appState);
        this.startPolling();
      }
    },

    computed: {
    },

    methods:{
      playerBaner(player) {
        // return full player name and time
        var date = new Date(null);
        date.setSeconds(player['time']);
        var result = date.toISOString().substr(11, 8);
        var name = player['name'];
        return `${name} ${result}`;
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
        let newState = await this.api().createSession(this.appState.slug);
        if (newState["status"] !== "error") {
          await this.getSession();
          this.startPolling();
        }
      },
      async getSession() {
        let newState = await this.api().getSession(this.appState.slug);

        this.setState(newState);
        window.history.pushState({}, null, `/sessions/${this.appState.slug}`);
      },
      async addPlayer(playerName) {
        let newState = await this.api().addPlayer(this.appState.slug, playerName);
        
        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async togglePlayer(playerName) {
        let newState = await this.api().togglePlayer(this.appState.slug, playerName);
        
        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async nextPlayer() {
        let newState = await this.api().nextPlayer(this.appState.slug);

        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async previousPlayer() {
        let newState = await this.api().previousPlayer(this.appState.slug);

        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async start() {
        let newState = await this.api().start(this.appState.slug);

        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async stop() {
          let newState = await this.api().stop(this.appState.slug);
  
          if (newState["status"] !== "error") {
            await this.getSession();
          }
      },
      refresh() {
        this.getSession();
        setTimeout(this.refresh, 1000);
      },
      startPolling() {
        if (this.pool !== true) {
          console.log('starting pooling')
          setTimeout(this.refresh(), 1000);
          this.poll = true;
        }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', init);

export default app;