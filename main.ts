// The World in One Day — the hand-in program for the news-image-20261120
// entry. The artwork itself is entry.png, drawn by build_image.py; this
// program's only job is to deliver those exact bytes to the output folder
// the grader reads, so the judge sees the page precisely as it was drawn.
//
// Where the output folder lives depends on the surroundings: the grader
// sets MAKEFUN_OUTPUT_DIR, and anywhere else the platform default /output
// is used. Run it with:  node main.ts

import { copyFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = join(dirname(fileURLToPath(import.meta.url)), 'entry.png');
const dest = join(outDir, 'entry.png');

copyFileSync(source, dest);

// The competition caps the image at 1 MiB, so verify the delivered copy
// before trusting it: the file must be there and within the cap.
const MAX_BYTES = 1048576; // 1 MiB
let size;
try {
  size = statSync(dest).size;
} catch {
  console.error(`error: entry.png was not delivered to ${dest}`);
  process.exit(1);
}
if (size > MAX_BYTES) {
  console.error(
    `error: ${dest} is ${size} bytes, over the 1 MiB cap of ${MAX_BYTES} bytes`,
  );
  process.exit(1);
}

console.log(`handed in ${dest} (${size} bytes)`);
