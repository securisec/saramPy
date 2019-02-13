#!/usr/bin/env python3
import argparse
from saram import Saram

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('-t', dest='token', required=True, help='Token provided in Slack')
    parse.add_argument('-u', dest='slack_user', required=True, help='Slack username')
    parse.add_argument('-n', dest='name', default=None, help='Name of the file')
    parse.add_argument('-l', dest='local', action='store_true', help='Dev mode. Use localhost')
    
    group = parse.add_mutually_exclusive_group()
    group.add_argument('-c', dest='command', nargs=argparse.REMAINDER, help='Command to run inside quotes')
    group.add_argument('-f', dest='file', help='Read a file and send it to the server')
    
    args = parse.parse_args()

    if args.local:
        p = Saram(token=args.token, user=args.slack_user, local=True)
    else:
        p = Saram(token=args.token, user=args.slack_user)
    print(p.url)
    if args.command:
        p.run_command(args.command).send_to_server()
    elif args.file:
        p.file_content(args.file, file_name=args.name).send_to_server()


if __name__ == "__main__":
    main()