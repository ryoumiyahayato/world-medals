"""Check offline HTML dependencies and optionally stage them, including ignored images."""
import argparse
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = None
        if tag in {"img", "script"}:
            url = attrs.get("src")
        elif tag == "link" and attrs.get("rel") == "stylesheet":
            url = attrs.get("href")
        if url:
            self.urls.add(url)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true", help="Add referenced assets to Git")
    args = parser.parse_args()
    page = Assets()
    page.feed((ROOT / "index.html").read_text(encoding="utf-8-sig"))
    paths = set()
    errors = []
    for url in sorted(page.urls):
        parts = urlsplit(url)
        if parts.scheme == "data":
            continue
        if parts.scheme or parts.netloc:
            errors.append(f"External dependency: {url}")
            continue
        path = (ROOT / unquote(parts.path)).resolve()
        if not path.is_relative_to((ROOT / "assets").resolve()):
            errors.append(f"Dependency outside assets/: {url}")
        elif not path.is_file():
            errors.append(f"Missing dependency: {url}")
        else:
            paths.add(path.relative_to(ROOT).as_posix())
    if errors:
        raise SystemExit("\n".join(errors))
    tracked = set(subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0"))
    print(f"Checked {len(paths)} local assets; {len(paths - tracked)} not yet tracked.")
    if args.stage and paths:
        # NUL-delimited stdin avoids Windows command-length limits and path quoting issues.
        subprocess.run(
            ["git", "--literal-pathspecs", "add", "--force", "--pathspec-from-file=-", "--pathspec-file-nul"],
            cwd=ROOT, input="\0".join(sorted(paths)).encode("utf-8") + b"\0", check=True,
        )
        print("Referenced assets staged. Commit them together with index.html and its data.")


if __name__ == "__main__":
    main()
