from datetime import datetime
from errbot import botcmd, BotPlugin
from errbot.utils import format_timedelta


class Seen(BotPlugin):
    @staticmethod
    def get_timestamp():
        return datetime.now()

    def save_message(self, username, message):
        data = {
            "time": self.get_timestamp(),
            "msg": message,
        }
        self[username] = data

    def get_message(self, username):
        if username not in self:
            return {}

        data = self[username]

        if 'time' not in data or 'msg' not in data:
            return {}

        return {
            "username": username,
            "timestamp": data['time'],
            "message": data['msg'],
            "since": format_timedelta(self.get_timestamp() - data['time']),
            "date": datetime.strftime(data['time'], '%A, %b %d at %H:%M'),
        }

    def callback_message(self, mess):
        message = mess.body
        if not message:
            return

        username = str(mess.frm)
        if not username:
            return

        self.log.debug("Recording presence of %s", username)

        self.save_message(username=username, message=message)

    @botcmd(admin_only=False)
    def seen(self, mess, args):
        """Find out when someone last said something"""

        requester = str(mess.frm)
        username = str(args)

        self.log.debug('{0} looking for {1}'.format(requester, username))

        if username == requester:
            return 'Having personality issues?'

        if username == '':
            return 'Hmm... seen whom?'

        data = self.get_message(username=username)
        if not data:
            return 'I have no record of %s' % args

        return 'I last saw {username} {since} ' \
               'ago (on {date}) which said "{message}"'.format(**data)
