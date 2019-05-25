"""
File to hold some base classes that need to be imported first. This should be a first import
to avoid circular import problems. This file should not import anything (other than standard libraries).

Copyright 2019 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class PlatformEntity(object):
    """
    Base class for objects in the platform. Give an action-logging interface.
    """
    _IgnoreRegisterActions = True
    def __init__(self):
        self._Actions = []

    def _RegisterAction(self, action_class, action_msg, *args):
        """
        Register actions in the object "_Actions" property.

        Used for unit-testing/debugging.

        The *args are parsed via msg.format(args). (We skip the formatting effort if
        we skip registration.)

        Does nothing if PlatformEntity._IgnoreRegisterActions is True (default).

        (This eliminates the performance hit of registration when used in production.)

        :param action_class: str
        :param action_msg: str
        :param args: tuple
        :return:
        """
        if self._IgnoreRegisterActions:
            return
        self._Actions.append((action_class, action_msg.format(args)))

    def _ClearActions(self):
        """
        Clear the action list. (Call ahead of running tests.
        :return:
        """
        self._Actions = []

    def _HasAction(self, action_class=None, msg_substring=None):
        """
        Convenience method for testing.

        Set either action_class or msg_substring.

        Looks for an actions that:

        (1) action_class matches *exactly* the search parameter
        (2) msg_substring appears in the  action message.

        If both are set, both consitions must hold for a single action.

        :param action_class: str
        :param msg_substring: str
        :return: bool
        """
        if action_class is not None and msg_substring is None:
            return action_class in [x[0] for x in self._Actions]
        if action_class is None and msg_substring is not None:
            for x in self._Actions:
                if msg_substring in x[1]:
                    return True
            return False
        if action_class is not None and msg_substring is not None:
            for x in self._Actions:
                if action_class == x[0] and msg_substring in x[1]:
                    return True
            return False
        raise ValueError('Must have at least one non-None input to HasAction()')


class PlatformError(Exception):
    pass


class TickerError(PlatformError):
    pass


class TickerNotFoundError(PlatformError):
    pass


class ConnectionError(PlatformError):
    pass