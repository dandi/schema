import os
import sys


def create_release(version):
    from models import Dandiset, Asset

    os.makedirs(f"releases/{version}", exist_ok=True)
    with open(f"releases/{version}/dandiset.json", "w") as fp:
        fp.write(Dandiset.schema_json(indent=2))
    with open(f"releases/{version}/asset.json", "w") as fp:
        fp.write(Asset.schema_json(indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        version = "master"
    else:
        version = sys.argv[1]
    print(f"Generating release for version: {version}")
    create_release(version)
