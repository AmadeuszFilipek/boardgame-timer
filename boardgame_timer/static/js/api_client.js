class ApiClient {

  path_prefix = "https://127.0.0.1:8000"

   async getSession(sessionSlug) {
      let res = await fetch('/api/sessions/' + sessionSlug);
      return await res.json();
    } 

   async createSession(sessionSlug) {
     return await this.post('/api/sessions', {
       session: { slug: sessionSlug }
     });
   }
   
   async addPlayer(sessionSlug, playerName) {
    return await this.post('/api/sessions/' + sessionSlug + '/' + playerName);
   }

   async previousPlayer(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/previous');
   }

   async nextPlayer(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/next');
   }

   async togglePlayer(sessionSlug, playerName) {
    return await this.post('/api/sessions/' + sessionSlug + '/' + playerName + '/toggle');
   }

   async start(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/start');
   }

   async stop(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/stop');
   }

   // helper method performing POST requests with jsonified data
   // returns parsed json response
   async post(url, data = null) {
     let res = await fetch(url, {
       method: 'POST',
       body: JSON.stringify(data),
       headers: {
         'Content-Type': 'application/json'
       }
     });
     return await res.json();
   }
 }

export default ApiClient;
