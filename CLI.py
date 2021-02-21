import backend


def main():
    args = backend.argparse_setup().parse_args()
    backend.logging_setup()
    backend.languagepod101(args)


if __name__ == "__main__":
    main()
