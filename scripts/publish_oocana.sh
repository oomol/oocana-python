#/bin/sh -e

(cd oocana && pdm build)
mkdir -p oocana/dist/npm_package/dist
node scripts/make_oocana_npm_package.js
cd oocana/dist/npm_package
# npm publish