/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

const { Vocana } = require("@vocana/vocana");
const path = require("node:path");


const vocana = new Vocana();

for (const type of eventTypes) {
  vocana.events.on(vocana.events.ANY_EVENT, m => console.log(type, m));
}

async function main() {
  await vocana.connect();
  await vocana.runFlow({
    flowPath: path.join(__dirname),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
    ].join(","),
  });
}

main();
