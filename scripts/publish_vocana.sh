#/bin/sh -e

rm -rf ./dist
pdm build
mkdir -p dist/oocana-sdk-python
mkdir -p dist/oocana-sdk-python/dist
node scripts/make_npm_package.js
cd dist/oocana-sdk-python && npm publish
