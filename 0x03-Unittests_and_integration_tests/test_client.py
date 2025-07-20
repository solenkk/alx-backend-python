#!/usr/bin/env python3
"""
Unit tests for utils and client modules.
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from parameterized import parameterized, parameterized_class
from utils import access_nested_map, get_json, memoize
from client import GithubOrgClient
import fixtures


class TestAccessNestedMap(unittest.TestCase):
    """Tests the access_nested_map function."""

    @parameterized.expand([
        ("simple", {"a": 1}, ("a",), 1),
        ("nested", {"a": {"b": 2}}, ("a",), {"b": 2}),
        ("deep", {"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, name, nested_map, path, expected):
        """Test access_nested_map returns correct result."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ("missing_key", {}, ("a",)),
        ("missing_nested_key", {"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, name, nested_map, path):
        """Test access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Tests the get_json function."""

    @parameterized.expand([
        ("url1", "http://example.com", {"payload": True}),
        ("url2", "http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, name, test_url, expected):
        """Test get_json returns expected JSON payload."""
        with patch("utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = expected
            self.assertEqual(get_json(test_url), expected)
            mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Tests the memoize decorator."""

    def test_memoize(self):
        """Test memoize caches method result after first call."""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()
        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            self.assertEqual(test_obj.a_property, 42)
            self.assertEqual(test_obj.a_property, 42)
            mock_method.assert_called_once()


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org calls get_json with proper URL."""
        expected = {"login": org_name}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self):
        """Test _public_repos_url returns expected URL."""
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test/repos"}
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url, "https://api.github.com/orgs/test/repos")

    @patch("client.GithubOrgClient._public_repos_url", new_callable=PropertyMock)
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json, mock_url):
        """Test public_repos returns list of repo names."""
        mock_url.return_value = "https://api.github.com/orgs/test/repos"
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        client = GithubOrgClient("test")
        self.assertEqual(client.public_repos(), ["repo1", "repo2"])
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with("https://api.github.com/orgs/test/repos")

    @patch("client.get_json")
    def test_has_license(self, mock_get_json):
        """Test has_license returns True if repo has specified license."""
        client = GithubOrgClient("test")
        repo = {"license": {"key": "mit"}}
        self.assertTrue(client.has_license(repo, "mit"))
        self.assertFalse(client.has_license(repo, "apache-2.0"))


@parameterized_class([
    {"org_payload": fixtures.org_payload,
     "repos_payload": fixtures.repos_payload,
     "expected_repos": fixtures.expected_repos,
     "apache2_repos": fixtures.apache2_repos}
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient with parameterized class."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get for all tests in class."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        cls.mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=cls.org_payload)),
            MagicMock(json=MagicMock(return_value=cls.repos_payload))
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repo names."""
        client = GithubOrgClient("test")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test filtering repos by license."""
        client = GithubOrgClient("test")
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
