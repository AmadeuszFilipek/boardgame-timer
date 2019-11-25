class ApiClient {

   async getSession(sessionSlug) {
      let res = await fetch('/api/sessions/' + sessionSlug);
      return await res.json();
    } 

   async createSession(sessionData) {
     return await this.post('/api/sessions', sessionData);
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

   async shuffle(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/shuffle');
   }

   async restart(sessionSlug) {
    return await this.post('/api/sessions/' + sessionSlug + '/restart');
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
