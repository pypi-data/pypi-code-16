"""
Invokes webhooks.py when is webhooks module is run as a script.
Example: python -m webhooks config.yml
"""

from .main import main


if __name__ == "__main__":
    main()
