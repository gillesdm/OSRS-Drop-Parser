# OSRS Wiki Search Tool

![OSRS Wiki Search Tool](https://img.shields.io/badge/OSRS-Wiki%20Search%20Tool-brightgreen)

A powerful command-line tool to fetch and save drop tables for monsters in Old School RuneScape (OSRS) using the OSRS Wiki API.

## Features

- Search for monsters within a specific OSRS Wiki category or search for a specific monster
- Fetch drop tables for all monsters in a category or for a specific monster
- Save drop tables in JSON format (always)
- Optionally save drop tables in TXT format
- Optionally save only item IDs as a comma-separated list
- Create RuneLite bank layout files
- Display progress and results in a rich, interactive console interface

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Windows

1. Open Command Prompt or PowerShell
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/osrs-wiki-search-tool.git
   cd osrs-wiki-search-tool
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### macOS

1. Open Terminal
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/osrs-wiki-search-tool.git
   cd osrs-wiki-search-tool
   ```
3. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the OSRS Wiki Search Tool, use the following command:

```
python osrs_scraper/main.py [options]
```

### Options

- `--logs`: Enable logging of API responses and parsed data
- `--txt`: Output drop tables as a txt file in addition to JSON
- `--id`: Output only item IDs as a comma-separated list in a txt file (default: True)
- `--sort`: Sort the item IDs from small to large (default: True)
- `--banklayout`: Create a RuneLite bank layout file (default: True)

### Examples

1. Search for a specific monster and save drop table in JSON and TXT formats:
   ```
   python osrs_scraper/main.py --txt
   ```

2. Search for a category of monsters and save only item IDs:
   ```
   python osrs_scraper/main.py --id
   ```

3. Create a RuneLite bank layout file for a specific monster:
   ```
   python osrs_scraper/main.py --banklayout
   ```

4. Enable logging for debugging:
   ```
   python osrs_scraper/main.py --logs
   ```

## Output

The tool will create output files in the `osrs_scraper/Output` directory. Depending on the options used, you may find:

- JSON files with full drop table information
- TXT files with formatted drop tables
- TXT files with comma-separated item IDs
- TXT files with RuneLite bank layout data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OSRS Wiki for providing the API and data
- The OSRS community for their continued support and contributions to the wiki

Happy scaping!
