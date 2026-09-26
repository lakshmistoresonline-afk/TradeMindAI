const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Minimum valid 1x1 cyan PNG buffer
const cyanPngBase64 = "iVBORw0KGgoAAAANSU5EUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
const pngBuffer = Buffer.from(cyanPngBase64, 'base64');

const publicDir = path.join(__dirname, '../web/public');

fs.writeFileSync(path.join(publicDir, 'pwa-192x192.png'), pngBuffer);
fs.writeFileSync(path.join(publicDir, 'pwa-512x512.png'), pngBuffer);

console.log("✓ PWA icons pwa-192x192.png and pwa-512x512.png generated in web/public/");
