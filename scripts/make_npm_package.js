const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

const getVersion = () => {
    return execSync("pdm run read_version.py", { cwd: __dirname }).toString().trim();
}

const distPath = path.join(__dirname, "..", "dist");
const pkgDirPath = path.join(__dirname, "..", "dist", "oocana-sdk-python");
const packageJSONPath = path.join(pkgDirPath, "package.json");
const whlFileName = execSync("ls *.whl", { cwd: distPath }).toString().trim();

execSync(`cp ${path.join(distPath, whlFileName)} ${path.join(pkgDirPath, "dist", whlFileName)}`)
const packageJSON = fs.readFileSync(path.join(__dirname, "package.json"), "utf-8");
const packageJSONObj = JSON.parse(packageJSON);
packageJSONObj.main = `dist/${whlFileName}`;
packageJSONObj.version = getVersion();
fs.writeFileSync(packageJSONPath, JSON.stringify(packageJSONObj, null, 2));
