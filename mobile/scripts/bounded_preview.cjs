// One-file, bounded-memory preview for documented oversized PNG originals.
const sharp = require('sharp');
const path = require('node:path');
const [input, output, maximum='520000000'] = process.argv.slice(2);
if (!input || !output || path.resolve(input) === path.resolve(output)) {
  throw new Error('Usage: bounded_preview.cjs ORIGINAL OUTPUT.png [MAX_PIXELS]; originals cannot be overwritten');
}
const limit = Number(maximum);
if (!Number.isSafeInteger(limit) || limit <= 0 || limit > 520000000) throw new Error('Pixel limit must be within 1..520000000');
sharp.cache({memory:128, files:4, items:20});
sharp.concurrency(1);
sharp(input,{limitInputPixels:limit,sequentialRead:true})
  .resize({width:1200,height:1200,fit:'inside',withoutEnlargement:true})
  .png().toFile(output).then(result=>console.log(JSON.stringify(result)))
  .catch(error=>{console.error(error.message);process.exitCode=1;});
