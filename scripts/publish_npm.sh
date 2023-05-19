#/bin/sh -e

rm -rf ./dist
pdm build
mkdir -p dist/vocana-sdk-python
mkdir -p dist/vocana-sdk-python/dist
node scripts/make_npm_package.js
cd dist/vocana-sdk-python && npm publish
