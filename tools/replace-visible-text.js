const fs = require("fs");

/**
 * Replace occurrences in *visible text nodes* (between tags) while keeping tag
 * attributes like href/src intact.
 *
 * Optional: also replaces within title="..." attributes (tooltips).
 */
function replaceVisibleTextInBody(html, { fromRe, to, replaceTitleAttrs }) {
  const bodyOpen = html.search(/<body\b[^>]*>/i);
  if (bodyOpen === -1) return html;
  const bodyTagEnd = html.indexOf(">", bodyOpen);
  if (bodyTagEnd === -1) return html;

  const bodyClose = html.search(/<\/body\s*>/i);
  if (bodyClose === -1) return html;

  const head = html.slice(0, bodyTagEnd + 1);
  const body = html.slice(bodyTagEnd + 1, bodyClose);
  const tail = html.slice(bodyClose);

  const parts = body.split(/(<[^>]*>)/g);
  let inScript = false;
  let inStyle = false;

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (part.startsWith("<")) {
      const lower = part.toLowerCase();
      if (lower.startsWith("<script")) inScript = true;
      else if (lower.startsWith("</script")) inScript = false;
      else if (lower.startsWith("<style")) inStyle = true;
      else if (lower.startsWith("</style")) inStyle = false;

      if (replaceTitleAttrs) {
        // Only touch title="..."; avoid href/src/etc.
        parts[i] = part.replace(
          /(\btitle=")([^"]*)(")/gi,
          (_m, a, b, c) => a + b.replace(fromRe, to) + c,
        );
      }
    } else if (!inScript && !inStyle) {
      parts[i] = part.replace(fromRe, to);
    }
  }

  return head + parts.join("") + tail;
}

function replaceTitleTagText(html, { fromRe, to }) {
  // <title> is visible in the browser tab; keep everything else intact.
  return html.replace(/(<title\b[^>]*>)([\s\S]*?)(<\/title>)/gi, (_m, a, b, c) => {
    return a + String(b).replace(fromRe, to) + c;
  });
}

function main() {
  const args = process.argv.slice(2);
  const targetPath = args[0];
  if (!targetPath) {
    console.error("Usage: node tools/replace-visible-text.js <path-to-html>");
    process.exit(2);
  }

  const html = fs.readFileSync(targetPath, "utf8");
  const out = replaceVisibleTextInBody(replaceTitleTagText(html, {
    fromRe: /hot51/gi,
    to: "baby91",
  }), {
    fromRe: /hot51/gi,
    to: "baby91",
    replaceTitleAttrs: true,
  });

  if (out !== html) {
    fs.writeFileSync(targetPath, out, "utf8");
  }
}

main();
