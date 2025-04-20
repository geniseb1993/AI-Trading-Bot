const http = require('http');

// Test both endpoints
async function testEndpoints() {
  console.log('Testing endpoints...');
  
  const endpoints = [
    '/api/dual-bot/generate-signals',
    '/api/generate-signals'
  ];
  
  for (const endpoint of endpoints) {
    console.log(`\nTesting ${endpoint}...`);
    
    const options = {
      hostname: 'localhost',
      port: 5000,
      path: endpoint,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    };
    
    try {
      const response = await new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
          let data = '';
          
          res.on('data', (chunk) => {
            data += chunk;
          });
          
          res.on('end', () => {
            console.log(`Status Code: ${res.statusCode}`);
            if (res.statusCode === 200) {
              try {
                const jsonData = JSON.parse(data);
                console.log('Response:', JSON.stringify(jsonData, null, 2));
                resolve(jsonData);
              } catch (e) {
                console.log('Raw response:', data);
                resolve(data);
              }
            } else {
              console.log('Error response:', data);
              resolve(data);
            }
          });
        });
        
        req.on('error', (e) => {
          console.error(`Request error: ${e.message}`);
          reject(e);
        });
        
        req.end();
      });
    } catch (error) {
      console.error(`Error testing ${endpoint}:`, error);
    }
  }
}

testEndpoints().catch(err => console.error('Test failed:', err)); 