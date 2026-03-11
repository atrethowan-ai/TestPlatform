// This script copies all quiz JSON files from content/quizzes/age6 and age9 to the public directory for loading in the browser.
const fs = require('fs');
const path = require('path');

const srcDirs = [
  path.join(__dirname, '../../content/quizzes/age6'),
  path.join(__dirname, '../../content/quizzes/age9'),
];
const destDir = path.join(__dirname, 'public');

if (!fs.existsSync(destDir)) fs.mkdirSync(destDir);

for (const srcDir of srcDirs) {
  for (const file of fs.readdirSync(srcDir)) {
    if (file.endsWith('.json')) {
      fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
    }
  }
}
console.log('Quiz files copied to public/.');
