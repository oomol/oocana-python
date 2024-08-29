/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

import  remitter from "remitter";
import { Vocana } from "@oomol/oocana";
import path from "node:path"
import { fileURLToPath } from "node:url";
import { readdir } from "node:fs/promises";


const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  const files = await readdir(path.join(__dirname, "flows"));
  for (const flow of files) {
    await run(flow);
  }
}

async function run(flow) {
  console.log("run flow", flow);
  const cli = new Vocana();
  cli.events.on(remitter.ANY_EVENT, m => console.log("console every event:", m));

  await cli.connect();
  await cli.runFlow({
    flowPath: path.join(__dirname, "flows", flow, "flow.oo.yaml"),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
      path.join(__dirname, "packages")
    ].join(","),
  });

  const dispose = cli.events.on("BlockFinished", (event) => {
    if (event["error"]) {
      console.error("BlockFinished with error", event)
      process.exit(1);
    }
  })


  return new Promise((resolve, reject) => {
    // TODO: SessionFinished 还有可能是 flow 不合法，需要 @oomol/oocana 提供退出码
    cli.events.once("SessionFinished", () => {
      console.log(flow, "SessionFinished");
      dispose();
      resolve();
    });
    setTimeout(() => {
      reject("timeout");
    }, 1000 * 25);
  });
}

main();
