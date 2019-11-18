class ApiClient {

   async getSession({ sessionSlug }) {
      let res = await fetch(`/api/sessions/${townSlug}`);
      return await res.json();
    }

   async createSession({ sessionSlug }) {
     return await this.post('/api/sessions', {
       session: { slug: sessionSlug }
     });
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
