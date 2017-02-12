"""Elo ratings from Challonge tournament results.

Usage: challonge2elo <tournament>... [--current=<path>] [--out=<path>]

Arguments:
  <tournament>  Tournament ID (e.g., 'foo' for challonge.com/foo, or
                'foo-bar' for foo.challonge.com/bar).

Options:
  -h --help         Show this screen.
  --current=<path>  Current ratings [default: ratings.json].
  --out=<path>      Output file [default: ratings.csv].

"""
import csv
import json
import os

import docopt
import elo
import requests

CHALLONGE_USERNAME = os.getenv('CHALLONGE_USERNAME')
CHALLONGE_API_KEY = os.getenv('CHALLONGE_API_KEY')


def get_current_ratings(filename):
    """Read the current ratings from a file or create new ratings."""
    if os.path.isfile(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return []


def get_tournament(tid, username, api_key):
    """Retrieve a tournament record from Challonge."""
    url = 'https://api.challonge.com/v1/tournaments/{0}.json'.format(tid)
    params = {'include_participants': 1, 'include_matches': 1}
    auth = (username, api_key)

    request = requests.get(url, params=params, auth=auth)
    return request.json()['tournament']


def map_ids_to_names(participants):
    """Map tournament participants' IDs to their names."""
    ids_to_names = {}
    for p in participants:
        participant = p['participant']
        participant_id = participant['id']
        participant_name = participant['name']

        ids_to_names[participant_id] = participant_name

        # Participants have different IDs during the group stage.
        group_player_ids = participant['group_player_ids']
        if group_player_ids:
            group_player_id = group_player_ids[0]

            ids_to_names[group_player_id] = participant_name

    return ids_to_names


def get_player(ratings, name):
    """Get a player from the ratings by name."""
    for player in ratings:
        if player['name'].lower() == name.lower():
            return player

    new_player = {'name': name, 'rating': elo.INITIAL}
    ratings.append(new_player)

    return new_player


def update_ratings(ratings, matches, ids_to_names):
    """Update players' ratings based on match outcomes."""
    for m in matches:
        match = m['match']
        loser_id = match['loser_id']
        winner_id = match['winner_id']

        loser_name = ids_to_names[loser_id]
        winner_name = ids_to_names[winner_id]

        loser = get_player(ratings, loser_name)
        loser_rating = loser['rating']

        winner = get_player(ratings, winner_name)
        winner_rating = winner['rating']

        winner['rating'], loser['rating'] = elo.rate_1vs1(winner_rating,
                                                          loser_rating)


def output_json(ratings, filename):
    """Write the ratings to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(ratings, f, indent=4)
        f.write('\n')


def output_csv(ratings, filename):
    """Write the ratings to a CSV file."""
    with open(filename, 'w') as f:
        writer = csv.writer(f)

        header = ['Rank', 'Player', 'Rating']
        writer.writerow(header)

        for i, player in enumerate(ratings):
            rank = i + 1
            name = player['name']
            rating = player['rating']

            row = [rank, name, rating]
            writer.writerow(row)


def main():
    """Update and output the ratings."""
    args = docopt.docopt(__doc__)

    tournament_ids = args['<tournament>']
    current_ratings_filename = args['--current']
    output_filename = args['--out']

    ratings = get_current_ratings(current_ratings_filename)

    username = CHALLONGE_USERNAME
    api_key = CHALLONGE_API_KEY

    for tournament_id in tournament_ids:
        tournament = get_tournament(tournament_id, username, api_key)
        participants = tournament['participants']
        matches = tournament['matches']

        ids_to_names = map_ids_to_names(participants)
        update_ratings(ratings, matches, ids_to_names)

    ratings.sort(key=lambda k: k['rating'], reverse=True)
    output_json(ratings, current_ratings_filename)
    output_csv(ratings, output_filename)


if __name__ == '__main__':
    main()
