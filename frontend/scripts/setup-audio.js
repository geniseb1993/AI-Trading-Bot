const fs = require('fs');
const path = require('path');
const https = require('https');

const SOUND_FILES = [
  {
    name: 'access-granted-87075.mp3',
    url: 'https://assets.mixkit.co/active_storage/sfx/1005/1005-preview.mp3',
    description: 'Access Granted Sound'
  },
  {
    name: 'access-denied-101308.mp3',
    url: 'https://assets.mixkit.co/active_storage/sfx/126/126-preview.mp3',
    description: 'Access Denied Sound'
  }
];

// Path to the public/sounds directory
const soundsDir = path.join(__dirname, '..', 'public', 'sounds');

// Ensure the sounds directory exists
if (!fs.existsSync(soundsDir)) {
  console.log(`Creating sounds directory at ${soundsDir}`);
  fs.mkdirSync(soundsDir, { recursive: true });
}

// Function to download a file
function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    
    https.get(url, (response) => {
      response.pipe(file);
      
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {}); // Delete the file if there was an error
      reject(err);
    });
  });
}

// Download all sound files
async function downloadAllSounds() {
  console.log('Starting download of sound files...');
  
  for (const sound of SOUND_FILES) {
    const destPath = path.join(soundsDir, sound.name);
    
    try {
      console.log(`Downloading ${sound.description} (${sound.name})...`);
      await downloadFile(sound.url, destPath);
      console.log(`Download complete: ${destPath}`);
    } catch (error) {
      console.error(`Error downloading ${sound.name}:`, error);
    }
  }
  
  console.log('All sound files downloaded successfully!');
  console.log('');
  console.log('To test the sounds, open:');
  console.log('http://localhost:3000/sounds/debug.html');
}

// Execute the download
downloadAllSounds().catch(console.error); 