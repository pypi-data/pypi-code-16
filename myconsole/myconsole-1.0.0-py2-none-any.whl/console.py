import myconsole.embed
import IPython

def create( welcomeBanner, input, output = None, exitMessage = '' ):
    if output is None:
        output = input
    input_ = '{} '.format( input )
    output_ = '{} '.format( output )
    configuration = myconsole.embed.configuration( input_, output_ )
    ipshell = IPython.terminal.embed.InteractiveShellEmbed(
        config=configuration,
        banner1 = welcomeBanner,
        exit_msg = exitMessage )
    return ipshell
