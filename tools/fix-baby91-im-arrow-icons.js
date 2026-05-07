const fs = require("fs");

const targetPath = "baby91.im/index.html";
const html = fs.readFileSync(targetPath, "utf8");

const replacements = [
  ['<p>?? <a href="android.html"><strong>baby91 Android APK</strong></a></p>', '<p>👉 <a href="android.html"><strong>baby91 Android APK</strong></a></p>'],
  ['<p>?? <a href="hot51.html"><strong>baby91 iOS</strong></a></p>', '<p>👉 <a href="hot51.html"><strong>baby91 iOS</strong></a></p>'],
  ['<p>?? <a href="download.html"><strong>Download baby91 APK Terbaru</strong></a></p>', '<p>👉 <a href="download.html"><strong>Download baby91 APK Terbaru</strong></a></p>'],
  ['<p>?? <a href="tanpa-login.html"><strong>baby91 Tanpa Login</strong></a></p>', '<p>👉 <a href="tanpa-login.html"><strong>baby91 Tanpa Login</strong></a></p>'],
];

let out = html;
let changed = 0;
for (const [from, to] of replacements) {
  if (out.includes(from)) {
    out = out.split(from).join(to);
    changed++;
  }
}

if (out !== html) fs.writeFileSync(targetPath, out, "utf8");
if (changed === 0) process.exitCode = 2;
