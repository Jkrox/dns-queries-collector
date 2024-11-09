# DNS Log parser
This is a DNS log parser that processes DNS log files, collects statistics, and optionally sends the data to the Lumu API.

## Requirements
- Python 3.12 or higher

## Setup
1. Clone the repository:
    ```sh
    git clone https://github.com/Jkrox/dns-queries-collector
    cd dns-queries-collector
    ```

2. Copy the `.env.example` to `.env` and fill in your Lumu API credentials:
    ```
    cp .env.example .env
    ```

## Running the program

1. Ensure your `.env` file is correctly configured with your Lumu API credentials:
    ```env
    LUMU_CLIENT_KEY=your_client_key
    COLLECTOR_ID=your_collector_id
    ```
2. Run the program with the path to your DNS log file:
    ```sh
    python main.py queries.log
    ```

3. To enable sending data to the Lumu API, add the `--send-to-api` flag:
    ```sh
    python main.py queries.log --send-to-api
    ```


## CLI Arguments
```sh
$ python main.py --help
usage: main.py [-h] [--send-to-api] filename

DNS Log Parser for Lumu

positional arguments:
  filename       Path to the DNS log file

options:
  -h, --help     show this help message and exit
  --send-to-api  Enable sending data to Lumu API
```

## Computational Complexity of the Ranking Algorithm

The ranking algorithm used in this project is implemented in the `print_rank` method of the `DNSLogParser` class. The computational complexity of this algorithm can be broken down as follows:

1. **Counting occurrences**: The `Counter` class from the `collections` module is used to count occurrences of client IPs and hostnames. This operation is O(n), where n is the number of log entries.

2. **Sorting**: The `most_common` method of the `Counter` class is used to get the top 5 most common items. This method internally uses a heap to keep track of the top k elements, which has a complexity of O(n log k), where k is the number of top elements to retrieve (in this case, k=5).

3. **Printing**: Printing the results is O(k), where k is the number of top elements to print (in this case, k=5).

Overall, the computational complexity of the ranking algorithm is O(n log k), where n is the number of log entries and k is the number of top elements to retrieve.
