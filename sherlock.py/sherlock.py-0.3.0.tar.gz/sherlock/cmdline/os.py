import os
from cmdline import cmdline

@cmdline("""
function is_su() {
    return is_su
}
""")
def is_su():
    return os.geteuid() is 0
