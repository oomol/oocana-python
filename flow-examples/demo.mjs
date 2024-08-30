/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

import { Oocana } from "@oomol/oocana";
import path from "node:path"
import { fileURLToPath } from "node:url";
import { readdir } from "node:fs/promises";


const __dirname = path.dirname(fileURLToPath(import.meta.url));
process.env["PATH"] = `${path.join(__dirname, "..", "executor", "bin")}:${process.env["PATH"]}}`;

async function main() {
  const files = await readdir(path.join(__dirname, "flows"));
  for (const file of files) {
    // TODO: executor 在启动后接受到其他 session started 的事件，自己会自动退出，因此无法同时运行多个。executor 应该自己的 session 结束以后，才做这个处理。
    await run(file).catch((e) => {
      console.error(`run flow ${file} failed`, e);
      process.exit(1);
    });
  }
}

async function run(flow) {
  const label = `run flow ${flow}`;
  console.time(label);

  const cli = new Oocana();
  await cli.connect();

  const task = await cli.runFlow({
    flowPath: path.join(__dirname, "flows", flow, "flow.oo.yaml"),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
      path.join(__dirname, "packages")
    ].join(","),
    sessionId: flow,
  });

  cli.events.on("BlockFinished", (event) => {
    if (event["error"]) {
      console.error("BlockFinished with error", event)
      process.exit(1);
    }
  })


  const code = await task.wait();
  if (code !== 0) {
    console.error(`run flow ${flow} failed with code ${code}`);
    process.exit(1);
  }
  console.timeEnd(label);
  cli.dispose();
}

main();
