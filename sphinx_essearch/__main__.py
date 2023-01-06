import os
from pathlib import Path
import argparse


def main():
    from dotenv import load_dotenv

    DOTENV_LOADED = os.environ.get("DOTENV_LOADED")
    if not DOTENV_LOADED:
        load_dotenv(Path(os.getcwd()) / "default.env", override=True)
        load_dotenv(Path(os.getcwd()) / ".env", override=True)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--out",
        type=str,
        default=os.getenv("OUT_DIR"),
    )

    parser.add_argument(
        "--aws-host",
        dest="aws_host",
        type=str,
        default=os.getenv("AWS_HOST"),
    )
    parser.add_argument(
        "--aws-region",
        dest="aws_region",
        type=str,
        default=os.getenv("AWS_REGION"),
    )
    parser.add_argument(
        "--es-index-name",
        dest="es_index_name",
        type=str,
        default=os.getenv("ES_INDEX_NAME"),
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument(
        "--src",
        type=str,
        default=os.getenv("SRC_DIR"),
    )
    build_parser.add_argument(
        "--doctree",
        type=str,
        default=os.getenv("DOCTREE_DIR"),
    )
    build_parser.add_argument(
        "--support",
        type=str,
        default=os.getenv("SUPPORT_DIR"),
    )
    build_parser.add_argument(
        "--aws-host",
        dest="aws_host",
        type=str,
        default=os.getenv("AWS_HOST"),
    )
    build_parser.add_argument(
        "--aws-region",
        dest="aws_region",
        type=str,
        default=os.getenv("AWS_REGION"),
    )
    build_parser.add_argument(
        "--es-index-name",
        dest="es_index_name",
        type=str,
        default=os.getenv("ES_INDEX_NAME"),
    )

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument(
        "--search-html",
        dest="search_html",
        type=str,
        default=os.getenv("SEARCH_HTML"),
    )

    args = parser.parse_args()

    if args.mode == "build":
        from .build import build

        build(
            src=args.src,
            out=args.out,
            doctree=args.doctree,
            support=args.support,
            aws_host=args.aws_host,
            aws_region=args.aws_region,
            es_index_name=args.es_index_name,
        )

    elif args.mode == "preview":
        from .preview import preview

        preview(
            out=args.out,
            aws_host=args.aws_host,
            aws_region=args.aws_region,
            es_index_name=args.es_index_name,
            search_html=args.search_html,
        )


if __name__ == "__main__":
    main()
