/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

import  remitter from "remitter";
import { Vocana } from "@oomol/oocana";
import path from "node:path"
import { exit, exitCode } from "node:process";
import { fileURLToPath } from "node:url";

const cli = new Vocana();

cli.events.on(remitter.ANY_EVENT, m => console.log(m));
const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  await cli.connect();
  await cli.runFlow({
    flowPath: path.join(__dirname, "flows", "basic.flow"),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
    ].join(","),
  });

  cli.events.on("BlockFinished", (event) => {
    if (event["error"]) {
      console.error("BlockFinished with error", event)
      exitCode(-1)
    }
  })

  setTimeout(() => {
    console.log("wait timeout")
    exit(-1)
  }, 1000 * 25);

  cli.events.on("SessionFinished", () => {
    console.log("SessionFinished")
    exit(0)
  })
}

main();
