const fs = require("fs");
const path = require("path");

/**
 * Revert accidental replacements inside image URLs under:
 *   local_assets/hot51.app/wp-content/uploads/...
 *
 * We only touch *attribute values / URLs* (not visible text) by matching the
 * URL-like substrings inside the HTML. This is a best-effort, lightweight fix
 * to restore image filenames that were renamed in HTML but not on disk.
 */
function fixHtml(html) {
  let out = html;

  // 1) Replace ".../uploads/...baby91...<img-ext>" -> ".../uploads/...hot51...<img-ext>"
  // (covers cases like Ju-Zi-baby91-5.webp)
  out = out.replace(
    /(local_assets\/hot51\.app\/wp-content\/uploads\/[^"' \t\r\n>]*?)-baby91(?=[^"' \t\r\n>]*\.(?:webp|png|jpe?g|gif|svg))/gi,
    "$1-hot51",
  );

  // 2) Replace any remaining "baby91" token inside uploads image filename segments.
  // This is narrower (only within uploads path and only if an image extension appears later).
  out = out.replace(
    /(local_assets\/hot51\.app\/wp-content\/uploads\/[^"' \t\r\n>]*?)baby91(?=[^"' \t\r\n>]*\.(?:webp|png|jpe?g|gif|svg))/gi,
    "$1hot51",
  );

  return out;
}

function main() {
  const dir = process.argv[2];
  if (!dir) {
    console.error("Usage: node tools/fix-image-paths.js <dir-containing-html>");
    process.exit(2);
  }

  for (const file of fs.readdirSync(dir)) {
    if (!file.toLowerCase().endsWith(".html")) continue;
    const p = path.join(dir, file);
    const html = fs.readFileSync(p, "utf8");
    const fixed = fixHtml(html);
    if (fixed !== html) {
      fs.writeFileSync(p, fixed, "utf8");
      process.stdout.write(`fixed-img-path ${file}\n`);
    }
  }
}

main();

