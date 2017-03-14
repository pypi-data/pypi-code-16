"""Create SimC permutations based on in_file file."""
import itertools
import configparser


def simperm_create(in_file, multi_enemy=False):
    """Create the SimC permutations.

    Args:
        in_file: file content based on the SimPermut WoW Addon output.
        multi_enemy: add multiple enemies (currently 4) to each permuation (Default: False).

    Returns:
        int, str: amount of permutations and the permuations in form of str array of str arrays

    """
    config = configparser.ConfigParser()
    config.read(in_file)

    data = []
    # key must match SimPermuts AutoSimC export
    c = config['Gear']
    # keys must match the names SimC expects
    keys = [
        'head', 'neck', 'shoulder', 'back', 'chest'
        , 'wrist', 'hands', 'waist', 'legs', 'feet'
        , 'finger1', 'finger2'
        , 'trinket1', 'trinket2'
        , 'main_hand', 'off_hand'
    ]

    # create array set for itertools.product
    for key in iter(keys):
        # extra case for rings& trinkets
        if key == 'finger1' or key == 'trinket1':
            a = c.get(key).split('|')
            b = a[:len(a) // 2]
            data.append(b)
        elif key == 'finger2' or key == 'trinket2':
            a = c.get(key).split('|')
            b = a[len(a) // 2:]
            data.append(b)
        else:
            data.append(c.get(key).split('|'))

    # GENERATE output string
    #
    output_string = []
    counter = 0
    for r in itertools.product(*data):

        # TOP part
        #
        output = []
        for el in iter(config['Profile']):
            # we have some special cases we need to handle ... no clue
            # why naming is not consistent between simpermut& simc
            if el == 'profilename':
                # key 'profilename' becomes value of key class + iterator
                output.append("%s=%s_%s" % (config.get('Profile', 'class'), config.get('Profile', el), counter))
            elif el == 'spec':
                # rename spec into specialization
                output.append(f"specialization={config.get('Profile', el)}")
            elif el == 'class':
                # ignore 'class'
                pass
            elif el == 'profileid':
                # ignore 'profileid'
                pass
            elif el == 'profilename':
                # ignore 'profilename'
                pass
            elif el == 'other':
                # ignore 'profilename'
                pass
            else:
                output.append(f"{el}={config.get('Profile', el)}")

        # ITEMS part
        #
        for idx, el in enumerate(keys):
            # strip 'L' if it is there
            if r[idx].startswith('L'):
                s = str(r[idx])[1:]
            else:
                s = r[idx]
            output.append(f"{el}={s}")

        # ENEMYS
        #
        if multi_enemy:
            output.append("enemy=Fluffy_Pillow")
            output.append("enemy=enemy2")
            output.append("enemy=enemy3")
            output.append("enemy=enemy4")

        output_string.append(output)
        counter += 1

    return [counter, output_string]
