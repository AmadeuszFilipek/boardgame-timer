import ApiClient from 'api_client.js';

function init() {
  console.log('init');

  let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
      message: 'Hello Vue!',
      people: people,
      appState: {
        version: 0,
        state: {
          id: 'new_session_form',
        }
      },
    },

    async mounted() {
      if (localStorage.playerName) {
        this.playerName = localStorage.playerName;
      }

      let pathParts = window.location.pathname.split('/');
      if (pathParts.length === 3 && pathParts[1] === 'sessions') {
        this.appState.slug = pathParts[2];
        await this.loadState();
        this.startPolling();
      }
    },

    computed: {
      api() {
         return new ApiClient({ pathPrefix: 'http://127.0.0.1:8000/' });
       },
    },

    methods: {
      greet: function(name) {
         console.log('Hello from ' + name + '!')
      },
      setState(newState) {
        if (newState.version > this.appState.version) {
            this.appState = newState;
        }
      },

      startPolling() {
        setInterval(this.loadState.bind(this), 5000);
      },
      },

      async loadState() {
        try {
          let json = await this.api.getTown({
            townSlug: this.appState.slug
          });

          this.setState(json);
        } catch (e) {
          console.error('error =', e);
          window.history.pushState({}, null, '/');
        }
      },

      async createTown() {
        let json = await this.api.createTown({
          townSlug: this.appState.slug,
          playerName: this.playerName
        });
        console.log("json = ", json);

        this.setState(json);
        window.history.pushState({}, null, `/towns/${this.appState.slug}`);
        this.startPolling();
      },

    watch: {
    }
  });
}

document.addEventListener('DOMContentLoaded', init);

export default app;