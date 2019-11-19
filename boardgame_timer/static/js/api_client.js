class ApiClient {

  path_prefix = "https://127.0.0.1:8000"

   async getSession({ sessionSlug }) {
      let res = await fetch(`/api/sessions/${sessionSlug}`);
      return await res.json();
    } 

   async createSession(sessionSlug) {
    console.log(sessionSlug)
     return await this.post('/api/sessions', {
       session: { slug: sessionSlug }
     });
   }
 
   // helper method performing POST requests with jsonified data
   // returns parsed json response
   async post(url, data = null) {
     console.log(url)
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
