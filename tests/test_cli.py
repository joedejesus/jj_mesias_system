from __future__ import annotations

import unittest

from src.cli import build_parser


class CLITestCase(unittest.TestCase):
    def test_console_parser_accepts_urls_and_doctor(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "console",
            "hola",
            "--url",
            "https://example.com",
            "--doctor",
        ])
        self.assertEqual(args.mode, "console")
        self.assertEqual(args.prompt, "hola")
        self.assertEqual(args.urls, ["https://example.com"])
        self.assertTrue(args.doctor)


if __name__ == "__main__":
    unittest.main()
