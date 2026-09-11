import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  const brainDir = 'C:\\Users\\sansk\\.gemini\\antigravity\\brain\\50048786-bed3-4594-b87b-71594423fae1';
  const destDir = 'd:\\Projects\\Nova\\backend\\assets\\fallbacks';
  
  const mappings = {
    'milk_fallback': 'milk.webp',
    'rice_fallback': 'rice.webp',
    'oil_fallback': 'oil.webp',
    'noodles_fallback': 'noodles.webp',
    'hero_banner': 'hero.webp'
  };

  const results = [];

  try {
    const files = fs.readdirSync(brainDir);
    
    for (const [prefix, destName] of Object.entries(mappings)) {
      const matches = files.filter(f => f.startsWith(prefix) && f.endsWith('.png')).sort();
      if (matches.length > 0) {
        const latest = matches[matches.length - 1];
        const srcPath = path.join(brainDir, latest);
        const destPath = path.join(destDir, destName);
        
        fs.copyFileSync(srcPath, destPath);
        results.push(`Copied ${latest} to ${destName}`);
      }
    }
    
    return NextResponse.json({ success: true, results });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message });
  }
}
