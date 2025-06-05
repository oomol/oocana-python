# Changelog

## [0.16.8](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.7...oocana-python-executor@0.16.8) (2025-06-05)


### Bug Fixes

* coroutine should not be terminated once the function has completed ([#357](https://github.com/oomol/oocana-python/issues/357)) ([a357fdb](https://github.com/oomol/oocana-python/commit/a357fdbe5e592ba60ee1e1203adb4dea20f07d68))

## [0.16.7](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.6...oocana-python-executor@0.16.7) (2025-05-23)


### Features

* add output and new finished field ([#354](https://github.com/oomol/oocana-python/issues/354)) ([d185d3e](https://github.com/oomol/oocana-python/commit/d185d3e8bfb92c80a4775beff3219bd2352852bf))

## [0.16.6](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.5...oocana-python-executor@0.16.6) (2025-05-14)


### Bug Fixes

* support control character in secret ([#341](https://github.com/oomol/oocana-python/issues/341)) ([7b2af11](https://github.com/oomol/oocana-python/commit/7b2af1170e081609274f0fe4cb3337e5c18e2e53))

## [0.16.5](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.4...oocana-python-executor@0.16.5) (2025-05-09)


### Bug Fixes

* add random string to support multiple python executor instance with same info ([#336](https://github.com/oomol/oocana-python/issues/336)) ([d94ed58](https://github.com/oomol/oocana-python/commit/d94ed588bda9ba5ce9be5f537542ec655d2fa0fa))

## [0.16.4](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.3...oocana-python-executor@0.16.4) (2025-04-08)


### Features

* pkg dir ([#331](https://github.com/oomol/oocana-python/issues/331)) ([c45caf2](https://github.com/oomol/oocana-python/commit/c45caf2de16b01c79939a811c0b0d19b34fe5eb1))

## [0.16.3](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.2...oocana-python-executor@0.16.3) (2025-04-01)


### Features

* use executor ready give debug info ([#327](https://github.com/oomol/oocana-python/issues/327)) ([2fc15df](https://github.com/oomol/oocana-python/commit/2fc15dfd139f9d13021b69c3ad056663f2e1b968))


### Bug Fixes

* plotly and matplotlib is different module with no effect ([#329](https://github.com/oomol/oocana-python/issues/329)) ([5a49824](https://github.com/oomol/oocana-python/commit/5a498242db912d456298eadce2b1f1d2e22bce10))

## [0.16.2](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.1...oocana-python-executor@0.16.2) (2025-03-31)


### Features

* add tmp_pkg_dir api ([#325](https://github.com/oomol/oocana-python/issues/325)) ([081d86c](https://github.com/oomol/oocana-python/commit/081d86c8a7f7968262d8ef1d6706e57cda2d2e07))

## [0.16.1](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.16.0...oocana-python-executor@0.16.1) (2025-03-28)


### Features

* improve forward compatible ([#320](https://github.com/oomol/oocana-python/issues/320)) ([2c4de41](https://github.com/oomol/oocana-python/commit/2c4de41dd7add58785b43b5e49777c51f124448c))


### Bug Fixes

* return really exit code  ([#322](https://github.com/oomol/oocana-python/issues/322)) ([171c02f](https://github.com/oomol/oocana-python/commit/171c02fabac894b1b5b541ecc08f40382e8a5f24))


### Code Refactoring

* improve hook ([#323](https://github.com/oomol/oocana-python/issues/323)) ([9f6873f](https://github.com/oomol/oocana-python/commit/9f6873f963400d859ea3a00b6413337ef3646a1e))

## [0.16.0](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.15.4...oocana-python-executor@0.16.0) (2025-03-26)


### ⚠ BREAKING CHANGES

* add tmp dir ([#318](https://github.com/oomol/oocana-python/issues/318))

### Features

* add debug feature by debugpy ([#319](https://github.com/oomol/oocana-python/issues/319)) ([0f5178b](https://github.com/oomol/oocana-python/commit/0f5178beb352f782ddf060800b3d1be0f81ca222))
* add tmp dir ([#318](https://github.com/oomol/oocana-python/issues/318)) ([0ab47ca](https://github.com/oomol/oocana-python/commit/0ab47ca8a204818f5db421b11cd87fbd51462ac7))


### Code Refactoring

* avoid multiple return warning ([#316](https://github.com/oomol/oocana-python/issues/316)) ([13b2447](https://github.com/oomol/oocana-python/commit/13b2447e114f88b41be478aaadd590214733be67))

## [0.15.4](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.15.3...oocana-python-executor@0.15.4) (2025-03-21)


### Features

* use identifier instead of suffix ([#313](https://github.com/oomol/oocana-python/issues/313)) ([75c64a2](https://github.com/oomol/oocana-python/commit/75c64a26f5b06682b0bd257b3e303415f3679819))


### Bug Fixes

* keep parser's exit code as 2 ([#314](https://github.com/oomol/oocana-python/issues/314)) ([1869531](https://github.com/oomol/oocana-python/commit/186953181148ca33b8c4614a956f9ab8e9c30441))

## [0.15.3](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.15.2...oocana-python-executor@0.15.3) (2025-03-21)


### Code Refactoring

* remove compatible ([7817afe](https://github.com/oomol/oocana-python/commit/7817afe812677747ba4d6058d17b5ecdbd6d051f))

## [0.15.2](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.15.1...oocana-python-executor@0.15.2) (2025-03-21)


### Features

* accept identifier executor ([2237085](https://github.com/oomol/oocana-python/commit/2237085dc8244317443b663b5037e47acd8bbf45))

## [0.15.1](https://github.com/oomol/oocana-python/compare/oocana-python-executor@0.15.0...oocana-python-executor@0.15.1) (2025-03-18)


### Bug Fixes

* add package compatible ([c985d4a](https://github.com/oomol/oocana-python/commit/c985d4a76ae206c28d51e68c72ea7363d0243c7f))

## [0.15.0](https://github.com/oomol/oocana-python/compare/oocana-python-executor-v0.14.40...oocana-python-executor@0.15.0) (2025-03-04)


### ⚠ BREAKING CHANGES

* exit after current session finish ([#180](https://github.com/oomol/oocana-python/issues/180))
* test service, add flow auto test ([#170](https://github.com/oomol/oocana-python/issues/170))
* add custom show() handler for matplotlib and plotly ([#159](https://github.com/oomol/oocana-python/issues/159))
* session level executor ([#140](https://github.com/oomol/oocana-python/issues/140))

### Features

* accept service message ([#96](https://github.com/oomol/oocana-python/issues/96)) ([7c626d9](https://github.com/oomol/oocana-python/commit/7c626d912e096cedaaa3b49176607d039d021e7d))
* add bin feature by base64 ([#233](https://github.com/oomol/oocana-python/issues/233)) ([ec43e10](https://github.com/oomol/oocana-python/commit/ec43e10ec897b18e48361abc2c1f3bd53be23232))
* add custom show() handler for matplotlib and plotly ([#159](https://github.com/oomol/oocana-python/issues/159)) ([1581474](https://github.com/oomol/oocana-python/commit/1581474f7df7f6be5a7c4c51b329af628aab105e))
* add global shutdown ([#239](https://github.com/oomol/oocana-python/issues/239)) ([f1bb6f9](https://github.com/oomol/oocana-python/commit/f1bb6f91f3471370a98888109c6f318475ffe09f))
* add package to sys.path ([0c474e0](https://github.com/oomol/oocana-python/commit/0c474e0719ab02233c36bfb058cfb6476da43965))
* add session dir ([#224](https://github.com/oomol/oocana-python/issues/224)) ([9f988dd](https://github.com/oomol/oocana-python/commit/9f988dda4565d78ba45f63dfb1fa9eb0ee5f7c9a))
* apply secret patch ([#227](https://github.com/oomol/oocana-python/issues/227)) ([113fd07](https://github.com/oomol/oocana-python/commit/113fd07bda719e0c1b49228874e3f79f62617f02))
* capture print and send mqtt message immediately ([#245](https://github.com/oomol/oocana-python/issues/245)) ([7acb212](https://github.com/oomol/oocana-python/commit/7acb2127555dc4ca0495f11adf3241b68382ac42))
* change log dir to support multiple executor instance ([#216](https://github.com/oomol/oocana-python/issues/216)) ([4bf548c](https://github.com/oomol/oocana-python/commit/4bf548c5b3e31df1bff106e3cc40363de89fca93))
* delay exit after new session start for rerun cache ([#142](https://github.com/oomol/oocana-python/issues/142)) ([6073583](https://github.com/oomol/oocana-python/commit/6073583c554d2f3380125178362ea51a0ee73a25))
* delete temp source after session end ([75bf533](https://github.com/oomol/oocana-python/commit/75bf5332cb5e70846327a338848af24f2da22b2d))
* executor ready add package field ([ca2e0f5](https://github.com/oomol/oocana-python/commit/ca2e0f5e4e581a50c03dde791e43d6645f4004ae))
* exit after current session finish ([#180](https://github.com/oomol/oocana-python/issues/180)) ([6e50612](https://github.com/oomol/oocana-python/commit/6e5061236b8b2c42627706a78a93a036e01fa18f))
* follow new json schema ([#82](https://github.com/oomol/oocana-python/issues/82)) ([0d99ba2](https://github.com/oomol/oocana-python/commit/0d99ba29b7003a6cc36c79c087da25aa8e2cb562))
* implement snippet in executor ([#104](https://github.com/oomol/oocana-python/issues/104)) ([496b122](https://github.com/oomol/oocana-python/commit/496b1222d996d6d0fd354bb46c1b9e8391b3fe02))
* improve async code ([#220](https://github.com/oomol/oocana-python/issues/220)) ([2349251](https://github.com/oomol/oocana-python/commit/2349251a9ec8063a91e26e07723073007dcc8014))
* matplotlib switch style by theme env ([#295](https://github.com/oomol/oocana-python/issues/295)) ([a4301e5](https://github.com/oomol/oocana-python/commit/a4301e59859a3f64718d8b2b97915ec92f971357))
* move tmp files to &lt;session_id&gt; and only delete this directory ([#115](https://github.com/oomol/oocana-python/issues/115)) ([49e2769](https://github.com/oomol/oocana-python/commit/49e276918b16a1fec490fb3283ca29bd8f81eafb))
* pass through more relative info to mainframe ([eb09810](https://github.com/oomol/oocana-python/commit/eb0981031307a16363b3ce6c6fdcc9a955ceb800))
* publish package to pypi ([#301](https://github.com/oomol/oocana-python/issues/301)) ([f1bce12](https://github.com/oomol/oocana-python/commit/f1bce12cbc623be303c5cb329e58be1a9803bbc3))
* remove unused api ([#188](https://github.com/oomol/oocana-python/issues/188)) ([c2f633e](https://github.com/oomol/oocana-python/commit/c2f633e7c951ac5b122c39ceb4d7259196b8de65))
* replace exit ([#241](https://github.com/oomol/oocana-python/issues/241)) ([22b867b](https://github.com/oomol/oocana-python/commit/22b867b914a2cf9c4820e7b60e5849cfb4f5c3e9))
* return None when secret is null ([086ea55](https://github.com/oomol/oocana-python/commit/086ea55df55001f1ca9a04722bbf0d379f67c329))
* session level executor ([#140](https://github.com/oomol/oocana-python/issues/140)) ([ca77bec](https://github.com/oomol/oocana-python/commit/ca77becb427d22d516a8fca6f8a1c413953d201c))
* skip if not current package ([#203](https://github.com/oomol/oocana-python/issues/203)) ([98b70eb](https://github.com/oomol/oocana-python/commit/98b70eba80cf9f0ce58c2adb89a02fec2d463164))
* spilt global logger and executor, add context logger for block ([#283](https://github.com/oomol/oocana-python/issues/283)) ([a845bb9](https://github.com/oomol/oocana-python/commit/a845bb9be3390cf03cfca87770f88ffcf37577b3))
* support ${{OO_SECRET: xxx}} secret format ([#274](https://github.com/oomol/oocana-python/issues/274)) ([9a0e842](https://github.com/oomol/oocana-python/commit/9a0e842a8753e02cf29b6aec2de88633bd6f645f))
* support float and add some docs ([#149](https://github.com/oomol/oocana-python/issues/149)) ([16935cc](https://github.com/oomol/oocana-python/commit/16935ccc604de149310dea906e73bb1afe3f00ae))
* support global service ([#235](https://github.com/oomol/oocana-python/issues/235)) ([def49c0](https://github.com/oomol/oocana-python/commit/def49c0cd0ac96a1bbade1f0f2f3134863bf1741))
* support module cache duration session ([#98](https://github.com/oomol/oocana-python/issues/98)) ([a3c9b6a](https://github.com/oomol/oocana-python/commit/a3c9b6a111cf29947fa570da0594fdac34708073))
* support sub secret replace ([#229](https://github.com/oomol/oocana-python/issues/229)) ([1582881](https://github.com/oomol/oocana-python/commit/158288144e21fa6fd3c21f5c89ab04b02f98339a))
* test service, add flow auto test ([#170](https://github.com/oomol/oocana-python/issues/170)) ([2550582](https://github.com/oomol/oocana-python/commit/25505823a4916d3ddaf24616461ac813f12a416a))
* use pathname for detail logger ([8a18767](https://github.com/oomol/oocana-python/commit/8a18767cc0dcc2edb7ddf3c5d66b878b0579f7d5))
* use service instead of applet ([#94](https://github.com/oomol/oocana-python/issues/94)) ([66bb1d0](https://github.com/oomol/oocana-python/commit/66bb1d01b64295a98ac4b9a56aa76f3cba91c908))
* use special field to mark binary value ([#266](https://github.com/oomol/oocana-python/issues/266)) ([9705ee2](https://github.com/oomol/oocana-python/commit/9705ee224fb9379184686a2f3750a0c9867a2638))
* write binary to file instead of base64 ([#240](https://github.com/oomol/oocana-python/issues/240)) ([715a8cc](https://github.com/oomol/oocana-python/commit/715a8cca8c0efb84710fd94a0f8e2498d5f367ff))


### Bug Fixes

* add message type for reporter ([47d8fb3](https://github.com/oomol/oocana-python/commit/47d8fb3926e017324109cc51ffe64479140191ac))
* add secret fallback ([224b002](https://github.com/oomol/oocana-python/commit/224b002c2ba330358ca4a876b8e4493404119b1c))
* avoid expose executor path to sys.path ([#293](https://github.com/oomol/oocana-python/issues/293)) ([3425b13](https://github.com/oomol/oocana-python/commit/3425b13c37c78b73e1859417ecf30b5de9937978))
* call done message after other message done ([1a89141](https://github.com/oomol/oocana-python/commit/1a89141d2288e5c1c8ed882fca60fb840424b1fb))
* clear code cache after session end ([#146](https://github.com/oomol/oocana-python/issues/146)) ([b48ca03](https://github.com/oomol/oocana-python/commit/b48ca03929a59417343b62ba591f77cc31707c47))
* exit fail in child process ([07adce8](https://github.com/oomol/oocana-python/commit/07adce8457f1e7fefa4eb95ba0a9f050715ea3f8))
* function should be in options field ([dd6787e](https://github.com/oomol/oocana-python/commit/dd6787ea0213a8cd20b8b4fc61963f706c7e39c6))
* improve python3.10 compatible ([867d7b2](https://github.com/oomol/oocana-python/commit/867d7b23cbc0e6df5e79409d0427f8c5d77762b9))
* lock load module function ([#206](https://github.com/oomol/oocana-python/issues/206)) ([1e88c25](https://github.com/oomol/oocana-python/commit/1e88c2590c4d084d1c2122f2a62e841a0655c55d))
* missing drop message path ([2c14cc2](https://github.com/oomol/oocana-python/commit/2c14cc27ad8d78a318414a01dd700689f466114e))
* missing matplotlib ([7b45c94](https://github.com/oomol/oocana-python/commit/7b45c9456f7b26718af99b46bf0336cc405a97c6))
* missing module and global var ([#161](https://github.com/oomol/oocana-python/issues/161)) ([403ccdb](https://github.com/oomol/oocana-python/commit/403ccdb957e65561159b4c39469f2fa05800ce98))
* missing some commit  ([#144](https://github.com/oomol/oocana-python/issues/144)) ([0b62b0b](https://github.com/oomol/oocana-python/commit/0b62b0b59d59d5ebcd5e85f4bf48f22cc86cd079))
* mixing file path module conflict ([dfa9bb3](https://github.com/oomol/oocana-python/commit/dfa9bb3c67d5fd1d2ecd9e473a55d2eec9bfc4c9))
* module file maybe None ([2d59149](https://github.com/oomol/oocana-python/commit/2d59149d52d4b3544f9347c2c137da301065316a))
* move mqtt logger to executor logger ([#286](https://github.com/oomol/oocana-python/issues/286)) ([f2efda2](https://github.com/oomol/oocana-python/commit/f2efda269e49f351328461868034a4218b83f9f4))
* none package executor should only accept none package filed block ([870150d](https://github.com/oomol/oocana-python/commit/870150d8e8ced143ec4c69dadeb2802e8cb62a17))
* only remove module that in flow, keep dependencies modules in site-package ([#176](https://github.com/oomol/oocana-python/issues/176)) ([0c532c7](https://github.com/oomol/oocana-python/commit/0c532c71035d058e7f08265e0203367336709462))
* plotly get context issue, use cdn, remove html margin ([#164](https://github.com/oomol/oocana-python/issues/164)) ([4098606](https://github.com/oomol/oocana-python/commit/40986064fc8259baa5799f979b82c4ad2940c74e))
* **python_executor:** 3.10 f-string SyntaxError ([#210](https://github.com/oomol/oocana-python/issues/210)) ([bc875f4](https://github.com/oomol/oocana-python/commit/bc875f49a13e75c2c973b8fbd8d54bfef34dbe2b))
* remove .scriptlets directory ([e18b20c](https://github.com/oomol/oocana-python/commit/e18b20c5e48c487eba73b48abb0b0967cf62f7bc))
* remove added sys module after return module ([f840805](https://github.com/oomol/oocana-python/commit/f8408053685a9f1aeb161be40bbd08bd09d7c090))
* run block raise exception not suppress stderr and stdout message ([#100](https://github.com/oomol/oocana-python/issues/100)) ([1254f73](https://github.com/oomol/oocana-python/commit/1254f73698357e17c61da4f10453d26e2daa73ab))
* session level service should exit after session finished ([#195](https://github.com/oomol/oocana-python/issues/195)) ([2e4116d](https://github.com/oomol/oocana-python/commit/2e4116dda9dbd37f2d5629c4acf50892c9612465))
* skip set value if no value in store ([24d95b8](https://github.com/oomol/oocana-python/commit/24d95b8041c66e83dae93cfe1ecd947a528c7509))
* split executor log and global log ([2648890](https://github.com/oomol/oocana-python/commit/26488903d6bbc00610069cb46c373920b12b96cc))
* support run block in background ([fdd191e](https://github.com/oomol/oocana-python/commit/fdd191eda7038e4b24659c6a24891f490ab912f1))
* transform to str ([fd6c5bf](https://github.com/oomol/oocana-python/commit/fd6c5bf0c89600ca6e9d45b1248cd3147ab91c2f))
* uncomment preview ([d8ca88b](https://github.com/oomol/oocana-python/commit/d8ca88b61eea5c9c493961923de2858f1fbc8048))
* update import path for vars in oomol.py ([#252](https://github.com/oomol/oocana-python/issues/252)) ([2e74bfc](https://github.com/oomol/oocana-python/commit/2e74bfc0a2ab96d12c4268afbca761e22a06199f))
* use abspath resolve relative path ([8a5b963](https://github.com/oomol/oocana-python/commit/8a5b9630985dc0c8ef84e6cb1a221571ecb3eb11))
* use context vars to directly pass context instead of sys.modules ([#251](https://github.com/oomol/oocana-python/issues/251)) ([14aeca1](https://github.com/oomol/oocana-python/commit/14aeca1b3984643fa8d7892876b1764722b92689))
* use delay delete for workaround ([#132](https://github.com/oomol/oocana-python/issues/132)) ([54687f8](https://github.com/oomol/oocana-python/commit/54687f8527d0f1c71e14ab29fcfb0cd41b42c83d))
* use file path not node id ([#172](https://github.com/oomol/oocana-python/issues/172)) ([5824c99](https://github.com/oomol/oocana-python/commit/5824c994c30f80f3d46f134612e8cea45f43126b))
* use home dir path ([#183](https://github.com/oomol/oocana-python/issues/183)) ([a0597e9](https://github.com/oomol/oocana-python/commit/a0597e99ac7f814c2f6f51544e42d51db83c9c2e))
* use set store different job id to keep thread safe ([#92](https://github.com/oomol/oocana-python/issues/92)) ([5ca8448](https://github.com/oomol/oocana-python/commit/5ca8448b785d7fdacc8576e96bb75956e577ae53))
* workaround for some block run twice ([#277](https://github.com/oomol/oocana-python/issues/277)) ([2b02300](https://github.com/oomol/oocana-python/commit/2b0230040eaa0636c4e4f5c4026303852655795c))
* wrong executor module name ([#95](https://github.com/oomol/oocana-python/issues/95)) ([52e424d](https://github.com/oomol/oocana-python/commit/52e424d8e08aa7137c70c014237c651548e075f8))
* wrong EXECUTOR NAME ([#131](https://github.com/oomol/oocana-python/issues/131)) ([fc93311](https://github.com/oomol/oocana-python/commit/fc93311d7697047728981caa25c25abfceb2e191))
* wrong module import ([#80](https://github.com/oomol/oocana-python/issues/80)) ([99303d5](https://github.com/oomol/oocana-python/commit/99303d5d251c1237c5a9c9b75794785db9ee8c72))


### Code Refactoring

* add dark theme to plotly html ([#168](https://github.com/oomol/oocana-python/issues/168)) ([e4bbda7](https://github.com/oomol/oocana-python/commit/e4bbda77989c4fb656d05d27b631ae227adcdcc9))
* do not exit when new session start, only exit when current session finish ([703a4dd](https://github.com/oomol/oocana-python/commit/703a4dd6edb0f3ec6219ede309b96f380ddab25a))
* follow new api ([10576bc](https://github.com/oomol/oocana-python/commit/10576bc07532b50c9211e682611786de6fa8983a))
* improve ci and publish files ([#153](https://github.com/oomol/oocana-python/issues/153)) ([41e207f](https://github.com/oomol/oocana-python/commit/41e207f4272d49fdbea7c0600b9fdf97ce04b705))
* improve logger options and logic ([#151](https://github.com/oomol/oocana-python/issues/151)) ([567b305](https://github.com/oomol/oocana-python/commit/567b305f6ff63b6dd07b7842c000d6da819f6aee))
* improve logic ([#222](https://github.com/oomol/oocana-python/issues/222)) ([7f8bb26](https://github.com/oomol/oocana-python/commit/7f8bb26624c8a37b6a8551ada6d478d88c018db6))
* improve service ([#223](https://github.com/oomol/oocana-python/issues/223)) ([13422da](https://github.com/oomol/oocana-python/commit/13422da51dec6a211f684ec71d5f396acb0540a8))
* move log location ([#243](https://github.com/oomol/oocana-python/issues/243)) ([1d509a1](https://github.com/oomol/oocana-python/commit/1d509a13bebd38fcd87ad79ffb4373de69021e44))
* move to monorepo struct with pdm ([#75](https://github.com/oomol/oocana-python/issues/75)) ([c6da6fb](https://github.com/oomol/oocana-python/commit/c6da6fbc8806632170170213d5022d2e8dffc2b9))
* move typedDict to dataclasses and recovery test example ([#106](https://github.com/oomol/oocana-python/issues/106)) ([7e348d9](https://github.com/oomol/oocana-python/commit/7e348d9e417402605ae01466695bb7746378ef6d))
* plotly background follow theme ([#297](https://github.com/oomol/oocana-python/issues/297)) ([5b8cf92](https://github.com/oomol/oocana-python/commit/5b8cf9258737a8b6cb955620ca605fae4c75577c))
* plotly.js use another cdn ([#193](https://github.com/oomol/oocana-python/issues/193)) ([30b3864](https://github.com/oomol/oocana-python/commit/30b38645dab3505563b7ae68afc881178a5585e9))
* prepare service api ([#157](https://github.com/oomol/oocana-python/issues/157)) ([9c75547](https://github.com/oomol/oocana-python/commit/9c755471cf76fb6abd3458b7b698a3a3cf65dc96))
* remove unused function ([e81d5a5](https://github.com/oomol/oocana-python/commit/e81d5a5b144e4845287809c7277a7510ba9400fb))
* remove unused topic and add more relative client id ([af2c957](https://github.com/oomol/oocana-python/commit/af2c9579c7d4d31d15048f79bcb61f4b61e9f7f9))
* rename api ([c58c425](https://github.com/oomol/oocana-python/commit/c58c4258c64c8eff88e595cad2f9ba0cc49e8819))
* rename to snake_case and remove unused api ([c58c425](https://github.com/oomol/oocana-python/commit/c58c4258c64c8eff88e595cad2f9ba0cc49e8819))
* support show multiple figures, plotly set dark theme ([#166](https://github.com/oomol/oocana-python/issues/166)) ([409c79e](https://github.com/oomol/oocana-python/commit/409c79ee5b1b950f548a69051da8b72017917a49))
* update plotly theme by env ([#290](https://github.com/oomol/oocana-python/issues/290)) ([3a25982](https://github.com/oomol/oocana-python/commit/3a25982644e716612acf2a9292d675f35aef5668))
* use wrapper value to combine var value, and use fixed field for all wrapper value ([#268](https://github.com/oomol/oocana-python/issues/268)) ([1cdca46](https://github.com/oomol/oocana-python/commit/1cdca46011d1b09e9cf3c0476efcfdde163e2983))
* vertically center plotly preview ([#299](https://github.com/oomol/oocana-python/issues/299)) ([c0a8c5a](https://github.com/oomol/oocana-python/commit/c0a8c5afc3c179359e3d04255eb5a12736a3e930))

## [0.14.40](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.39...@oomol/python-executor@0.14.40) (2025-02-20)


### Code Refactoring

* vertically center plotly preview ([#299](https://github.com/oomol/oocana-python/issues/299)) ([c0a8c5a](https://github.com/oomol/oocana-python/commit/c0a8c5afc3c179359e3d04255eb5a12736a3e930))

## [0.14.39](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.38...@oomol/python-executor@0.14.39) (2025-02-19)


### Code Refactoring

* plotly background follow theme ([#297](https://github.com/oomol/oocana-python/issues/297)) ([5b8cf92](https://github.com/oomol/oocana-python/commit/5b8cf9258737a8b6cb955620ca605fae4c75577c))

## [0.14.38](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.37...@oomol/python-executor@0.14.38) (2025-02-18)


### Features

* matplotlib switch style by theme env ([#295](https://github.com/oomol/oocana-python/issues/295)) ([a4301e5](https://github.com/oomol/oocana-python/commit/a4301e59859a3f64718d8b2b97915ec92f971357))

## [0.14.37](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.36...@oomol/python-executor@0.14.37) (2025-02-17)


### Bug Fixes

* avoid expose executor path to sys.path ([#293](https://github.com/oomol/oocana-python/issues/293)) ([3425b13](https://github.com/oomol/oocana-python/commit/3425b13c37c78b73e1859417ecf30b5de9937978))

## [0.14.36](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.35...@oomol/python-executor@0.14.36) (2025-02-17)


### Code Refactoring

* update plotly theme by env ([#290](https://github.com/oomol/oocana-python/issues/290)) ([3a25982](https://github.com/oomol/oocana-python/commit/3a25982644e716612acf2a9292d675f35aef5668))

## [0.14.35](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.34...@oomol/python-executor@0.14.35) (2025-02-10)


### Bug Fixes

* split executor log and global log ([2648890](https://github.com/oomol/oocana-python/commit/26488903d6bbc00610069cb46c373920b12b96cc))

## [0.14.34](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.33...@oomol/python-executor@0.14.34) (2025-02-05)


### Bug Fixes

* move mqtt logger to executor logger ([#286](https://github.com/oomol/oocana-python/issues/286)) ([f2efda2](https://github.com/oomol/oocana-python/commit/f2efda269e49f351328461868034a4218b83f9f4))

## [0.14.33](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.32...@oomol/python-executor@0.14.33) (2025-01-23)


### Features

* spilt global logger and executor, add context logger for block ([#283](https://github.com/oomol/oocana-python/issues/283)) ([a845bb9](https://github.com/oomol/oocana-python/commit/a845bb9be3390cf03cfca87770f88ffcf37577b3))

## [0.14.32](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.31...@oomol/python-executor@0.14.32) (2025-01-22)


### Bug Fixes

* workaround for some block run twice ([#277](https://github.com/oomol/oocana-python/issues/277)) ([2b02300](https://github.com/oomol/oocana-python/commit/2b0230040eaa0636c4e4f5c4026303852655795c))

## [0.14.31](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.30...@oomol/python-executor@0.14.31) (2025-01-21)


### Bug Fixes

* add secret fallback ([224b002](https://github.com/oomol/oocana-python/commit/224b002c2ba330358ca4a876b8e4493404119b1c))

## [0.14.30](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.29...@oomol/python-executor@0.14.30) (2025-01-20)


### Features

* support ${{OO_SECRET: xxx}} secret format ([#274](https://github.com/oomol/oocana-python/issues/274)) ([9a0e842](https://github.com/oomol/oocana-python/commit/9a0e842a8753e02cf29b6aec2de88633bd6f645f))

## [0.14.29](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.28...@oomol/python-executor@0.14.29) (2025-01-09)


### Features

* pass through more relative info to mainframe ([eb09810](https://github.com/oomol/oocana-python/commit/eb0981031307a16363b3ce6c6fdcc9a955ceb800))


### Code Refactoring

* remove unused topic and add more relative client id ([af2c957](https://github.com/oomol/oocana-python/commit/af2c9579c7d4d31d15048f79bcb61f4b61e9f7f9))

## [0.14.28](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.27...@oomol/python-executor@0.14.28) (2025-01-08)


### Code Refactoring

* use wrapper value to combine var value, and use fixed field for all wrapper value ([#268](https://github.com/oomol/oocana-python/issues/268)) ([1cdca46](https://github.com/oomol/oocana-python/commit/1cdca46011d1b09e9cf3c0476efcfdde163e2983))

## [0.14.27](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.26...@oomol/python-executor@0.14.27) (2025-01-07)


### Features

* use special field to mark binary value ([#266](https://github.com/oomol/oocana-python/issues/266)) ([9705ee2](https://github.com/oomol/oocana-python/commit/9705ee224fb9379184686a2f3750a0c9867a2638))

## [0.14.26](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.25...@oomol/python-executor@0.14.26) (2025-01-02)


### Features

* return None when secret is null ([086ea55](https://github.com/oomol/oocana-python/commit/086ea55df55001f1ca9a04722bbf0d379f67c329))

## [0.14.25](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.24...@oomol/python-executor@0.14.25) (2024-12-27)


### Bug Fixes

* update import path for vars in oomol.py ([#252](https://github.com/oomol/oocana-python/issues/252)) ([2e74bfc](https://github.com/oomol/oocana-python/commit/2e74bfc0a2ab96d12c4268afbca761e22a06199f))

## [0.14.24](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.23...@oomol/python-executor@0.14.24) (2024-12-27)


### Features

* use pathname for detail logger ([8a18767](https://github.com/oomol/oocana-python/commit/8a18767cc0dcc2edb7ddf3c5d66b878b0579f7d5))


### Bug Fixes

* use context vars to directly pass context instead of sys.modules ([#251](https://github.com/oomol/oocana-python/issues/251)) ([14aeca1](https://github.com/oomol/oocana-python/commit/14aeca1b3984643fa8d7892876b1764722b92689))

## [0.14.23](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.22...@oomol/python-executor@0.14.23) (2024-12-24)


### Features

* capture print and send mqtt message immediately ([#245](https://github.com/oomol/oocana-python/issues/245)) ([7acb212](https://github.com/oomol/oocana-python/commit/7acb2127555dc4ca0495f11adf3241b68382ac42))

## [0.14.22](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.21...@oomol/python-executor@0.14.22) (2024-12-23)


### Code Refactoring

* move log location ([#243](https://github.com/oomol/oocana-python/issues/243)) ([1d509a1](https://github.com/oomol/oocana-python/commit/1d509a13bebd38fcd87ad79ffb4373de69021e44))

## [0.14.21](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.20...@oomol/python-executor@0.14.21) (2024-12-23)


### Features

* replace exit ([#241](https://github.com/oomol/oocana-python/issues/241)) ([22b867b](https://github.com/oomol/oocana-python/commit/22b867b914a2cf9c4820e7b60e5849cfb4f5c3e9))

## [0.14.20](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.19...@oomol/python-executor@0.14.20) (2024-12-19)


### Features

* add global shutdown ([#239](https://github.com/oomol/oocana-python/issues/239)) ([f1bb6f9](https://github.com/oomol/oocana-python/commit/f1bb6f91f3471370a98888109c6f318475ffe09f))
* support global service ([#235](https://github.com/oomol/oocana-python/issues/235)) ([def49c0](https://github.com/oomol/oocana-python/commit/def49c0cd0ac96a1bbade1f0f2f3134863bf1741))
* write binary to file instead of base64 ([#240](https://github.com/oomol/oocana-python/issues/240)) ([715a8cc](https://github.com/oomol/oocana-python/commit/715a8cca8c0efb84710fd94a0f8e2498d5f367ff))

## [0.14.19](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.18...@oomol/python-executor@0.14.19) (2024-12-12)


### Features

* add bin feature by base64 ([#233](https://github.com/oomol/oocana-python/issues/233)) ([ec43e10](https://github.com/oomol/oocana-python/commit/ec43e10ec897b18e48361abc2c1f3bd53be23232))

## [0.14.18](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.17...@oomol/python-executor@0.14.18) (2024-12-12)


### Features

* add package to sys.path ([0c474e0](https://github.com/oomol/oocana-python/commit/0c474e0719ab02233c36bfb058cfb6476da43965))

## [0.14.17](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.16...@oomol/python-executor@0.14.17) (2024-12-10)


### Features

* support sub secret replace ([#229](https://github.com/oomol/oocana-python/issues/229)) ([1582881](https://github.com/oomol/oocana-python/commit/158288144e21fa6fd3c21f5c89ab04b02f98339a))

## [0.14.16](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.15...@oomol/python-executor@0.14.16) (2024-12-05)


### Features

* apply secret patch ([#227](https://github.com/oomol/oocana-python/issues/227)) ([113fd07](https://github.com/oomol/oocana-python/commit/113fd07bda719e0c1b49228874e3f79f62617f02))

## [0.14.15](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.14...@oomol/python-executor@0.14.15) (2024-11-07)


### Features

* add session dir ([#224](https://github.com/oomol/oocana-python/issues/224)) ([9f988dd](https://github.com/oomol/oocana-python/commit/9f988dda4565d78ba45f63dfb1fa9eb0ee5f7c9a))
* improve async code ([#220](https://github.com/oomol/oocana-python/issues/220)) ([2349251](https://github.com/oomol/oocana-python/commit/2349251a9ec8063a91e26e07723073007dcc8014))


### Code Refactoring

* improve logic ([#222](https://github.com/oomol/oocana-python/issues/222)) ([7f8bb26](https://github.com/oomol/oocana-python/commit/7f8bb26624c8a37b6a8551ada6d478d88c018db6))
* improve service ([#223](https://github.com/oomol/oocana-python/issues/223)) ([13422da](https://github.com/oomol/oocana-python/commit/13422da51dec6a211f684ec71d5f396acb0540a8))

## [0.14.14](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.13...@oomol/python-executor@0.14.14) (2024-10-15)


### Bug Fixes

* none package executor should only accept none package filed block ([870150d](https://github.com/oomol/oocana-python/commit/870150d8e8ced143ec4c69dadeb2802e8cb62a17))

## [0.14.13](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.12...@oomol/python-executor@0.14.13) (2024-10-14)


### Features

* executor ready add package field ([ca2e0f5](https://github.com/oomol/oocana-python/commit/ca2e0f5e4e581a50c03dde791e43d6645f4004ae))

## [0.14.12](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.11...@oomol/python-executor@0.14.12) (2024-10-12)


### Features

* change log dir to support multiple executor instance ([#216](https://github.com/oomol/oocana-python/issues/216)) ([4bf548c](https://github.com/oomol/oocana-python/commit/4bf548c5b3e31df1bff106e3cc40363de89fca93))

## [0.14.11](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.10...@oomol/python-executor@0.14.11) (2024-09-30)


### Bug Fixes

* **python_executor:** 3.10 f-string SyntaxError ([#210](https://github.com/oomol/oocana-python/issues/210)) ([bc875f4](https://github.com/oomol/oocana-python/commit/bc875f49a13e75c2c973b8fbd8d54bfef34dbe2b))

## [0.14.10](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.9...@oomol/python-executor@0.14.10) (2024-09-27)


### Bug Fixes

* lock load module function ([#206](https://github.com/oomol/oocana-python/issues/206)) ([1e88c25](https://github.com/oomol/oocana-python/commit/1e88c2590c4d084d1c2122f2a62e841a0655c55d))

## [0.14.9](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.8...@oomol/python-executor@0.14.9) (2024-09-26)


### Features

* skip if not current package ([#203](https://github.com/oomol/oocana-python/issues/203)) ([98b70eb](https://github.com/oomol/oocana-python/commit/98b70eba80cf9f0ce58c2adb89a02fec2d463164))

## [0.14.8](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.7...@oomol/python-executor@0.14.8) (2024-09-14)


### Bug Fixes

* session level service should exit after session finished ([#195](https://github.com/oomol/oocana-python/issues/195)) ([2e4116d](https://github.com/oomol/oocana-python/commit/2e4116dda9dbd37f2d5629c4acf50892c9612465))

## [0.14.7](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.6...@oomol/python-executor@0.14.7) (2024-09-14)


### Code Refactoring

* plotly.js use another cdn ([#193](https://github.com/oomol/oocana-python/issues/193)) ([30b3864](https://github.com/oomol/oocana-python/commit/30b38645dab3505563b7ae68afc881178a5585e9))

## [0.14.6](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.5...@oomol/python-executor@0.14.6) (2024-09-12)


### Bug Fixes

* improve python3.10 compatible ([867d7b2](https://github.com/oomol/oocana-python/commit/867d7b23cbc0e6df5e79409d0427f8c5d77762b9))

## [0.14.5](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.4...@oomol/python-executor@0.14.5) (2024-09-12)


### Bug Fixes

* exit fail in child process ([07adce8](https://github.com/oomol/oocana-python/commit/07adce8457f1e7fefa4eb95ba0a9f050715ea3f8))


### Code Refactoring

* do not exit when new session start, only exit when current session finish ([703a4dd](https://github.com/oomol/oocana-python/commit/703a4dd6edb0f3ec6219ede309b96f380ddab25a))
* remove unused function ([e81d5a5](https://github.com/oomol/oocana-python/commit/e81d5a5b144e4845287809c7277a7510ba9400fb))

## [0.14.4](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.3...@oomol/python-executor@0.14.4) (2024-09-08)


### Features

* remove unused api ([#188](https://github.com/oomol/oocana-python/issues/188)) ([c2f633e](https://github.com/oomol/oocana-python/commit/c2f633e7c951ac5b122c39ceb4d7259196b8de65))

## [0.14.3](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.2...@oomol/python-executor@0.14.3) (2024-09-07)


### Code Refactoring

* rename api ([c58c425](https://github.com/oomol/oocana-python/commit/c58c4258c64c8eff88e595cad2f9ba0cc49e8819))
* rename to snake_case and remove unused api ([c58c425](https://github.com/oomol/oocana-python/commit/c58c4258c64c8eff88e595cad2f9ba0cc49e8819))

## [0.14.2](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.1...@oomol/python-executor@0.14.2) (2024-09-07)


### Code Refactoring

* follow new api ([10576bc](https://github.com/oomol/oocana-python/commit/10576bc07532b50c9211e682611786de6fa8983a))

## [0.14.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.14.0...@oomol/python-executor@0.14.1) (2024-09-06)


### Bug Fixes

* use home dir path ([#183](https://github.com/oomol/oocana-python/issues/183)) ([a0597e9](https://github.com/oomol/oocana-python/commit/a0597e99ac7f814c2f6f51544e42d51db83c9c2e))

## [0.14.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.5...@oomol/python-executor@0.14.0) (2024-09-04)


### ⚠ BREAKING CHANGES

* exit after current session finish ([#180](https://github.com/oomol/oocana-python/issues/180))

### Features

* exit after current session finish ([#180](https://github.com/oomol/oocana-python/issues/180)) ([6e50612](https://github.com/oomol/oocana-python/commit/6e5061236b8b2c42627706a78a93a036e01fa18f))

## [0.13.5](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.4...@oomol/python-executor@0.13.5) (2024-09-03)


### Bug Fixes

* module file maybe None ([2d59149](https://github.com/oomol/oocana-python/commit/2d59149d52d4b3544f9347c2c137da301065316a))

## [0.13.4](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.3...@oomol/python-executor@0.13.4) (2024-09-03)


### Bug Fixes

* skip set value if no value in store ([24d95b8](https://github.com/oomol/oocana-python/commit/24d95b8041c66e83dae93cfe1ecd947a528c7509))

## [0.13.3](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.2...@oomol/python-executor@0.13.3) (2024-09-03)


### Bug Fixes

* only remove module that in flow, keep dependencies modules in site-package ([#176](https://github.com/oomol/oocana-python/issues/176)) ([0c532c7](https://github.com/oomol/oocana-python/commit/0c532c71035d058e7f08265e0203367336709462))

## [0.13.2](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.1...@oomol/python-executor@0.13.2) (2024-09-02)


### Bug Fixes

* mixing file path module conflict ([dfa9bb3](https://github.com/oomol/oocana-python/commit/dfa9bb3c67d5fd1d2ecd9e473a55d2eec9bfc4c9))
* transform to str ([fd6c5bf](https://github.com/oomol/oocana-python/commit/fd6c5bf0c89600ca6e9d45b1248cd3147ab91c2f))
* use abspath resolve relative path ([8a5b963](https://github.com/oomol/oocana-python/commit/8a5b9630985dc0c8ef84e6cb1a221571ecb3eb11))

## [0.13.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.13.0...@oomol/python-executor@0.13.1) (2024-08-30)


### Bug Fixes

* use file path not node id ([#172](https://github.com/oomol/oocana-python/issues/172)) ([5824c99](https://github.com/oomol/oocana-python/commit/5824c994c30f80f3d46f134612e8cea45f43126b))

## [0.13.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.5...@oomol/python-executor@0.13.0) (2024-08-29)


### ⚠ BREAKING CHANGES

* test service, add flow auto test ([#170](https://github.com/oomol/oocana-python/issues/170))

### Features

* test service, add flow auto test ([#170](https://github.com/oomol/oocana-python/issues/170)) ([2550582](https://github.com/oomol/oocana-python/commit/25505823a4916d3ddaf24616461ac813f12a416a))

## [0.12.5](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.4...@oomol/python-executor@0.12.5) (2024-08-29)


### Code Refactoring

* add dark theme to plotly html ([#168](https://github.com/oomol/oocana-python/issues/168)) ([e4bbda7](https://github.com/oomol/oocana-python/commit/e4bbda77989c4fb656d05d27b631ae227adcdcc9))

## [0.12.4](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.3...@oomol/python-executor@0.12.4) (2024-08-29)


### Code Refactoring

* support show multiple figures, plotly set dark theme ([#166](https://github.com/oomol/oocana-python/issues/166)) ([409c79e](https://github.com/oomol/oocana-python/commit/409c79ee5b1b950f548a69051da8b72017917a49))

## [0.12.3](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.2...@oomol/python-executor@0.12.3) (2024-08-28)


### Bug Fixes

* plotly get context issue, use cdn, remove html margin ([#164](https://github.com/oomol/oocana-python/issues/164)) ([4098606](https://github.com/oomol/oocana-python/commit/40986064fc8259baa5799f979b82c4ad2940c74e))

## [0.12.2](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.1...@oomol/python-executor@0.12.2) (2024-08-28)


### Bug Fixes

* missing matplotlib ([7b45c94](https://github.com/oomol/oocana-python/commit/7b45c9456f7b26718af99b46bf0336cc405a97c6))

## [0.12.1](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.12.0...@oomol/python-executor@0.12.1) (2024-08-28)


### Bug Fixes

* missing module and global var ([#161](https://github.com/oomol/oocana-python/issues/161)) ([403ccdb](https://github.com/oomol/oocana-python/commit/403ccdb957e65561159b4c39469f2fa05800ce98))
* uncomment preview ([d8ca88b](https://github.com/oomol/oocana-python/commit/d8ca88b61eea5c9c493961923de2858f1fbc8048))

## [0.12.0](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.5...@oomol/python-executor@0.12.0) (2024-08-28)


### ⚠ BREAKING CHANGES

* add custom show() handler for matplotlib and plotly ([#159](https://github.com/oomol/oocana-python/issues/159))

### Features

* add custom show() handler for matplotlib and plotly ([#159](https://github.com/oomol/oocana-python/issues/159)) ([1581474](https://github.com/oomol/oocana-python/commit/1581474f7df7f6be5a7c4c51b329af628aab105e))

## [0.11.5](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.4...@oomol/python-executor@0.11.5) (2024-08-28)


### Code Refactoring

* improve ci and publish files ([#153](https://github.com/oomol/oocana-python/issues/153)) ([41e207f](https://github.com/oomol/oocana-python/commit/41e207f4272d49fdbea7c0600b9fdf97ce04b705))
* improve logger options and logic ([#151](https://github.com/oomol/oocana-python/issues/151)) ([567b305](https://github.com/oomol/oocana-python/commit/567b305f6ff63b6dd07b7842c000d6da819f6aee))
* prepare service api ([#157](https://github.com/oomol/oocana-python/issues/157)) ([9c75547](https://github.com/oomol/oocana-python/commit/9c755471cf76fb6abd3458b7b698a3a3cf65dc96))

## [0.11.4](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.3...@oomol/python-executor@0.11.4) (2024-08-20)


### Features

* support float and add some docs ([#149](https://github.com/oomol/oocana-python/issues/149)) ([16935cc](https://github.com/oomol/oocana-python/commit/16935ccc604de149310dea906e73bb1afe3f00ae))

## [0.11.3](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.2...@oomol/python-executor@0.11.3) (2024-08-20)


### Bug Fixes

* clear code cache after session end ([#146](https://github.com/oomol/oocana-python/issues/146)) ([b48ca03](https://github.com/oomol/oocana-python/commit/b48ca03929a59417343b62ba591f77cc31707c47))

## [0.11.2](https://github.com/oomol/oocana-python/compare/@oomol/python-executor@0.11.1...@oomol/python-executor@0.11.2) (2024-08-17)


### Bug Fixes

* missing some commit  ([#144](https://github.com/oomol/oocana-python/issues/144)) ([0b62b0b](https://github.com/oomol/oocana-python/commit/0b62b0b59d59d5ebcd5e85f4bf48f22cc86cd079))

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
