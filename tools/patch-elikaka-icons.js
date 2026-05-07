const fs = require("fs");

const targetPath = "baby91.top/elikaka-the-most-beautiful-girl-goddess.html";

const style =
  '<style>/* Ensure breadcrumb/meta icons render when opened via file:// */' +
  '.icon-home:before{content:"\\f015";font-family:"Font Awesome 6 Free";font-weight:900}' +
  '.icon-user:before{content:"\\f007";font-family:"Font Awesome 6 Free";font-weight:900}' +
  '.icon-clock:before{content:"\\f017";font-family:"Font Awesome 6 Free";font-weight:900}' +
  '.icon-folder:before{content:"\\f07b";font-family:"Font Awesome 6 Free";font-weight:900}' +
  '.icon-bubble:before{content:"\\f075";font-family:"Font Awesome 6 Free";font-weight:900}' +
  '.icon-magnifier:before{content:"\\f002";font-family:"Font Awesome 6 Free";font-weight:900}' +
  "</style>";

const needle = '<meta charset="UTF-8">';

const html = fs.readFileSync(targetPath, "utf8");
if (html.includes(style)) process.exit(0);
if (!html.includes(needle)) {
  console.error(`Needle not found: ${needle}`);
  process.exit(2);
}

const out = html.replace(needle, `${needle} ${style}`);
fs.writeFileSync(targetPath, out, "utf8");
