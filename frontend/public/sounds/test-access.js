// This file can be included in any page to test audio accessibility
// It will attempt to load and play both sound files

function testSoundAccess() {
  const paths = [
    './sounds/access-granted-87075.mp3',
    './sounds/access-denied-101308.mp3',
    '/sounds/access-granted-87075.mp3',
    '/sounds/access-denied-101308.mp3'
  ];
  
  const results = document.createElement('div');
  results.style.padding = '10px';
  results.style.margin = '10px';
  results.style.backgroundColor = 'rgba(0,0,0,0.8)';
  results.style.color = '#0ae0ec';
  results.style.fontFamily = 'monospace';
  results.style.position = 'fixed';
  results.style.bottom = '10px';
  results.style.right = '10px';
  results.style.zIndex = '9999';
  results.style.maxWidth = '500px';
  results.style.maxHeight = '300px';
  results.style.overflow = 'auto';
  results.style.borderRadius = '5px';
  
  document.body.appendChild(results);
  
  results.innerHTML = '<h3>Testing Sound Access</h3>';
  
  paths.forEach(path => {
    const entry = document.createElement('div');
    entry.innerHTML = `<p>Testing: ${path} ...</p>`;
    results.appendChild(entry);
    
    fetch(path)
      .then(response => {
        if (response.ok) {
          entry.innerHTML += `<p style="color: #4CAF50">✓ File found (${response.status})</p>`;
          
          // Try to create an audio element
          const audio = new Audio(path);
          
          // Log the audio element properties
          entry.innerHTML += `<p>Audio Element: ${audio.canPlayType('audio/mpeg') ? 'Can play MP3' : 'Cannot play MP3'}</p>`;
          
          // Try to play it
          const playPromise = audio.play();
          
          if (playPromise !== undefined) {
            playPromise
              .then(() => {
                entry.innerHTML += `<p style="color: #4CAF50">✓ Audio playback started</p>`;
                
                // Stop after 1 second
                setTimeout(() => {
                  audio.pause();
                  entry.innerHTML += `<p>Audio playback stopped</p>`;
                }, 1000);
              })
              .catch(error => {
                entry.innerHTML += `<p style="color: #f44336">✗ Audio playback failed: ${error.message}</p>`;
              });
          }
        } else {
          entry.innerHTML += `<p style="color: #f44336">✗ File not found (${response.status})</p>`;
        }
      })
      .catch(error => {
        entry.innerHTML += `<p style="color: #f44336">✗ Error accessing file: ${error.message}</p>`;
      });
  });
}

// Execute immediately if we're in a browser environment
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', testSoundAccess);
}

// Export for module usage
if (typeof module !== 'undefined') {
  module.exports = testSoundAccess;
}

// Test script to create placeholder sound files
const fs = require('fs');
const path = require('path');

// Create empty placeholder sound files if they don't exist
const createPlaceholder = (filename) => {
  const filePath = path.join(__dirname, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`Creating placeholder file: ${filename}`);
    
    // Create a tiny valid MP3 file (not actually playable but valid format)
    const data = Buffer.from('ID3\x03\x00\x00\x00\x00\x00\x02TALB\x00\x00\x00\x0F\x00\x00\x03Placeholder', 'binary');
    
    fs.writeFileSync(filePath, data);
    console.log(`Created ${filename}`);
  } else {
    console.log(`File already exists: ${filename}`);
    
    // Check file size
    const stats = fs.statSync(filePath);
    if (stats.size < 1000) {
      console.log(`File ${filename} is too small (${stats.size} bytes), replacing with placeholder`);
      
      // Create a tiny valid MP3 file (not actually playable but valid format)
      const data = Buffer.from('ID3\x03\x00\x00\x00\x00\x00\x02TALB\x00\x00\x00\x0F\x00\x00\x03Placeholder', 'binary');
      
      fs.writeFileSync(filePath, data);
      console.log(`Replaced ${filename}`);
    }
  }
};

// Create both sound files
createPlaceholder('access-granted-87075.mp3');
createPlaceholder('access-denied-101308.mp3');

console.log('Sound placeholders created successfully.'); 