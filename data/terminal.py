from sys import platform as sys_platform, stdin as sys_stdin, stdout as sys_stdout
from shlex import split as shlex_split
from os.path import exists

if sys_platform.startswith('win'):
    import msvcrt

    def _getch():
        ch = msvcrt.getch()
        return ch.decode('utf-8', 'ignore') if isinstance(ch, bytes) else ch
else:
    import tty, termios

    def _getch():
        fd = sys_stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys_stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class Terminal():
    RED = '\033[31m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    DIM = '\033[2m'

    def __init__(self, commands=None, prompt='COCLI > ', history_ignore=[]):
        self.COMMANDS = commands or []
        self.history_ignore = history_ignore
        # Prepare easy access dict for command info by name
        self.args_info = {cmd['name']: cmd for cmd in self.COMMANDS}
        self.prompt = prompt
        self.history = self.history_file(1)
        self.history_index = None
        self.user_input = ''
        self._last_hint_lines_printed = 0

    def history_file(self, option, data=''):
        if not exists('.history'):
            open('.history', 'w').close()
        if option == 1:
            return open('.history').read().splitlines()
        elif option == 2:
            with open('.history', 'a') as f:
                f.write(data)
        elif option == 3:
            with open('.history', 'w') as f:
                f.write(data)

    def clear_line(self):
        sys_stdout.write('\r\033[K')

    def clear_previous_hint(self):
        for _ in range(self._last_hint_lines_printed):
            sys_stdout.write('\033[F')
            self.clear_line()
        self._last_hint_lines_printed = 0

    def print_hint_line(self, hint):
        self.clear_previous_hint()
        if hint:
            sys_stdout.write(self.DIM + hint + self.RESET + '\n')
            self._last_hint_lines_printed = hint.count('\n') + 1
        else:
            sys_stdout.write('\n')
            self._last_hint_lines_printed = 1

    def print_prompt(self):
        self.clear_line()
        suggestion = ''
        hint = ''
        color = self.RED

        stripped = self.user_input.rstrip()
        parts = stripped.split(maxsplit=1)
        cmd_part = parts[0] if parts else ''

        if self.user_input and ' ' not in self.user_input:
            matches = [c['name'] for c in self.COMMANDS if c['name'].startswith(self.user_input) and c['name'] != self.user_input]
            if matches:
                shortest = min(matches, key=len)
                suggestion = shortest[len(self.user_input):]
                color = self.RED

        elif cmd_part in self.args_info:
            cmd_info = self.args_info[cmd_part]
            hint_lines = [cmd_info.get('desc', '')]

            args = cmd_info.get('args', {})
            if args:
                hint_lines.append('Arguments:')
                arg_texts = []
                max_len = 0
                for arg_name, arg_data in args.items():
                    arg_type = arg_data.get('type')
                    if arg_type == 'flag':
                        prefix = '\033[38;5;196m[flag]\033[0m '
                        display_name = arg_name
                    else:
                        prefix = '\033[38;5;46m[value]\033[0m'
                        display_name = arg_name + '=str'
                    text = prefix + display_name
                    arg_texts.append((text, arg_data.get('desc', '')))
                    if len(text) > max_len:
                        max_len = len(text)

                for text, desc in arg_texts:
                    padded_text = text.ljust(max_len + 2)
                    hint_lines.append(f'  {padded_text}{desc}')

            hint = '\n'.join(hint_lines)

            after_cmd = stripped[len(cmd_part):].lstrip()
            arg_parts = after_cmd.split()
            if arg_parts:
                last_arg = arg_parts[-1]
                if '=' not in last_arg:
                    matches = [a for a in args if a.startswith(last_arg)]
                    if matches:
                        shortest = min(matches, key=len)
                        suggestion = shortest[len(last_arg):]
                        color = self.BLUE

        self.print_hint_line(hint)
        sys_stdout.write(self.prompt + self.user_input)
        if suggestion:
            sys_stdout.write(color + suggestion + self.RESET)
        sys_stdout.flush()

    def run(self):
        self.user_input = ''
        self.history_index = None
        self.print_prompt()

        while True:
            ch = _getch()

            if ch in ('\r', '\n'):
                self.clear_previous_hint()
                self.clear_line()
                print()
                line = self.user_input
                self.user_input = ''
                self.history_index = None
                return line

            elif ch in ('\x7f', '\b'):
                self.user_input = self.user_input[:-1]
                self.print_prompt()

            elif ch == '\x1b':
                next1 = _getch()
                next2 = _getch()
                if next1 == '[':
                    if next2 == 'A' and self.history:
                        if self.history_index is None:
                            self.history_index = len(self.history) - 1
                        elif self.history_index > 0:
                            self.history_index -= 1
                        self.user_input = self.history[self.history_index]
                        self.print_prompt()
                    elif next2 == 'B' and self.history_index is not None:
                        if self.history_index < len(self.history) - 1:
                            self.history_index += 1
                            self.user_input = self.history[self.history_index]
                        else:
                            self.history_index = None
                            self.user_input = ''
                        self.print_prompt()

            elif ch == '\t':
                parts = self.user_input.split(maxsplit=1)
                cmd_part = parts[0] if parts else ''

                if len(parts) == 1 and self.user_input:
                    matches = [c['name'] for c in self.COMMANDS if c['name'].startswith(self.user_input)]
                    if matches:
                        self.user_input = min(matches, key=len)
                else:
                    if cmd_part in self.args_info:
                        args = self.args_info[cmd_part].get('args', {})
                        after_cmd = self.user_input[len(cmd_part):].lstrip()
                        arg_parts = after_cmd.split()
                        if arg_parts:
                            last_arg = arg_parts[-1]
                            if '=' not in last_arg:
                                matches = [a for a in args if a.startswith(last_arg)]
                                if matches:
                                    completed = min(matches, key=len)
                                    arg_parts[-1] = completed
                                    self.user_input = cmd_part + ' ' + ' '.join(arg_parts)

                self.print_prompt()

            elif ch.isprintable():
                self.user_input += ch
                self.history_index = None
                self.print_prompt()

    def parse_command(self, line):
        try:
            parts = shlex_split(line)
        except ValueError:
            parts = line.strip().split()

        if not parts:
            return '', {}

        cmd = parts[0]
        args = {}
        cmd_info = self.args_info.get(cmd, {})
        cmd_args = cmd_info.get('args', {})

        for part in parts[1:]:
            if '=' in part:
                key, val = part.split('=', 1)
                args[key.strip()] = val.strip()
            else:
                # If argument is a flag type, set True, else treat as value with empty string
                if part in cmd_args and cmd_args[part].get('type') == 'flag':
                    args[part] = True
                else:
                    args[part] = part  # or True? depends on usage

        # Save history if command not ignored
        if (len(self.history) == 0 or self.history[-1] != line) and cmd not in self.history_ignore:
            self.history.append(line)
            self.history_file(2, line+'\n')

        return cmd, args
