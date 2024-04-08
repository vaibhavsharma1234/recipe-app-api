"""
test custom django management commands
"""


from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# with patch we mock the test
@patch('core.management.commands.wait_for_db.Command.check')
# command has a function check we mock it
class CommandTests(SimpleTestCase):
    """
    test the wait_for_db command
    """
    def test_wait_for_db_ready(self, patched_check):
        """
        test waiting for db when db is available
        """
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    # case now when db not ready
    # mock the sleep meethon check db wait some time and check again
    # applies argument inside out
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        test waiting for db when db is not available
        """
        # raise an exception
        # first two times caal the psycopg2 error  AND NEXT 3
        # TIMES OPERATIONAL ERROR
        patched_check.side_effect = [Psycopg2Error]*2 + \
            [OperationalError]*3 + [True]
        call_command('wait_for_db')
        # FOR SIX TIMES WE CALL THE CHECK FUNCTION AND AT SIX WE REUTRN TRUE
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
