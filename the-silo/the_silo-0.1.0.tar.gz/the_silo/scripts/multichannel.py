import os
import math

def shuffle():
    """
    For either selected read nodes in the compositing script, shuffle out all channels contained and create a write node for each channel.
    """
    import nuke
    for read in nuke.selectedNodes():
        if read.Class() != 'Read':
            continue
        shuffles = []
        for layer in nuke.layers(read):
            shuffle = nuke.nodes.Shuffle(name='shuffle_{0}'.format(layer), inputs=[read])
            shuffle['in'].setValue(layer)
            shuffle['alpha'].setValue('black')
            shuffles.append(shuffle)
            write = nuke.nodes.Write(name='write_{0}'.format(layer), inputs=[shuffle])
            write['channels'].setValue('rgb')
            write['file'].setValue('{0}.{1}.exr'.format(read['file'].value().replace('.exr', ''), layer))
            write['file_type'].setValue('exr')
            write['datatype'].setValue('16 bit half')
            write['compression'].setValue('Zip (1 scanline)')
            write['reading'].setValue(True)
        contact = nuke.nodes.ContactSheet(inputs=shuffles)
        contact['width'].setValue(4096)
        contact['height'].setValue(4096)
        sqrt = math.ceil(math.sqrt(len(shuffles)))
        contact['rows'].setValue(sqrt)
        contact['columns'].setValue(sqrt)
        c_write = nuke.nodes.Write(name='write_{0}_contact_sheet'.format(layer), inputs=[contact])
        c_write['channels'].setValue('rgb')
        c_write['file'].setValue('{0}.ContactSheet.exr'.format(read['file'].value().replace('.exr', '')))
        c_write['file_type'].setValue('exr')
        c_write['datatype'].setValue('16 bit half')
        c_write['compression'].setValue('Zip (1 scanline)')
        c_write['reading'].setValue(True)


def create():
    """
    For a selected group of read nodes from the same rendering process (i.e.
    same naming pattern, using "." as a separator for Render Elements), create
    a multichannel EXR.
    """
    def is_number(value):
        """
        Check if a value is a number by trying to cast it as an integer

        :param value: Input value to check
        :type: any
        """
        try:
            int(value)
            return True
        except ValueError:
            return False

    import nuke
    if not nuke.selectedNodes():
        return
    passes = []
    rgba = None
    for node in nuke.selectedNodes():
        if node.Class() != 'Read':
            continue
        fp_base = os.path.basename(node['file'].value())
        split_vals = fp_base.split('.')
        if len(split_vals) > 2 and not is_number(split_vals[-2]):
            passes.append(node)
        else:
            rgba = node
    last_copy = None
    for pass_read in sorted(passes, key=lambda x:
        os.path.basename(x['file'].value()).split('.')[-2].lower()):
        pass_name = os.path.basename(pass_read['file'].value()).split('.')[-2]
        nuke.Layer(pass_name, ['{0}.red'.format(pass_name),
                               '{0}.green'.format(pass_name),
                               '{0}.blue'.format(pass_name)])
        if not last_copy:
            copy = nuke.nodes.Copy(name='copy_{0}'.format(pass_name),
                                   inputs=[rgba, pass_read])
            copy['from0'].setValue('red')
            copy['to0'].setValue('{0}.red'.format(pass_name))
            copy['from1'].setValue('green')
            copy['to1'].setValue('{0}.green'.format(pass_name))
            copy['from2'].setValue('blue')
            copy['to2'].setValue('{0}.blue'.format(pass_name))
            copy['from3'].setValue('none')
            copy['to3'].setValue('none')
            last_copy = copy
        else:
            copy = nuke.nodes.Copy(name='copy_{0}'.format(pass_name),
                                   inputs=[last_copy, pass_read])
            copy['from0'].setValue('red')
            copy['to0'].setValue('{0}.red'.format(pass_name))
            copy['from1'].setValue('green')
            copy['to1'].setValue('{0}.green'.format(pass_name))
            copy['from2'].setValue('blue')
            copy['to2'].setValue('{0}.blue'.format(pass_name))
            copy['from3'].setValue('none')
            copy['to3'].setValue('none')
            last_copy = copy
    write = nuke.nodes.Write(name='multichannel_write', inputs=[last_copy])
    write['channels'].setValue('all')
    write['file_type'].setValue('exr')
    write['datatype'].setValue('16 bit half')
    write['compression'].setValue('Zip (1 scanline)')
    write['file'].setValue(rgba['file'].value().replace('.exr',
                                                        '_multichannel.exr'))
