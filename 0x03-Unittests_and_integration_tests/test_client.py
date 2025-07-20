#!/usr/bin/env python3
"""Unit and Integration tests for utils and client"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from utils import access_nested_map, get_json, memoize
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""
    @patch("client.get_json", return_value=None)
    def test_org(self, mock_get_json):
        """Test that org method calls get_json with correct URL"""
        org_name = "testorg"
        client = GithubOrgClient(org_name)
        client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that public repos URL returns expected value"""
        payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("testorg")
            self.assertEqual(
                client._public_repos_url,
                payload["repos_url"]
            )

    @patch("client.get_json")
    @patch.object(
        GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
    )
    def test_public_repos(self, mock_repos_url, mock_get_json):
        """Test that public_repos returns expected list of repos"""
        mock_repos_url.return_value = (
            "https://api.github.com/orgs/testorg/repos"
        )
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        client = GithubOrgClient("testorg")
        self.assertEqual(
            client.public_repos(),
            ["repo1", "repo2"]
        )
        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/testorg/repos"
        )


if __name__ == "__main__":
    unittest.main()
