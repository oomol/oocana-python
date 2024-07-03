#/bin/sh -e

cp -r executor/* dist/python-executor
cd dist/python-executor && npm publish
rm -rf ./dist/python-executor
