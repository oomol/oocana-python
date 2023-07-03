#/bin/sh -e

mkdir -p dist/vocana-executor-python
cp -r executor/* dist/vocana-executor-python
cd dist/vocana-executor-python && npm publish
rm -rf dist/vocana-executor-python
