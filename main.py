import http.client
import json
import re
import sys
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any
import argparse
from utils import load_env

class DNSLogParser:
    def __init__(self, client_key: str, collector_id: str) -> None:
        self.client_key = client_key
        self.collector_id = collector_id
        self.client_ips = Counter()
        self.hosts = Counter()
        self.total_records = 0
        self.records_buffer: List[Dict[str, str | Any]] = []

    def parse_line(self, line: str) -> Dict:
        """Parse a single line of DNS log."""
        # Regex pattern example
        pattern = r'.*client.*?\s(\d+\.\d+\.\d+\.\d+)#\d+\s*\((.*?)\):\squery:'

        match = re.search(pattern, line)
        if not match:
            return None

        client_ip, hostname = match.groups()
        
        # Extract the timestamp from the line
        timestamp_match = re.match(r'^(\d{1,2}-\w{3}-\d{4}\s\d{2}:\d{2}:\d{2}\.\d{3})', line)
        if timestamp_match:
            try:
                timestamp = timestamp_match.group(1)
                dt = datetime.strptime(timestamp, "%d-%b-%Y %H:%M:%S.%f")
                iso_timestamp = dt.isoformat() # Convert to ISO 8601 format
            except ValueError:
                iso_timestamp = timestamp
        else:
            iso_timestamp = datetime.now().isoformat()

        return {
            "timestamp": iso_timestamp,
            "client_ip": client_ip,
            "hostname": hostname.strip(),
        }

    def process_file(self, filename: str, send_to_api: bool = False) -> None:
        """Process the log file and collect statistics."""
        try:
            with open(filename, "r") as file:
                for line in file:
                    parsed_data = self.parse_line(line)
                    if parsed_data:
                        self.total_records += 1
                        self.client_ips[parsed_data["client_ip"]] += 1
                        self.hosts[parsed_data["hostname"]] += 1

                        if send_to_api:
                            self.records_buffer.append(parsed_data)
                            if len(self.records_buffer) >= 500: # Send to API in chunks of 500 records
                                self.send_to_api()
                                self.records_buffer.clear() # Clear the buffer

                if send_to_api and self.records_buffer:
                    self.send_to_api()

        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            sys.exit(1)

    def send_to_api(self) -> None:
        """Send the records to the Lumu API in chunks."""
        if not self.records_buffer:
            return

        payload = [
            {
                "timestamp": record["timestamp"],
                "name": record["hostname"],
                "client_ip": record["client_ip"],
            }
            for record in self.records_buffer
        ]

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        url = f"/collectors/{self.collector_id}/dns/queries?key={self.client_key}"
        connection = http.client.HTTPSConnection("api.lumu.io")
        try:
            connection.request(
                "POST", url, 
                json.dumps(payload), 
                headers
            )
            response = connection.getresponse()
            if response.status not in (200, 201):
                print(f"Error sending data to API: {response.status} - {response.reason}")
            else:
                print(f"Successfully sent {len(self.records_buffer)} records -> {response.status} - {response.reason}")

        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            connection.close()

    def get_percentage(self, count: int) -> float:
        """Calculate the percentage of a given count."""
        return (count / self.total_records * 100) if self.total_records > 0 else 0

    def print_rank(self, counter: Counter, title: str, width: int = 15, n_elements: int = 15) -> None:
        """Print a ranking formatted output."""
        separator = "-" * width
        print(f"\n{title} Rank")
        print(f"{separator} ------ --------")

        for item, count in counter.most_common(n_elements):
            percentage = self.get_percentage(count)
            print(f"{item:<{width}} {count:5d}  {percentage:6.2f}%")

        print(f"{separator} ------ --------")

    def print_statistics(self):
        """Print the statistics"""
        print(f"\nTotal records {self.total_records}")
        self.print_rank(self.client_ips, "Client IPs", 20)
        self.print_rank(self.hosts, "Host", 60) 

def main() -> None:
    import os
    load_env()
    
    parser = argparse.ArgumentParser(description="DNS Log Parser for Lumu")
    parser.add_argument("filename", help="Path to the DNS log file")
    parser.add_argument("--send-to-api", action="store_true", help="Enable sending data to Lumu API")
    args = parser.parse_args()
    
    dns_parser = DNSLogParser(
        client_key=os.environ.get("LUMU_CLIENT_KEY"),
        collector_id=os.environ.get("COLLECTOR_ID"),
    )
    
    print(f"Processing file: {args.filename}")
    dns_parser.process_file(args.filename, args.send_to_api)
    dns_parser.print_statistics()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)