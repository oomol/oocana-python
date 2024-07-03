import tomllib

def read_version(dir):
    file_path = dir + '/pyproject.toml'
    with open(file_path, 'rb') as f:
        data = tomllib.load(f)
        return data['project']['version']


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if not args:
        print('Usage: read_version.py <path to pyproject.toml>')
        sys.exit(1)
    print(read_version(args[0]))