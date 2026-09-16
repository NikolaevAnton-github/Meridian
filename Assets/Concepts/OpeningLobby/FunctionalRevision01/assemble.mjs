// Compose the local drawing source using explicit UTF-8.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
if(fs.existsSync(path.join(dir,'manifest.json')))throw Error('Frozen candidate');
const files=['drafting.mjs.txt','occlusion.mjs.txt','sheets.mjs.txt','render.mjs.txt'];
fs.writeFileSync(path.join(dir,'generate.mjs'),files.map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n'),'utf8');
