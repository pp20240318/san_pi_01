const fs = require("fs");
const path = require("path");

const root = path.join(process.cwd(), "baby91.top");

function svg(viewBox, d) {
  return `<svg aria-hidden="true" viewBox="${viewBox}" width="14" height="14" style="display:inline-block;vertical-align:-2px;margin-right:6px;fill:currentColor"><path d="${d}"/></svg>`;
}

const icons = {
  user: svg(
    "0 0 24 24",
    "M12 12a4.2 4.2 0 1 0-4.2-4.2A4.2 4.2 0 0 0 12 12Zm0 2.1c-4.2 0-7.6 2.2-7.6 4.9V21a1 1 0 0 0 1 1h13.2a1 1 0 0 0 1-1v-2c0-2.7-3.4-4.9-7.6-4.9Z",
  ),
  clock: svg(
    "0 0 24 24",
    "M12 2.5A9.5 9.5 0 1 0 21.5 12 9.51 9.51 0 0 0 12 2.5Zm0 17A7.5 7.5 0 1 1 19.5 12 7.51 7.51 0 0 1 12 19.5Zm.75-12.5a1 1 0 0 0-1 1v4.6c0 .27.11.52.3.71l2.7 2.7a1 1 0 1 0 1.41-1.41l-2.41-2.41V8a1 1 0 0 0-1-1Z",
  ),
  folder: svg(
    "0 0 24 24",
    "M10 4.5H4.5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h15a2 2 0 0 0 2-2V8.5a2 2 0 0 0-2-2H12l-1.2-1.6a2 2 0 0 0-1.6-.8Z",
  ),
  bubble: svg(
    "0 0 24 24",
    "M4 4.5h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9.2L5 21.1a1 1 0 0 1-1.6-.8V17.5H4a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2Z",
  ),
};

const replacements = [
  { from: '<i class=" icon-user" aria-hidden="true" role="img"></i>', to: icons.user },
  { from: '<i class=" icon-clock" aria-hidden="true" role="img"></i>', to: icons.clock },
  { from: '<i class=" icon-folder" aria-hidden="true" role="img"></i>', to: icons.folder },
  { from: '<i class=" icon-bubble" aria-hidden="true" role="img"></i>', to: icons.bubble },
];

for (const file of fs.readdirSync(root)) {
  if (!file.toLowerCase().endsWith(".html")) continue;
  const p = path.join(root, file);
  const html = fs.readFileSync(p, "utf8");
  let out = html;
  for (const { from, to } of replacements) out = out.split(from).join(to);
  if (out !== html) fs.writeFileSync(p, out, "utf8");
}
