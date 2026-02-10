import collections
import re
from typing import Dict, List, Iterable

class LogParser:
    def __init__(self, log_path: str):
        self.log_path = log_path
        # Example pattern for Common Log Format: 127.0.0.1 - - [01/Jan/2024...] "GET /index.html" 404 123
        self.log_pattern = re.compile(
            r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?"\s(?P<status>\d{3})'
        )

    def get_lines(self) -> Iterable[str]:
        """Generator to read file line-by-line to save memory (O(1) space)."""
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            print(f"Error: File {self.log_path} not found.")
            return

    def get_top_ips_by_status(self, target_status: str, top_n: int = 5) -> List[tuple]:
        """
        Parses the log and returns the most frequent IPs for a status code.
        """
        ip_counts = collections.Counter()

        for line in self.get_lines():
            match = self.log_pattern.search(line)
            if match:
                ip = match.group('ip')
                status = match.group('status')
                
                if status == target_status:
                    ip_counts[ip] += 1
        
        return ip_counts.most_common(top_n)

# --- Mocking for Tests ---
import unittest
from unittest.mock import patch, mock_open

class TestLogParser(unittest.TestCase):
    def test_parser_logic(self):
        # Sample log data with two 404s from one IP and one 404 from another
        mock_data = (
            '192.168.1.1 - - "GET /a" 404 10\n'
            '192.168.1.1 - - "GET /b" 404 20\n'
            '10.0.0.1 - - "GET /c" 404 30\n'
            '192.168.1.1 - - "GET /d" 200 40\n'
        )
        
        with patch("builtins.open", mock_open(read_data=mock_data)):
            parser = LogParser("fake_path.log")
            results = parser.get_top_ips_by_status("404", top_n=1)
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], ("192.168.1.1", 2))

if __name__ == "__main__":
    # In an interview, you can run the unittest suite directly
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLogParser)
    unittest.TextTestRunner(verbosity=1).run(suite)