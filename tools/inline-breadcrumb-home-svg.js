const fs = require("fs");

const targetPath = "baby91.top/elikaka-the-most-beautiful-girl-goddess.html";

const from =
  '<span itemprop="name"><i class=" icon-home" aria-hidden="true" role="img"></i><span class="breadcrumb-home has-icon">Home</span></span>';

const to =
  '<span itemprop="name"><svg class="breadcrumb-home-icon" aria-hidden="true" viewBox="0 0 24 24" width="14" height="14" style="display:inline-block;vertical-align:-2px;margin-right:6px;fill:currentColor"><path d="M12 3.172 3 10.5v10.5a1 1 0 0 0 1 1h6v-7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7h6a1 1 0 0 0 1-1V10.5l-9-7.328Z"/></svg><span class="breadcrumb-home has-icon">Home</span></span>';

const html = fs.readFileSync(targetPath, "utf8");
if (!html.includes(from)) {
  console.error("Target breadcrumb snippet not found.");
  process.exit(2);
}

const out = html.replace(from, to);
fs.writeFileSync(targetPath, out, "utf8");
