import tastyapi
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-gu', '--get_user', help='Query information on a specific user', type=str)
    parser.add_argument('-gi', '--get_image', help='Query for random image based on keyword.', type=str)
    parser.add_argument('-gs', '--get_staff', help='Query for list of staff', action='store_true')
    parser.add_argument('-ns', '--node_status', help='Query for status of nodes', action='store_true')
    parser.add_argument('-ss', '--server_status', help='Query for status of servers', action='store_true')
    parser.add_argument('-ts', '--teamspeak_status', help='Query for Teamspeak status', action='store_true')
    parser.add_argument('-ri', '--random_image', help='Query for random image', action='store_true')
    parser.add_argument('-j', '--json', help='Return unformatted JSON', action='store_true')
    args = parser.parse_args()

    if args.get_user:
        if args.json:
            return tastyapi.get_user(args.get_user)
        return tastyapi.get_user(args.get_user)
    elif args.get_image:
        return tastyapi.get_image(args.get_image)
    elif args.get_staff:
        if args.json:
            return tastyapi.get_staff()
        return tastyapi.get_staff()
    elif args.node_status:
        return tastyapi.node_status()
    elif args.server_status:
        return tastyapi.server_status()
    elif args.teamspeak_status:
        return tastyapi.teamspeak_status()
    elif args.random_image:
        return tastyapi.random_image()
