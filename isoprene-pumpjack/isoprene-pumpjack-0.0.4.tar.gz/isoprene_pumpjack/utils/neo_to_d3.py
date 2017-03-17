#!/usr/bin/env python
'''
Transformation of Neo4J result object into a d3 friendly dictionary.
'''


def dedupe_dict_list(duped, id_prop="id"):
    '''Dedupe a list of dicts by a dictionary property'''
    deduped = list({v[id_prop]:v for v in duped}.values())
    return deduped

def neo_node_to_d3_node(node):
    d3node = {
        "id": node.id,
        "labels": [label for label in node.labels],
        "props": {k: v for k, v in node.items()}
    }
    return d3node

def neo_link_to_d3_link(link):
    d3link = {
        "id": link.id,
        "source": link.start,
        "target": link.end,
        "labels": [link.type],
        "props": {k: v for k, v in link.items()}
    }
    return d3link

def neo_to_d3(result, nodeLabels=[], linkLabels=[]):
    '''
    Convert neo results to d3 drawable nodes/links object
    
    Takes
    * the neo result (BoltStatementResult)
    * a list of node labels (string[])
    * a list of link labels (string[])

    Dedupes to the standard format:
    {
        nodes: [
            {
                id: string,
                labels: string[],
                properties: {}
            }
        ],
        links: [
            {
                id: string,
                source: string, # id of a node
                target: string, # id of a node
                labels: string[],
                properties: {}
            }
        ]
    }
    '''
    d3data = {
        "nodes": [],
        "links": []
    }

    process_neo_objects = [
        {
            "labels": nodeLabels,
            "function": neo_node_to_d3_node,
            "d3key": "nodes"
        },
        {
            "labels": linkLabels,
            "function": neo_link_to_d3_link,
            "d3key": "links"
        }
    ]

    for record in result:
        for process in process_neo_objects:
            for label in process["labels"]:
                neo_objects = record[label]
                if isinstance(neo_objects, list):
                    for neo_object in neo_objects:
                        d3object = process["function"](neo_object)
                        d3data[process["d3key"]].append(d3object)
                else:
                    neo_object = neo_objects
                    d3object = process["function"](neo_object)
                    d3data[process["d3key"]].append(d3object)
    
            d3data[process["d3key"]] = dedupe_dict_list(d3data[process["d3key"]], "id")

    return d3data

