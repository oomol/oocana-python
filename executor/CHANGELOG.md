# Changelog

## [0.11.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.0...@oomol/python-executor@0.11.1) (2024-08-16)


### Features

* delay exit after new session start for rerun cache ([#142](https://github.com/oomol/oocana-python/issues/142)) ([6073583](https://github.com/oomol/oocana-python/commit/6073583c554d2f3380125178362ea51a0ee73a25))

## [0.11.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.7...@oomol/python-executor@0.11.0) (2024-08-13)


### ⚠ BREAKING CHANGES

* session level executor ([#140](https://github.com/oomol/oocana-python/issues/140))

### Features

* session level executor ([#140](https://github.com/oomol/oocana-python/issues/140)) ([ca77bec](https://github.com/oomol/oocana-python/commit/ca77becb427d22d516a8fca6f8a1c413953d201c))

## [0.10.7](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.6...@oomol/python-executor@0.10.7) (2024-08-05)


### Bug Fixes

* use delay delete for workaround ([#132](https://github.com/oomol/oocana-python/issues/132)) ([54687f8](https://github.com/oomol/oocana-python/commit/54687f8527d0f1c71e14ab29fcfb0cd41b42c83d))

## [0.10.6](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.5...@oomol/python-executor@0.10.6) (2024-08-05)


### Bug Fixes

* missing drop message path ([2c14cc2](https://github.com/oomol/oocana-python/commit/2c14cc27ad8d78a318414a01dd700689f466114e))
* wrong EXECUTOR NAME ([#131](https://github.com/oomol/oocana-python/issues/131)) ([fc93311](https://github.com/oomol/oocana-python/commit/fc93311d7697047728981caa25c25abfceb2e191))

## [0.10.5](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.4...@oomol/python-executor@0.10.5) (2024-08-02)


### Features

* move tmp files to &lt;session_id&gt; and only delete this directory ([#115](https://github.com/oomol/oocana-python/issues/115)) ([49e2769](https://github.com/oomol/oocana-python/commit/49e276918b16a1fec490fb3283ca29bd8f81eafb))

## [0.10.4](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.3...@oomol/python-executor@0.10.4) (2024-07-29)


### Features

* delete temp source after session end ([75bf533](https://github.com/oomol/oocana-python/commit/75bf5332cb5e70846327a338848af24f2da22b2d))


### Bug Fixes

* remove .scriptlets directory ([e18b20c](https://github.com/oomol/oocana-python/commit/e18b20c5e48c487eba73b48abb0b0967cf62f7bc))

## [0.10.3](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.2...@oomol/python-executor@0.10.3) (2024-07-29)


### Bug Fixes

* add message type for reporter ([47d8fb3](https://github.com/oomol/oocana-python/commit/47d8fb3926e017324109cc51ffe64479140191ac))

## [0.10.2](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.1...@oomol/python-executor@0.10.2) (2024-07-29)


### Bug Fixes

* call done message after other message done ([1a89141](https://github.com/oomol/oocana-python/commit/1a89141d2288e5c1c8ed882fca60fb840424b1fb))

## [0.10.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.10.0...@oomol/python-executor@0.10.1) (2024-07-23)


### Bug Fixes

* function should be in options field ([dd6787e](https://github.com/oomol/oocana-python/commit/dd6787ea0213a8cd20b8b4fc61963f706c7e39c6))

## [0.10.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.9.1...@oomol/python-executor@0.10.0) (2024-07-19)


### Features

* implement snippet in executor ([#104](https://github.com/oomol/oocana-python/issues/104)) ([496b122](https://github.com/oomol/oocana-python/commit/496b1222d996d6d0fd354bb46c1b9e8391b3fe02))

## [0.9.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.9.0...@oomol/python-executor@0.9.1) (2024-07-17)


### Bug Fixes

* run block raise exception not suppress stderr and stdout message ([#100](https://github.com/oomol/oocana-python/issues/100)) ([1254f73](https://github.com/oomol/oocana-python/commit/1254f73698357e17c61da4f10453d26e2daa73ab))

## [0.9.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.8.0...@oomol/python-executor@0.9.0) (2024-07-17)


### Features

* support module cache duration session ([#98](https://github.com/oomol/oocana-python/issues/98)) ([a3c9b6a](https://github.com/oomol/oocana-python/commit/a3c9b6a111cf29947fa570da0594fdac34708073))

## [0.8.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.7.0...@oomol/python-executor@0.8.0) (2024-07-12)


### Features

* accept service message ([#96](https://github.com/oomol/oocana-python/issues/96)) ([7c626d9](https://github.com/oomol/oocana-python/commit/7c626d912e096cedaaa3b49176607d039d021e7d))
* use service instead of applet ([#94](https://github.com/oomol/oocana-python/issues/94)) ([66bb1d0](https://github.com/oomol/oocana-python/commit/66bb1d01b64295a98ac4b9a56aa76f3cba91c908))


### Bug Fixes

* remove added sys module after return module ([f840805](https://github.com/oomol/oocana-python/commit/f8408053685a9f1aeb161be40bbd08bd09d7c090))
* support run block in background ([fdd191e](https://github.com/oomol/oocana-python/commit/fdd191eda7038e4b24659c6a24891f490ab912f1))
* use set store different job id to keep thread safe ([#92](https://github.com/oomol/oocana-python/issues/92)) ([5ca8448](https://github.com/oomol/oocana-python/commit/5ca8448b785d7fdacc8576e96bb75956e577ae53))
* wrong executor module name ([#95](https://github.com/oomol/oocana-python/issues/95)) ([52e424d](https://github.com/oomol/oocana-python/commit/52e424d8e08aa7137c70c014237c651548e075f8))

## [0.7.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.6.1...@oomol/python-executor@0.7.0) (2024-07-09)


### Features

* follow new json schema ([#82](https://github.com/oomol/oocana-python/issues/82)) ([0d99ba2](https://github.com/oomol/oocana-python/commit/0d99ba29b7003a6cc36c79c087da25aa8e2cb562))

## [0.6.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.6.0...@oomol/python-executor@0.6.1) (2024-07-09)


### Bug Fixes

* wrong module import ([#80](https://github.com/oomol/oocana-python/issues/80)) ([99303d5](https://github.com/oomol/oocana-python/commit/99303d5d251c1237c5a9c9b75794785db9ee8c72))

## [0.6.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.5.10...@oomol/python-executor@0.6.0) (2024-07-03)


### Features

* implement session and block end ([#74](https://github.com/oomol/oocana-python/issues/74)) ([0d96d87](https://github.com/oomol/oocana-python/commit/0d96d87f567e834e14b02484bbba677f7380c956))
