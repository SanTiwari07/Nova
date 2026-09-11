const fs = require('fs');
const path = require('path');

const brainDir = 'C:\\Users\\sansk\\.gemini\\antigravity\\brain\\50048786-bed3-4594-b87b-71594423fae1';
const destDir = 'd:\\Projects\\Nova\\backend\\assets\\fallbacks';

const mappings = {
  'milk_fallback': 'milk.webp',
  'rice_fallback': 'rice.webp',
  'oil_fallback': 'oil.webp',
  'noodles_fallback': 'noodles.webp',
  'hero_banner': 'hero.webp'
};

try {
  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }

  const files = fs.readdirSync(brainDir);
  
  for (const [prefix, destName] of Object.entries(mappings)) {
    const matches = files.filter(f => f.startsWith(prefix) && f.endsWith('.png')).sort();
    if (matches.length > 0) {
      const latest = matches[matches.length - 1];
      const srcPath = path.join(brainDir, latest);
      const destPath = path.join(destDir, destName);
      
      fs.copyFileSync(srcPath, destPath);
      console.log(`Copied ${latest} to ${destName}`);
    }
  }
} catch (e) {
  console.error('Copy script failed (this is non-fatal):', e.message);
}
