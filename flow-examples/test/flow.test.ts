import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { Oocana, isPackageLayerEnable } from "@oomol/oocana";
import type { OocanaEventConfig } from "@oomol/oocana-types";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readdir } from "node:fs/promises";
import type { AnyEventData } from "remitter";
import { homedir } from "node:os";

const __dirname = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
console.log("__dirname", __dirname);
process.env["PATH"] = `${path.join(__dirname, "..", "executor", "bin")}:${process.env["PATH"]}}`;

describe(
  "Flow Tests",
  {
    timeout: 20 * 1000,
  },
  () => {
    let files: Set<string> = new Set();

    beforeAll(async () => {
      files = new Set(await readdir(path.join(__dirname, "flows")));
      console.log("files", files);
    });

    afterAll(() => {
      // expect(files.size).eq(0, `files not tested: ${Array.from(files)}`);
    });

    it("run basic flow", async () => {
      files.delete("basic");
      const { code } = await run("basic");
      expect(code).toBe(0);
    });

    it("run var flow", async () => {
      files.delete("var");
      const { code } = await run("var");
      expect(code).toBe(0);
    });

    it("run bin flow", async () => {
      files.delete("bin");
      const { code, events } = await run("bin");
      expect(code).toBe(0);

      const latestBlockLog = events.findLast(e => e.event === "BlockLog")?.data
        ?.log;
      expect(latestBlockLog).toBe(
        "b'AQIDBA=='"
      );
    });

    it("run service flow", async () => {
      files.delete("service");
      const { code, events } = await run("service");
      expect(code).toBe(0);
    });

    it("run exit flow", async () => {
      files.delete("exit");
      const { code } = await run("exit");
      expect(code).toBe(0);
    });

    it("run global flow", async () => {
      files.delete("global");
      const { code } = await run("global");
      expect(code).toBe(0);
    });

    it("run isinstance flow", async () => {
      files.delete("isinstance");
      const { code } = await run("isinstance");
      expect(code).toBe(0);
    });

    it("run secret flow", async () => {
      files.delete("secret");
      const { code } = await run("secret");
      expect(code).toBe(0);
    });

    it("run path flow", async () => {
      files.delete("path");
      if (await isPackageLayerEnable()) {
        const { code } = await run("path");
        expect(code).toBe(0);
      }
    });
  }
);

async function run(
  flow: string
): Promise<{ code: number; events: AnyEventData<OocanaEventConfig>[] }> {
  console.log(`run flow ${flow}`);
  const label = `run flow ${flow}`;
  console.time(label);

  const cli = new Oocana();
  await cli.connect();

  const events: AnyEventData<OocanaEventConfig>[] = [];
  cli.events.onAny(event => {
    events.push(event);
  });

  const task = await cli.runFlow({
    flowPath: path.join(__dirname, "flows", flow, "flow.oo.yaml"),
    blockSearchPaths: [
      path.join(__dirname, "blocks"),
      path.join(__dirname, "packages"),
    ].join(","),
    extraBindPaths: [`${homedir()}/.oocana:/root/.oocana`],
    sessionId: flow,
    oomolEnvs: {
      VAR: "1",
    },
    envs: {
      VAR: "1",
    },
  });

  cli.events.on("BlockFinished", event => {
    if (event["error"]) {
      console.error("BlockFinished with error", event);
      throw new Error(`BlockFinished with error: ${event}`);
    }
  });

  task.addLogListener("stdout", data => {
    console.log(data);
  });
  task.addLogListener("stderr", data => {
    console.error(data);
  });

  const code = await task.wait();
  console.timeEnd(label);
  cli.dispose();

  return { code, events };
}
