import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { Oocana, isPackageLayerEnable } from "@oomol/oocana";
import type { OocanaEventConfig } from "@oomol/oocana-types";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readdir } from "node:fs/promises";
import type { AnyEventData } from "remitter";
import { homedir, tmpdir } from "node:os";

const flow_examples = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const packages = path.join(flow_examples, "packages");
const workspace = path.join(flow_examples, "workspace");
process.env["PATH"] = `${path.join(flow_examples, "..", "executor", "bin")}:${process.env["PATH"]}}`;

describe(
  "Flow Tests",
  {
    timeout: 20 * 1000,
  },
  () => {
    let files: Set<string> = new Set();

    beforeAll(async () => {
      files = new Set(await readdir(path.join(workspace, "flows")));
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

    it("run run-block flow", async () => {
      files.delete("run-block");
      const { code } = await run("run-block");
      expect(code).toBe(0);
    });

    it("run run-subflow flow", async () => {
      files.delete("run-subflow");
      const { code } = await run("run-subflow");
      expect(code).toBe(0);
    });

    it("run query-block flow", async () => {
      files.delete("query-block");
      const { code } = await run("query-block");
      expect(code).toBe(0);
    });

    it("run query-downstream flow", async () => {
      files.delete("query-downstream");
      const { code } = await run("query-downstream");
      expect(code).toBe(0);
    });

    it("run var flow", async () => {
      files.delete("var");
      const { code } = await run("var");
      expect(code).toBe(0);
    });

    it("run output flow", async () => {
      files.delete("output");
      const { code, events } = await run("output");
      expect(code).toBe(0);

      const outputEvent = events.find(e => e.event === "BlockOutput")?.data;
      expect(outputEvent).toBeDefined();
      expect(outputEvent?.output, JSON.stringify(outputEvent)).eq("output");

      const outputsEvent = events.find(e => e.event === "BlockOutputs")?.data;
      expect(outputsEvent).toBeDefined();
      expect(outputsEvent?.outputs["a"]).eq("outputs");

      const finishEvent = events.find(e => e.event === "BlockFinished")?.data;
      expect(finishEvent).toBeDefined();
      expect(finishEvent!.result, JSON.stringify(finishEvent)).toBeDefined();
      expect(finishEvent!.result!["a"], JSON.stringify(finishEvent)).eq("finished");
    });

    it("run output-options flow", async () => {
      files.delete("output");
      const { code, events } = await run("output-options");
      expect(code).toBe(0);

      const finishEvents = events.filter(e => e.event === "BlockFinished");
      expect(finishEvents.length).toBe(2);

      const lastFinishEvent = finishEvents.findLast(e => e.event === "BlockFinished")?.data;
      expect(lastFinishEvent).toBeDefined();
      expect(lastFinishEvent?.stacks[0].node_id).toBe("end");
    });

    it("run dataframe flow", async () => {
      files.delete("dataframe");
      if (await isPackageLayerEnable()) {
        const { code, events } = await run("dataframe");
        expect(code).toBe(0); 
      }
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

    it("run matplotlib flow", async () => {
      files.delete("matplotlib");
      if (await isPackageLayerEnable()) {
        const { code, events } = await run("matplotlib");
        expect(code).toBe(0);
        expect(events.find(e => e.event === "BlockPreview")).toBeDefined();
      }
    });

    it("run plotly flow", async () => {
      files.delete("plotly");
      if (await isPackageLayerEnable()) {
        const { code, events } = await run("plotly");
        expect(code).toBe(0);
        expect(events.find(e => e.event === "BlockPreview")).toBeDefined();
      }
    }, {
      timeout: 35 * 1000
    });

    it("run tmp-dir flow", async () => {
      files.delete("tmp-dir");
      const { code } = await run("tmp-dir");
      expect(code).toBe(0);
    });

    it("run pkg-dir flow", async () => {
      files.delete("pkg-dir");
      const { code } = await run("pkg-dir");
      expect(code).toBe(0);
    });

    it("run progress flow", async () => {
      files.delete("progress");
      const { code, events } = await run("progress");
      expect(code).toBe(0);

      const progressEvents = events.filter(e => e.event === "BlockProgress");
      expect(progressEvents.length).greaterThanOrEqual(4);

      const latestFinished = events.findLast(e => e.event === "BlockFinished");
      const lastNode = latestFinished?.data.stacks?.[0].node_id;
      expect(lastNode).toBe("end");

      // Validate the return value: {"count": 3}
      expect(latestFinished?.data.result?.count).toBe(3);
    });

    it("run warning flow", async () => {
      files.delete("warning");
      const { code, events } = await run("warning");
      expect(code).toBe(0);

      const latestBlockWarning = events.findLast(
        e => e.event === "BlockWarning"
      )?.data?.warning;
      expect(latestBlockWarning).toBe(
        "Output handle key: [c] is not defined in Block outputs schema."
      );
    });

    it("run nullable flow", async () => {
      files.delete("nullable");
      const { code, events } = await run("nullable");
      expect(code).toBe(0);

      const latestFinished = events.findLast(e => e.event === "BlockFinished");
      const lastNode = latestFinished?.data.stacks?.[0].node_id;
      expect(lastNode).toBe("end");
    });

    it("run subflow-progress flow", async () => {
      files.delete("subflow-progress");
      const { code, events } = await run("subflow-progress");
      expect(code).toBe(0);

      const progressEvents = events.filter(e => e.event === "BlockProgress");

      expect(
        progressEvents.every(
          e => e.data.progress >= 0 && e.data.progress <= 100
        )
      ).toBe(true);

      expect(progressEvents.length).greaterThanOrEqual(8);

      const latestFinished = events.findLast(e => e.event === "BlockFinished");
      const lastNode = latestFinished?.data.stacks?.[0].node_id;
      expect(lastNode).toBe("end");
    });

    it("run from flow", async () => {
      files.delete("from");
      const { code, events } = await run("from");
      expect(code).toBe(0);

      const latestFinished = events.findLast(e => e.event === "BlockFinished");
      const lastNode = latestFinished?.data.stacks?.[0].node_id;
      expect(lastNode).toBe("end");

      // Validate the computed result: input(2) + output(3) + value1(4) = 9
      expect(latestFinished?.data.result?.output).toBe(9);
    });

    it("run additional-block flow", async () => {
      files.delete("additional-block");
      const { code, events } = await run("additional-block");
      expect(code).toBe(0);

      const latestFinished = events.findLast(e => e.event === "BlockFinished");
      const lastNode = latestFinished?.data.stacks?.[0].node_id;
      expect(lastNode).toBe("end");

      // Validate the dynamic I/O merged result: "hello" + "world" = "helloworld"
      expect(latestFinished?.data.result?.output).toBe("helloworld");
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
    flowPath: path.join(workspace, "flows", flow, "flow.oo.yaml"),
    searchPaths: [packages, path.join(workspace, "blocks")],
    bindPaths: [`src=${homedir()}/.oocana,dst=/root/.oocana`, `src=${tmpdir()},dst=${tmpdir()}`],
    excludePackages: [workspace],
    sessionId: flow,
    tempRoot: tmpdir(),
    debug: true,
    oomolEnvs: {
      VAR: "1",
    },
    envs: {
      VAR: "1",
    },
    projectData: tmpdir(),
    pkgDataRoot: tmpdir(),
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
