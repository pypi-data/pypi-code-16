# match.py
## matches teams to opponents
## and/or players into teams

# imports
import copy
from networkx import Graph, max_weight_matching
from kuhn_munkres import Cost, Matrix

# functions
def make_entity_list(entities):
    entity_list, mappings = list(), list()
    i = 0
    for entity in entities:
        count = entities[entity]['count']
        mappings += ([entity,] * count)
        entity_list += range(i, i+count)
        i += count
    return entity_list, mappings

def process_pairs(matchings, mappings):
    processed, results = set(), set()
    for team in matchings:
        opp = matchings[team]
        if (team not in processed and opp not in processed):
            results.add((mappings[team], mappings[opp]))
            processed.update([team, opp])
    return results

def pair_teams(teams, score_fn):
    """
    generates optimal team pairings
    :param teams: a dictionary of teams, with teams[teamID]
      returning a dictionary with 'rating', 'count', and 'conflicts',
      teams[teamID]['count'] as an nonnegative integer,
      and teams[teamID]['conflicts'] as a list of team ID's
    :param score_fn: a function that, given two ratings,
      returns a nonnegative score such that higher scores are better,
      e.g.: abs(.5 - p(rating_1 beats rating_2))
      score_fn should be commutative
    :return: team pairings (using ID's)
    :rtype: set of tuples
    """
    team_list, mappings = make_entity_list(teams)
    team_graph = Graph()
    team_graph.add_nodes_from(team_list)
    for i in xrange(len(team_list)):
        team, added = team_list[i], set()
        team_ID = mappings[team]
        for opp in team_list[(i+1):]: # prior teams already connected
            opp_ID = mappings[opp]
            if opp_ID in added: continue # skip all but first
            if (opp_ID is not team_ID and
                opp_ID not in teams[team_ID]['conflicts'] and
                team_ID not in teams[opp_ID]['conflicts']):
                weight = score_fn(teams[team_ID]['rating'],
                                  teams[opp_ID]['rating'])
                added.add(opp_ID)
                team_graph.add_edge(team, opp, weight=weight)
    max_matchings = max_weight_matching(team_graph, True)
    return process_pairs(max_matchings, mappings)

def pair_players(players, score_fn):
    """
    generates optimal player pairings
    :param players: a dictionary of players, with players[playerID]
      returning a dictionary with 'rating', 'count', and 'conflicts',
      players[playerID]['count'] as an nonnegative integer,
      and players[playerID]['conflicts'] as a list of player ID's
    :param score_fn: a function that, given two ratings,
      returns a nonnegative score such that higher scores are better,
      e.g.: abs(.5 - p(rating_1 beats rating_2))
      score_fn should be commutative
    :return: player pairings (using ID's)
    :rtype: set of tuples
    """
    return pair_teams(players, score_fn)

def group_teams(teams, score_fn, game_size):
    """
    attempts to generate optimal team groupings
    :param teams: a dictionary of teams, with teams[teamID]
      returning a dictionary with 'rating', 'count', and 'conflict',
      teams[teamID]['count'] as a nonnegative integer
      representing the maximum number of games to make with that team,
      and teams[teamID]['conflicts'] as a list of team ID's
    :param score_fn: a function that, given an arbitrary number of
      ratings, returns a score such that higher scores
      are preferable, e.g. a measure of variance
      score_fn should be commutative and associative
    :param game_size: number of teams per game
    :return: team groupings (using ID's)
    :rtype: set of tuples
    """
    if (game_size < 2):
        return set([(team,) for team in teams])
    elif (game_size == 2):
        return pair_teams(teams, score_fn)
    mappings = make_entity_list(teams)[1]
    remains = copy.copy(mappings)
    counts = dict()
    for team in teams:
        counts[team] = 0
    groupings = set()
    for team in mappings:
        if counts[team] >= teams[team]['count']: continue
        current = [team,]
        for i in xrange(game_size-1):
            remaining = [t for t in remains if
                         (t not in current and
                          tuple(sorted(current + [t,]))
                          not in groupings)]
            for teamID in  current:
                remaining = [t for t in remaining if
                             (t not in teams[teamID]['conflicts'] and
                              teamID not in teams[t]['conflicts'])]
            if len(remaining) == 0: break
            remaining.sort(key=lambda x:
                           score_fn(teams[x]['rating'],
                           *[teams[t]['rating'] for t in current]))
            current.append(remaining[0])
        if len(current) < game_size: continue
        for i in xrange(len(current)):
            counts[current[i]] += 1
            remains.remove(current[i])
        groupings.add(tuple(sorted(current)))
    return groupings

def group_players(players, score_fn, team_size):
    """
    attempts to generate optimal player groupings
    :param players: a dictionary of players, with players[playerID]
      returning a dictionary with 'rating', 'count', and 'conflict',
      players[playerID]['count'] as a nonnegative integer
      representing the number of teams to make with that player,
      and players[playerID]['conflicts'] as a list of player ID's
    :param score_fn: a function that, given an arbitrary number of
      ratings, returns a score such that higher scores
      are preferable, e.g. a measure of variance
      score_fn should be commutative and associative
    :param team_size: number of players per team
    :return: player groupings (using ID's)
    :rtype: set of tuples
    """
    return group_teams(players, score_fn, team_size)

def process_assignments(assignments, match_map, temp_map,
                         matchings):
    results = set()
    for match, temp in assignments: # unpack tuple
        if (match >= len(match_map) or
            temp >= len(temp_map)): continue
        match_ID, temp_ID = match_map[match], temp_map[temp]
        if temp_ID in matchings[match_ID].get('conflicts', dict()):
            continue
        results.add((match_ID, temp_ID))
    return results

def assign_templates(matchings, templates):
    """
    given game matchings and templates, provides optimal template assignments
    :param matchings: a dictionary that maps matching tuples to another
      dictionary containing each matching's
      'count' (maximum # of games to be created with this pairing),
      'scores' (a dictionary mapping template ID's to the scores
                this pairing has for that template; default 0),
      and 'conflicts' (a set containing ID's of templates
                       this pairing cannot play on)
    :param templates: a dictionary mapping template ID's to another
      dictionary containing each template's
      'count' (maximum # of games to be created with this template)
    :return: matchings-template pairings
    :rtype: set of tuples
    """
    match_list, match_map = make_entity_list(matchings)
    temp_list, temp_map = make_entity_list(templates)
    array = list()
    for match in match_list:
        match_row = list()
        match_ID, added = match_map[match], set()
        scores = matchings[match_ID].get('scores', dict())
        conflicts = matchings[match_ID].get('conflicts', dict())
        for temp in temp_list:
            temp_ID = temp_map[temp]
            if (temp_ID in added or
                temp_ID in conflicts):
                score = Cost(1, 0)
            else:
                score = Cost(0, scores.get(temp_ID, 0))
            match_row.append(score)
        array.append(match_row)
    assignments = Matrix(array).solve()
    return process_assignments(assignments, match_map, temp_map,
                                matchings)
