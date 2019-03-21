#!/usr/bin/env python3
import argparse
from pathlib import Path
from saramPy import Saram, SaramInit

def main():
    parse = argparse.ArgumentParser(add_help=False)
    parse.add_argument('--init', dest='init', help='Configure Saram config file. Pass the api key')
    parse.add_argument('-l', '--local', dest='local', action='store_true', help='Dev mode. Use localhost')
    parse.add_argument('--baseurl', dest='baseurl', default=None)
    options, parser = parse.parse_known_args()

    # seperate arugment parser for init
    if options.init:
        i = SaramInit(options.init, local=options.local, base_url=options.baseurl)
        i.init()
        exit()
    # main argument parser
    else:
        parse = argparse.ArgumentParser(add_help=True)
        parse.add_argument('-t', '--token', dest='token', required=True, help='Token provided in Slack')
        parse.add_argument('-l', '--local', dest='local', action='store_true', help='Dev mode. Use localhost')
        parse.add_argument('--comment', dest='comment', default=None, help='Add an optional comment')
        
        group = parse.add_mutually_exclusive_group()
        group.add_argument('-c', '--command', dest='command', nargs=argparse.REMAINDER, help='Command to run inside quotes')
        group.add_argument('-f', '--file', dest='file', help='Read a file and send it to the server')
        
        parse.add_argument('--baseurl', dest='baseurl', default=None)
        
        args = parse.parse_args()

        if args.local:
            p = Saram(token=args.token, local=True)
        else:
            p = Saram(token=args.token, base_url=args.baseurl)
        print(p.url)
        if args.command:
            p.run_command(args.command, comment=args.comment).send_to_server()
        elif args.file:
            p.file_content(args.file, file_name=Path(args.file).parts[-1], comment=args.comment).send_to_server()


if __name__ == "__main__":
    main()