const fs = require("fs");
const path = require("path");

const root = path.join(process.cwd(), "baby91.top");
const arrowSvg =
  '<svg class="scroll-top-icon" aria-hidden="true" viewBox="0 0 24 24" width="16" height="16" style="display:inline-block;vertical-align:-2px;fill:currentColor"><path d="M12 5.5 4.5 13a1 1 0 0 0 1.4 1.4L11 9.3V20a1 1 0 1 0 2 0V9.3l5.1 5.1A1 1 0 0 0 19.5 13L12 5.5Z"/></svg>';

const patterns = [
  '<i class=" fa fa-angle-up" aria-hidden="true" role="img"></i>',
  '<i class="fa fa-angle-up" aria-hidden="true" role="img"></i>',
];

for (const file of fs.readdirSync(root)) {
  if (!file.toLowerCase().endsWith(".html")) continue;
  const p = path.join(root, file);
  const html = fs.readFileSync(p, "utf8");
  let out = html;
  for (const from of patterns) out = out.split(from).join(arrowSvg);
  if (out !== html) fs.writeFileSync(p, out, "utf8");
}
