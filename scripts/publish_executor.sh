#/bin/sh -e

DIR=$(cd $(dirname "$0"); pwd)
cd $DIR/..

./scripts/sync_version.js executor
mkdir -p dist/python-executor
cp -r executor/* dist/python-executor
cd dist/python-executor
npm publish
rm -rf ./dist/python-executor