import IPython.terminal.prompts
from IPython.terminal.prompts import Token
import traitlets.config.loader

def configuration( input, output ):
    class CustomPrompt( IPython.terminal.prompts.Prompts ):
        def in_prompt_tokens(self, cli=None):
            return [ (Token.Prompt, input ),
                    (Token.PromptNum, str(self.shell.execution_count)),
                    (Token.Prompt, ': '), ]

        def out_prompt_tokens(self):
            return [ (Token.OutPrompt, output ),
                     (Token.OutPromptNum, str(self.shell.execution_count)),
                     (Token.OutPrompt, ': '), ]

    config = traitlets.config.loader.Config()
    config.TerminalInteractiveShell.prompts_class=CustomPrompt
    return config
