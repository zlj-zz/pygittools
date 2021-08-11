import sys
from pprint import pprint

sys.path.insert(0, ".")

from pigit import Git_Cmds
from pigit.shell_completion import ShellCompletion


def test_generater():
    for item in ShellCompletion.Supported_Shell:
        print(item)
        s = ShellCompletion(
            {key: value.get("help", "") for key, value in Git_Cmds.items()},
            shell=item,
            script_dir=".",
        )
        pprint(s.generate_resource())
