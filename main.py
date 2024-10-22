from .main_parser import *
from sys import argv


def main(args):
    if args[1] == "kucoin":
        if args[2] == "start":
            parser_kucoin()
    
    elif args[1] == "market":
        if args[2] == "start":
            parser_marketcap()

    elif args[1] == "start_nan":
        handler_dataset_nan(args[2])

    elif args[1] == "print_nan":
        print_stat_nan(args[2])

    elif args[1] == "web":
        pass


if __name__ == "__main__":
    main(argv)