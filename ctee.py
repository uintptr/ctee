#!/usr/bin/env python3

import sys
import os
import re
import io

from typing import Optional

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, NONE, DROP = range(10)

colors = ["BLACK",
          "RED",
          "GREEN",
          "YELLOW",
          "BLUE",
          "MAGENTA",
          "CYAN",
          "WHITE",
          "NONE",
          "DROP"]


def console_print(text: str, color: int = WHITE):
    text = "\x1b[1;%dm" % (30 + color) + text + "\x1b[0m"
    print(text)


def parse_config(conf_file: str) -> tuple[list[str], dict[str, int]]:

    strings: list[str] = []
    color_map: dict[str, int] = {}

    print("[+] parsing {}".format(conf_file))

    if (True == os.path.isfile(conf_file)):
        with open(conf_file, "r") as f:
            for line in f:
                line = line.strip("\r\n")
                if (True == line.startswith('#') or
                        0 == len(line)):
                    continue
                (s, c) = line.split('=')

                color = c.strip(' ')
                string = re.sub('" *', '', s)

                strings.append(string)

                color_map[string] = colors.index(color)

    return (strings, color_map)


def read_loop(out_fd: Optional[io.IOBase] = None):

    config_file = None
    home_conf_file = os.path.expanduser("~/.ctee.conf")
    sxs_conf_filr = os.path.abspath("ctee.conf")

    if (True == os.path.exists(home_conf_file)):
        config_file = home_conf_file
    elif (True == os.path.exists(sxs_conf_filr)):
        config_file = sxs_conf_filr

    if (config_file is not None):
        config_ts = os.stat(config_file).st_mtime
        strings, color_map = parse_config(config_file)
    else:
        config_ts = 0
        strings = []
        color_map = {}

    while (True):

        line = sys.stdin.readline()

        if ("" == line):
            #
            # stdint died ?
            #
            break

        line = line.strip("\r\n")

        #
        # see if the config file changed and reparse it so the user
        # doesn't have to interrupt his thing
        #
        if (config_file is not None):
            if (config_ts != os.stat(config_file).st_mtime):
                config_ts = os.stat(config_file).st_mtime
                strings, color_map = parse_config(config_file)

        color = NONE

        for s in strings:
            if None != re.search(s, line):
                color = color_map[s]
                break

        if (DROP == color):
            continue

        if (out_fd is not None):
            out_fd.write(line + "\n")
            out_fd.flush()

        if (NONE == color):
            print(line)
        else:
            console_print(line, color)


def main() -> int:

    status = 1

    try:
        if (1 == len(sys.argv)):
            read_loop()
        else:
            with open(sys.argv[1], "a") as f:
                read_loop(f)
        status = 0
    except KeyboardInterrupt:
        status = 0

    return status


if __name__ == '__main__':

    status = main()

    if (0 != status):
        sys.exit(status)
