const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const files = [
  'backtest_results.csv',
  'buy_signals.csv',
  'short_signals.csv'
];

const rootDir = path.resolve(__dirname, '..');
const publicDir = path.resolve(__dirname, 'public');

console.log('Monitoring CSV files for changes...');

// Initial copy of all files
files.forEach(file => {
  const sourceFile = path.join(rootDir, file);
  const targetFile = path.join(publicDir, file);
  
  if (fs.existsSync(sourceFile)) {
    fs.copyFileSync(sourceFile, targetFile);
    console.log(`Copied ${file} to public folder`);
  } else {
    console.log(`Warning: ${file} not found in root directory`);
  }
});

// Watch files for changes
files.forEach(file => {
  const sourceFile = path.join(rootDir, file);
  const targetFile = path.join(publicDir, file);
  
  fs.watchFile(sourceFile, { interval: 1000 }, (curr, prev) => {
    if (curr.mtime !== prev.mtime) {
      console.log(`${file} has changed, updating...`);
      fs.copyFileSync(sourceFile, targetFile);
      console.log(`Updated ${file} in public folder`);
    }
  });
});

console.log('Monitoring active. Press Ctrl+C to stop.');

// Keep the process running
process.stdin.resume(); 