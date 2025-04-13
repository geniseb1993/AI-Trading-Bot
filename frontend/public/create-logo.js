const fs = require('fs');
const { createCanvas } = require('canvas');

// Create a canvas instance
const canvas = createCanvas(192, 192);
const ctx = canvas.getContext('2d');

// Fill background with blue
ctx.fillStyle = '#3f51b5';
ctx.fillRect(0, 0, 192, 192);

// Draw text
ctx.font = 'bold 48px Arial';
ctx.fillStyle = 'white';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillText('AI', 96, 70);
ctx.fillText('BOT', 96, 120);

// Save to file
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('./frontend/public/logo192.png', buffer);

console.log('logo192.png has been created successfully!'); 