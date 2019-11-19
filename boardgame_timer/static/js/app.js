
import ApiClient from './api_client.js';

function init() {
  console.log('init');

  let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
      appState: {
        version: 0,
        state: {
          id: 'new_session_form',
          slug: '',
        }
      },
    },
    methods:{
      api() {
        return new ApiClient();
      },
      async greet() {
        window.alert("hellow");
      },
      async createSession() {
        console.log("In createSession");
        let result = await this.api().createSession(this.appState.state.slug);
        console.log(result);
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', init);

export default app;