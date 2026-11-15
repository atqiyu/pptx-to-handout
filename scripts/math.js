// Pre-render $...$ and $$...$$ to static KaTeX HTML.
// Usage: node math.js <katex.min.js path> <in.html> <out.html>
const fs = require('fs');
const [, , katexPath, inFile, outFile] = process.argv;
if (!katexPath || !inFile || !outFile) {
  console.error('usage: node math.js <katex.min.js> <in.html> <out.html>');
  process.exit(1);
}
const katex = require(katexPath);

let html = fs.readFileSync(inFile, 'utf8');
const opt = { throwOnError: false, strict: false };

// Display math first so the inline pass cannot eat its delimiters.
html = html.replace(/\$\$([\s\S]+?)\$\$/g, (m, t) =>
  '<div class="math-block">' + katex.renderToString(t.trim(), { ...opt, displayMode: true }) + '</div>');
// [^$] (not [^\n$]) so formulas may wrap across source lines.
html = html.replace(/\$([^$]+?)\$/g, (m, t) => katex.renderToString(t.trim(), opt));

fs.writeFileSync(outFile, html);
console.log('math rendered:', outFile);