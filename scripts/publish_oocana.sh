#/bin/sh -e

DIR=$(cd $(dirname "$0"); pwd)
cd $DIR/..

./scripts/sync_version.js oocana
(cd oocana && pdm build)
mkdir -p oocana/dist/npm_package/dist
node scripts/make_oocana_npm_package.js
cd oocana/dist/npm_package
# npm publish