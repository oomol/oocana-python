const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

const getVersion = () => {
    return execSync("pdm run read_version.py", { cwd: __dirname }).toString().trim();
}

const distPath = path.join(__dirname, "..", "dist");
const pkgDirPath = path.join(__dirname, "..", "dist", "vocana-sdk-python");
const packageJOSNPath = path.join(pkgDirPath, "package.json");
const whlFileName = execSync("ls *.whl", { cwd: distPath }).toString().trim();

execSync(`cp ${path.join(distPath, whlFileName)} ${path.join(pkgDirPath, "dist", whlFileName)}`)
const packageJOSN = fs.readFileSync(path.join(__dirname, "package.json"), "utf-8");
const packageJOSNObj = JSON.parse(packageJOSN);
packageJOSNObj.main = `dist/${whlFileName}`;
packageJOSNObj.version = getVersion();
fs.writeFileSync(packageJOSNPath, JSON.stringify(packageJOSNObj, null, 2));
