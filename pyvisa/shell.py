#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pyvisa.shell
    ~~~~~~~~~~~~

    Shell for interactive testing.

    This file is taken from the Lantz Project.

    :copyright: (c) 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import cmd
import sys

from .compat import input
from . import ResourceManager, constants, VisaIOError
from .thirdparty import prettytable

if sys.platform == 'darwin':

    class Cmd(cmd.Cmd):

        # This has been patched to enable autocompletion on Mac OSX
        def cmdloop(self, intro=None):
            """Repeatedly issue a prompt, accept input, parse an initial prefix
            off the received input, and dispatch to action methods, passing them
            the remainder of the line as argument.
            """

            self.preloop()
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    self.old_completer = readline.get_completer()
                    readline.set_completer(self.complete)

                    if 'libedit' in readline.__doc__:
                        # readline linked to BSD libedit
                        if self.completekey == 'tab':
                            key = '^I'
                        else:
                            key = self.completekey
                        readline.parse_and_bind('bind %s rl_complete' % (key,))
                    else:
                        # readline linked to the real readline
                        readline.parse_and_bind(self.completekey + ': complete')

                except ImportError:
                    pass
            try:
                if intro is not None:
                    self.intro = intro
                if self.intro:
                    self.stdout.write(str(self.intro)+"\n")
                stop = None
                while not stop:
                    if self.cmdqueue:
                        line = self.cmdqueue.pop(0)
                    else:
                        if self.use_rawinput:
                            try:
                                line = input(self.prompt)
                            except EOFError:
                                line = 'EOF'
                        else:
                            self.stdout.write(self.prompt)
                            self.stdout.flush()
                            line = self.stdin.readline()
                            if not len(line):
                                line = 'EOF'
                            else:
                                line = line.rstrip('\r\n')
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
                self.postloop()
            finally:
                if self.use_rawinput and self.completekey:
                    try:
                        import readline
                        readline.set_completer(self.old_completer)
                    except ImportError:
                        pass
else:
    Cmd = cmd.Cmd


class VisaShell(Cmd):
    """Shell for interactive testing.
    """

    intro = '\nWelcome to the VISA shell. Type help or ? to list commands.\n'
    prompt = '(visa) '

    use_rawinput = True

    def __init__(self, library_path=''):
        Cmd.__init__(self)
        self.resource_manager = ResourceManager(library_path)
        self.default_prompt = self.prompt

        #: Resource list (used for autocomplete)
        #: Store a tuple with the name and the alias.
        #: list[tuple(str, str)]
        self.resources = []

        #: Resource in use
        #: pyvisa.resources.Resource
        self.current = None

        #: list[str]
        self.py_attr = []
        #: list[str]
        self.vi_attr = []

    def do_list(self, args):
        """List all connected resources."""

        try:
            resources = self.resource_manager.list_resources_info()
        except Exception as e:
            print(e)
        else:
            self.resources = []
            for ndx, (resource_name, value) in enumerate(resources.items()):
                if not args:
                    print('({:2d}) {}'.format(ndx, resource_name))
                    if value.alias:
                        print('     alias: {}'.format(value.alias))

                self.resources.append((resource_name, value.alias or None))

    def do_open(self, args):
        """Open resource by number, resource name or alias: open 3"""

        if not args:
            print('A resource name must be specified.')
            return

        if self.current:
            print('You can only open one resource at a time. Please close the current one first.')
            return

        if args.isdigit():
            try:
                args = self.resources[int(args)][0]
            except IndexError:
                print('Not a valid resource number. Use the command "list".')
                return

        try:
            self.current = self.resource_manager.open_resource(args)
            print('{} has been opened.\n'
                  'You can talk to the device using "write", "read" or "query.\n'
                  'The default end of message is added to each message'.format(args))

            self.py_attr = []
            self.vi_attr = []
            for attr in getattr(self.current, 'visa_attributes_classes', ()):
                if attr.py_name:
                    self.py_attr.append(attr.py_name)
                self.vi_attr.append(attr.visa_name)

            self.prompt = '(open) '
        except Exception as e:
            print(e)

    def complete_open(self, text, line, begidx, endidx):
        if not self.resources:
            self.do_list('do not print')
        return [item[0] for item in self.resources if item[0].startswith(text)] + \
               [item[1] for item in self.resources if item[1] and item[1].startswith(text)]

    def do_close(self, args):
        """Close resource in use."""

        if not self.current:
            print('There are no resources in use. Use the command "open".')
            return

        try:
            self.current.close()
        except Exception as e:
            print(e)
        else:
            print('The resource has been closed.')
            self.current = None
            self.prompt = self.default_prompt

    def do_query(self, args):
        """Query resource in use: query *IDN? """

        if not self.current:
            print('There are no resources in use. Use the command "open".')
            return

        try:
            print('Response: {}'.format(self.current.query(args)))
        except Exception as e:
            print(e)

    def do_read(self, args):
        """Receive from the resource in use."""

        if not self.current:
            print('There are no resources in use. Use the command "open".')
            return

        try:
            print(self.current.read())
        except Exception as e:
            print(e)

    def do_write(self, args):
        """Send to the resource in use: send *IDN? """

        if not self.current:
            print('There are no resources in use. Use the command "open".')
            return

        try:
            self.current.write(args)
        except Exception as e:
            print(e)

    def print_attribute_list(self):
        p = prettytable.PrettyTable(('VISA name', 'Constant', 'Python name', 'val'))
        for attr in getattr(self.current, 'visa_attributes_classes', ()):
            try:
                val = self.current.get_visa_attribute(attr.attribute_id)
            except VisaIOError as e:
                val = e.abbreviation
            except Exception as e:
                val = str(e)
                if len(val) > 10:
                    val = val[:10] + '...'
            p.add_row((attr.visa_name, attr.attribute_id, attr.py_name, val))

        print(p.get_string(sortby='VISA name'))

    def do_attr(self, args):
        """Get or set the state for a visa attribute.

        List all attributes:

            attr

        Get an attribute state:

            attr <name>

        Set an attribute state:

            attr <name> <state>
        """

        if not self.current:
            print('There are no resources in use. Use the command "open".')
            return

        args = args.strip()

        if not args:
            self.print_attribute_list()
            return

        args = args.split(' ')

        if len(args) > 2:
            print('Invalid syntax, use `attr <name>` to get; or `attr <name> <value>` to set')
        elif len(args) == 1:
            # Get
            attr_name = args[0]
            if attr_name.startswith('VI_'):
                try:
                    print(self.current.get_visa_attribute(getattr(constants, attr_name)))
                except Exception as e:
                    print(e)
            else:
                try:
                    print(getattr(self.current, attr_name))
                except Exception as e:
                    print(e)
        else:
            attr_name, attr_state = args[0], args[1]
            if attr_name.startswith('VI_'):
                try:
                    self.current.set_visa_attribute(getattr(constants, attr_name), attr_state)
                    print('Done')
                except Exception as e:
                    print(e)
            else:
                print('Setting Resource Attributes by python name is not yet supported.')
                return
                try:
                    print(getattr(self.current, attr_name))
                    print('Done')
                except Exception as e:
                    print(e)

    def complete_attr(self, text, line, begidx, endidx):
        return [item for item in self.py_attr if item.startswith(text)] + \
               [item for item in self.vi_attr if item.startswith(text)]

    def do_exit(self, arg):
        """Exit the shell session."""

        if self.current:
            self.current.close()
        self.resource_manager.close()
        del self.resource_manager
        return True

    def do_EOF(self, arg):
        """.
        """
        return True


def main(library_path=''):
    VisaShell(library_path).cmdloop()

