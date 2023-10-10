/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-env node */

const { Vocana } = require("@vocana/vocana");
const path = require("node:path");

const vocana = new Vocana();

const eventTypes = [
  "SessionStarted",
  "SessionFinished",
  "FlowStarted",
  "FlowFinished",
  "FlowError",
  "FlowLog",
  "BlockStarted",
  "BlockFinished",
  "BlockProps",
  "BlockResult",
  "BlockError",
  "BlockLog",
  "VocanaError",
  "VocanaLog",
];
for (const type of eventTypes) {
  vocana.events.on(type, m => console.log(type, m));
}

vocana.runFlow({
  flowPath: path.join(__dirname),
  blockSearchPaths: [
    path.join(__dirname, "blocks"),
    path.join(__dirname, "packages"),
  ].join(","),
});
