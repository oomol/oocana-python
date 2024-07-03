#!/usr/bin/env node

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

const oocanaPath = path.join(__dirname, "..", "oocana");
const buildPath = path.join(oocanaPath, "dist");
const whlFileName = execSync("ls *.whl", { cwd: buildPath }).toString().trim();

const npmDir = path.join(oocanaPath, "dist", "npm_package");
execSync(`cp ${path.join(buildPath, whlFileName)} ${path.join(npmDir, "dist", whlFileName)}`)

const packageMeta = JSON.parse(fs.readFileSync(path.join(oocanaPath, "package.json"), "utf-8"))
packageMeta.version = getVersion();

fs.writeFileSync(path.join(npmDir, "package.json"), JSON.stringify(packageMeta, null, 2));
