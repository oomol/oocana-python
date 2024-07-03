#!/usr/bin/env node

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

const package = process.argv[2];
const packageDir = path.join(__dirname, "..", package);

const getVersion = () => {
    return execSync(`pdm run read_version.py ../${package}`, { cwd: __dirname }).toString().trim();
}

const packageMeta = JSON.parse(fs.readFileSync(path.join(packageDir, "package.json"), "utf-8"))
packageMeta.version = getVersion();
fs.writeFileSync(path.join(packageDir, "package.json"), JSON.stringify(packageMeta, null, 2));