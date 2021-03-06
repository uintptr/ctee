#!/usr/bin/env python3

import sys
import os
import re


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


def console_print(text, color=WHITE):
    text = "\x1b[1;%dm" % (30 + color) + text + "\x1b[0m"
    print(text)


def parse_config(conf_file):

    strings = []
    color_map = {}

    print("[+] parsing {}".format(conf_file))

    if (True == os.path.isfile(conf_file)):
        with open(conf_file, "r") as f:
            for line in f:
                line = line.strip("\r\n")
                if(True == line.startswith('#') or
                        0 == len(line)):
                    continue
                (s, c) = line.split('=')

                color = c.strip(' ')
                string = re.sub('" *', '', s)

                strings.append(string)

                color_map[string] = colors.index(color)

    return (strings, color_map)


def read_loop(out_fd):

    conf_file = os.path.expanduser("~/.ctee.conf")

    if (True == os.path.exists(conf_file)):
        config_ts = os.stat(conf_file).st_mtime
        strings, color_map = parse_config(conf_file)
    else:
        config_ts = 0
        strings = []
        color_map = {}

    while (True):

        line = sys.stdin.readline()

        if (None == line or 0 == len(line)):
            #
            # stdint died ?
            #
            break

        line = line.strip("\r\n")

        #
        # see if the config file changed and reparse it so the user
        # doesn't have to interrupt his thing
        #
        if (True == os.path.exists(conf_file)):
            if (config_ts != os.stat(conf_file).st_mtime):
                config_ts = os.stat(conf_file).st_mtime
                strings, color_map = parse_config(conf_file)

        color = NONE

        for s in strings:
            if None != re.search(s, line):
                color = color_map[s]
                break

        if (DROP == color):
            continue

        if (None != out_fd):
            out_fd.write(line + "\n")
            out_fd.flush()

        if (NONE == color):
            print(line)
        else:
            console_print(line, color)


def main():

    if (1 == len(sys.argv)):
        read_loop(None)
    else:
        with open(sys.argv[1], "a") as f:
            read_loop(f)


if __name__ == '__main__':
    sys.exit(main())
