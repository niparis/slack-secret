def read_version():
    with open("pyproject.toml", "r") as fout:
        data = fout.read().splitlines()

    for line in data:
        if "version" in line:
            version = line.split("=")[1].strip().strip('"')

    return version


__version__ = read_version()
