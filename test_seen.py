import os
from datetime import datetime
from unittest import mock

from errbot.backends.test import FullStackTest


class TestSeen(FullStackTest):
    pytest_plugins = ["errbot.backends.test"]
    timeout = os.environ.get('TIMEOUT', 20)

    TIMESTAMP = datetime(2017, 7, 15, 3, 15, 28, 578312)

    def setUp(self, **kwargs):
        super().setUp(extra_plugin_dir='.', loglevel=50)
        self.plugin = self._bot.plugin_manager.get_plugin_obj_by_name('Seen')

    def test_that_save_message_saves_a_message(self):
        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = self.TIMESTAMP

            self.plugin.save_message(username='flip',
                                     message='some random words from flip')

            assert self.plugin.get('flip') == {
                'msg': 'some random words from flip',
                'time': self.TIMESTAMP,
            }

    def test_that_get_message_returns_a_message_dict(self):
        self.plugin['flip'] = {
            "msg": "some random words",
            "time": self.TIMESTAMP,
        }

        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = datetime(2017, 7, 15, 3, 15, 28, 578312)
            a = self.plugin.get_message(username='flip')

            for i in ("username", "timestamp", "message", "since", "date"):
                assert a.get(i, False)

            assert a["username"] == "flip"
            assert a["timestamp"] == self.TIMESTAMP
            assert a["message"] == "some random words"
            assert a["since"] == "0 seconds"
            assert a["date"] == "Saturday, Jul 15 at 03:15"

    def test_that_get_message_returns_an_empty_dict_if_user_not_found(self):
        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = datetime(2017, 7, 15, 3, 15, 28, 578312)
            a = self.plugin.get_message(username='johan')
            assert a == {}

    def test_that_get_message_returns_an_empty_dict_if_data_is_corrupt(self):
        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = datetime(2017, 7, 15, 3, 15, 28, 578312)

            self.plugin['flip'] = {"msg": "some random words"}
            a = self.plugin.get_message(username='flip')
            assert a == {}

            self.plugin['flip'] = {"time": self.TIMESTAMP}
            a = self.plugin.get_message(username='flip')
            assert a == {}

    def test_that_seen_cmd_returns_joke_when_requester_uses_own_name(self):
        self.assertCommand('!seen gbin@localhost',
                           'Having personality issues?', timeout=self.timeout)

    def test_that_seen_cmd_returns_question_when_no_username_is_given(self):
        self.assertCommand('!seen', 'Hmm... seen whom?', timeout=self.timeout)

    def test_that_seen_cmd_returns_not_seen_message_when_user_not_found(self):
        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = datetime(2017, 7, 15, 3, 15, 28, 578312)
            self.assertCommand('!seen flip',
                               'I have no record of flip',
                               timeout=self.timeout)

    def test_that_seen_cmd_returns_seen_message_when_user_was_seen(self):
        self.plugin['flip'] = {
            "msg": "some random words",
            "time": self.TIMESTAMP,
        }
        with mock.patch.object(self.plugin, 'get_timestamp') as mock_helper:
            mock_helper.return_value = datetime(2017, 7, 15, 3, 15, 28, 578312)
            self.assertCommand('!seen flip', 'I last saw flip 0 seconds ago '
                                             '(on Saturday, '
                                             'Jul 15 at 03:15) '
                                             'which said "some random words"',
                               timeout=self.timeout)
