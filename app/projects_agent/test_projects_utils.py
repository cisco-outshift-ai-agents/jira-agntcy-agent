import unittest
from unittest import TestCase

from projects_agent.projects_utils import is_valid_email


class TestProjectsUtils(unittest.TestCase):

    def test_valid_email(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag+sorting@example.com"))
        self.assertTrue(is_valid_email("user_name@example.co.in"))

    def test_invalid_email(self):
        self.assertFalse(is_valid_email("plainaddress"))
        self.assertFalse(is_valid_email("@missingusername.com"))
        self.assertFalse(is_valid_email("username@.com"))
        self.assertFalse(is_valid_email("username@.com."))
        self.assertFalse(is_valid_email("username@com"))
