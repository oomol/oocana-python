/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

const { oocana } = require("@oomol/oocana");
const path = require("node:path");


const oocana = new oocana();

oocana.events.on(oocana.events.ANY_EVENT, m => console.log(m));

async function main() {
  await oocana.connect();
  await oocana.runFlow({
    flowPath: path.join(__dirname),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
    ].join(","),
  });
}

main();
