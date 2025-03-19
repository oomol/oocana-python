# path

when run package in layer mode, package will be added to python's search path, so the task block can use module under root package.

```shell
# file struct in package 
├── a.py
└── tasks
    └── python-a
```

python-a task block can import a module in package.

```python
from a import *
```

this behavior is only available in layer mode.