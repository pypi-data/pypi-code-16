from .ninja_def import ninja_def
from .ninja_io import ninja_io
from .ninja_build_pipe import ninja_build_pipe


def ninja_build(tasks):
    """Return the Ninja build section

    Args:
        tasks (list): a list of task dictionaries
    Returns:
        a string
    """
    output = []
    for t in tasks:
        item = "build {0}{1}: {2} {3}{4}{5}".format(
                    ninja_io(t['out']),
                    ninja_build_pipe(t, "out|"),
                    t['rule'],
                    ninja_io(t.get('in', '')),
                    ninja_build_pipe(t, "dep|"),
                    ninja_build_pipe(t, "dep||")
                )
        if 'def' in t:
            output.append("{}\n{}".format(
                    item,
                    ninja_def(t['def'], "  "))
                )
        else:
            output.append(item)
    return "\n\n".join(output)
