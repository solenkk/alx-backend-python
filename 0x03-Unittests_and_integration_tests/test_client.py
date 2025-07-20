#!/usr/bin/env python3
"""Unit and Integration tests for utils and client"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from utils import access_nested_map, get_json, memoize
from client import GithubOrgClient

# Local dummy fixtures for testing
org_payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
repos_payload = [
    {"name": "repo1", "license": {"key": "apache-2.0"}},
    {"name": "repo2", "license": {"key": "other"}},
]
expected_repos = ["repo1", "repo2"]
apache2_repos = ["repo1"]


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for access_nested_map function"""

    @parameterized.expand([
        ("simple", {"a": 1}, ("a",), 1),
        ("nested1", {"a": {"b": 2}}, ("a",), {"b": 2}),
        ("nested2", {"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, name, nested_map, path, expected):
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ("missing1", {}, ("a",)),
        ("missing2", {"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, name, nested_map, path):
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
    """Unit tests for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")
    def test_get_json(self, test_url, test_payload, mock_get):
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = test_payload
        result = get_json(test_url)
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Unit test for memoize decorator"""

    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_method.assert_called_once()


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json", return_value=None)
    def test_org(self, org_name, mock_get_json):
        client = GithubOrgClient(org_name)
        client.org
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self):
        payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("testorg")
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    @patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock)
    def test_public_repos(self, mock_repos_url, mock_get_json):
        mock_repos_url.return_value = "https://api.github.com/orgs/testorg/repos"
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        client = GithubOrgClient("testorg")
        self.assertEqual(client.public_repos(), ["repo1", "repo2"])
        mock_get_json.assert_called_once_with("https://api.github.com/orgs/testorg/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('requests.get')
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if url == "https://api.github.com/orgs/testorg":
                mock_response = Mock()
                mock_response.json.return_value = cls.org_payload
                return mock_response
            elif url == cls.org_payload["repos_url"]:
                mock_response = Mock()
                mock_response.json.return_value = cls.repos_payload
                return mock_response
            return None

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("testorg")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient("testorg")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()
