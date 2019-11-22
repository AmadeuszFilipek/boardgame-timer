
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
      poll: false,
      playerName: null,
      appState: {
        version: 0,
        slug: ''
        }
      },

    // this is for other players, not creator of session
    async mounted() {
      if (this.appState.version > 0) {
        this.startPolling();
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
        // return full player name and time
        var date = new Date(null);
        date.setSeconds(player['time']);
        var result = date.toISOString().substr(11, 8);
        var name = player['name'];
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
        let newState = await this.api().createSession(this.getCreateSessionData);
        if (newState["status"] !== "error") {
          await this.getSession();
          this.startPolling();

          window.history.pushState({}, null, `/sessions/${this.appState.slug}`);

        }
      },
      async getSession() {
        let newState = await this.api().getSession(this.appState.slug);

        this.setState(newState);
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
      async shuffle() {
        let newState = await this.api().shuffle(this.appState.slug);

        if (newState["status"] !== "error") {
          await this.getSession();
        }
      },
      async restart() {
        let newState = await this.api().restart(this.appState.slug);

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