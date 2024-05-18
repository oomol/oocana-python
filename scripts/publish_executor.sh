#/bin/sh -e

mkdir -p dist/oocana-executor-python
cp -r executor/* dist/oocana-executor-python
cd dist/oocana-executor-python && npm publish
rm -rf dist/oocana-executor-python
