# -*- coding:utf-8 -*-

from __future__ import print_function
import random

from ..utils import run_cmd, color_print, confirm, similar_command
from ..str_utils import shorten
from ..common import Fx, Color, TermColor, Emotion
from .interaction import InteractiveAdd, TermError
from .cmds import Git_Cmds, CommandType


class GitProcessor(object):
    """Git short command processor."""

    def __init__(
        self, extra_cmds=None, use_recommend=True, show_original=True, **kwargs
    ):
        super(GitProcessor, self).__init__()

        self.use_recommend = use_recommend
        self.show_original = show_original

        self.cmds = Git_Cmds
        self.cmds.update(
            {
                "i": {
                    "belong": CommandType.Index,
                    "command": InteractiveAdd(
                        use_color=kwargs.get("use_color", True),
                        help_wait=kwargs.get("help_wait", 1.5),
                    ).add_interactive,
                    "help": "interactive operation git tree status.",
                    "type": "func",
                },
                "shell": {
                    "command": "",
                    "help": "Into PIGIT shell mode.",
                },  # only for tips.
            }
        )

        if extra_cmds:
            if not isinstance(extra_cmds, dict):
                raise TypeError("Custom cmds must be dict.")
            self.cmds.update(extra_cmds)

    @staticmethod
    def color_command(command):
        # type:(str) -> str
        """Color the command string.
        prog: green;
        short command: yellow;
        arguments: skyblue;
        values: white.

        Args:
            command(str): valid command string.

        Returns:
            (str): color command string.
        """

        command_list = command.split(" ")
        color_command = (
            Fx.bold
            + TermColor.DeepGreen
            + command_list.pop(0)
            + " "
            + TermColor.Yellow
            + command_list.pop(0)
            + " "
            + Fx.unbold
            + Fx.italic
            + TermColor.SkyBlue
        )
        while len(command_list) > 0:
            temp = command_list.pop(0)
            if temp.startswith("-"):
                color_command += temp + " "
            else:
                break

        color_command += Fx.reset
        if len(command_list) > 0:
            color_command += " ".join(command_list)

        return color_command

    def process_command(self, _command, args=None):
        # type:(str, list|tuple) -> None
        """Process command and arguments.

        Args:
            _command (str): short command string
            args (list|None, optional): command arguments. Defaults to None.

        Raises:
            SystemExit: not git.
            SystemExit: short command not right.
        """

        option = self.cmds.get(_command, None)

        # Invalid, if need suggest.
        if option is None:
            print("Don't support this command, please try ", end="")
            color_print("g --show-commands", TermColor.Gold)

            if self.use_recommend:  # check config.
                predicted_command = similar_command(_command, self.cmds.keys())
                if confirm(
                    "%s The wanted command is %s ?[y/n]:"
                    % (
                        Emotion.Icon_Thinking,
                        TermColor.Green + predicted_command + Fx.reset,
                    )
                ):
                    self.process_command(predicted_command, args=args)

            return

        command = option.get("command", None)
        # Has no command can be executed.
        if not command:
            color_print(
                "Invalid custom short command, nothing can to exec.", TermColor.Red
            )
            return

        if not option.get("has_arguments", False):
            if args:
                color_print(
                    "The command does not accept parameters. Discard {0}.".format(args),
                    TermColor.Red,
                )
                args = []

        _type = option.get("type", "string")
        if _type == "func":
            try:
                command(args)
            except TermError as e:
                color_print(str(e), TermColor.Red)
        else:  # is string.
            if args:
                args_str = " ".join(args)
                command = " ".join([command, args_str])
            if self.show_original:
                print(
                    "{0}  {1}".format(
                        Emotion.Icon_Rainbow, self.color_command(command)
                    ),
                )
            run_cmd(command)

    ################################
    # Print command help message.
    ################################
    def _generate_help_by_key(self, _key, use_color=True):
        # type:(str, bool) -> str
        """Generate one help by given key.

        Args:
            _key (str): Short command string.
            use_color (bool, optional): Wether color help message. Defaults to True.

        Returns:
            (str): Help message of one command.
        """

        _msg = "    {key_color}{:<9}{reset}{}{command_color}{}{reset}"
        if use_color:
            _key_color = TermColor.Green
            _command_color = TermColor.Gold
        else:
            _key_color = _command_color = ""

        # Get help message and command.
        _help = self.cmds[_key].get("help", "")
        _command = self.cmds[_key]["command"]

        # Process help.
        _help = _help + "\n" if _help else ""

        # Process command.
        if callable(_command):
            _command = "Callable: %s" % _command.__name__

        _command = shorten(_command, 70, placeholder="...")
        _command = " " * 13 + _command if _help else _command

        # Splicing and return.
        return _msg.format(
            _key,
            _help,
            _command,
            key_color=_key_color,
            command_color=_command_color,
            reset=Fx.reset,
        )

    def command_help(self):
        """Print help message."""
        print("These are short commands that can replace git operations:")
        for key in self.cmds.keys():
            msg = self._generate_help_by_key(key)
            print(msg)

    def command_help_by_type(self, command_type):
        """Print a part of help message.

        Print the help information of the corresponding part according to the
        incoming command type string. If there is no print error prompt for the
        type.

        Args:
            command_type (str): A command type of `TYPE`.
        """

        # Process received type.
        command_type = command_type.capitalize().strip()

        # Checking the type wether right.
        if command_type not in CommandType.__members__:
            color_print("There is no such type.", TermColor.Red)
            print("Please use `", end="")
            color_print("g --types", TermColor.Green, end="")
            print(
                "` to view the supported types.",
            )
            if self.use_recommend:
                predicted_type = similar_command(
                    command_type, CommandType.__members__.keys()
                )
                if confirm(
                    "%s The wanted type is %s ?[y/n]:"
                    % (
                        Emotion.Icon_Thinking,
                        TermColor.Green + predicted_type + Fx.reset,
                    )
                ):
                    self.command_help_by_type(predicted_type)
            return

        # Print help.
        print("These are the orders of {0}".format(command_type))
        for k, v in self.cmds.items():
            belong = v.get("belong", CommandType.Extra)
            # Prevent the `belong` attribute from being set in the custom command.
            if isinstance(belong, CommandType) and belong.value == command_type:
                msg = self._generate_help_by_key(k)
                print(msg)

    @classmethod
    def type_help(cls):
        """Print all command types with random color."""
        for member in CommandType:
            print(
                "{0}{1}  ".format(
                    Color.fg(
                        random.randint(70, 255),
                        random.randint(70, 255),
                        random.randint(70, 255),
                    ),
                    member.value,
                ),
                end="",
            )
        print(Fx.reset)
