from whoahqa.security import pwd_context
from whoahqa.models import (
    User,
    UserProfile,
)
from whoahqa.tests import TestBase


class TestUserProfile(TestBase):
    def setUp(self):
        super(TestUserProfile, self).setUp()
        pwd_context.load_path('test.ini')

    def test_set_password(self):
        profile = UserProfile(user=User(), username="admin", password="admin")
        self.assertTrue(pwd_context.verify('admin', profile.pwd))

    def test_check_password(self):
        profile = UserProfile(user=User(), username="admin", password="admin")
        self.assertTrue(profile.check_password('admin'))

    def test_check_password_returns_false_if_len_greater_than_255(self):
        profile = UserProfile(user=User(), username="admin", password="admin")
        self.assertFalse(profile.check_password('a' * 256))

    def test_password_property_returns_raw_password(self):
        profile = UserProfile(user=User(), username="admin", password="admin")
        self.assertEqual(profile.password, profile.pwd)
