# Omnivore RSS Export

A Python script to export your [Omnivore](https://omnivore.app/) RSS subscriptions to OPML format. This makes it easy to backup your subscriptions or migrate them to another RSS reader.

## Features

- Exports all RSS subscriptions to OPML format
- Groups feeds by folder in the OPML output
- Option to exclude feeds that have never been successfully fetched
- Displays detailed information about each subscription
- Supports environment variables for configuration

## Prerequisites

- Python 3.7+
- Omnivore API token
- `requests` and `python-dotenv` packages

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd omnivore-rss-export
```

2. Install required packages:
```bash
pip install requests python-dotenv
```

3. Create a `.env` file in the project directory with your Omnivore API configuration:
```
OMNIVORE_API_TOKEN=your_api_token_here
OMNIVORE_HOST=api-prod.omnivore.app
OMNIVORE_GRAPH_QL_PATH=/api/graphql
```

To get your API token:
1. Go to your Omnivore settings
2. Navigate to the API section
3. Generate a new API token

## Usage

### Basic Export

To export all your RSS subscriptions:
```bash
python omnivore_rss_export.py
```

### Exclude Unfetched Feeds

To export only feeds that have been successfully fetched at least once:
```bash
python omnivore_rss_export.py --exclude-unfetched
```

### Output

The script will:
1. Display information about each subscription, including:
   - Name
   - URL
   - Folder
   - Description
   - Created date
   - Last fetched date
   - Various subscription settings
2. Create an OPML file named `omnivore_rss_export_YYYYMMDD.opml` in the current directory

The OPML file can be imported into most RSS readers, including:
- Feedly
- Inoreader
- NewsBlur
- And many others

## Output Format

The script displays detailed information for each subscription:
```
Name: Example Feed
URL: https://example.com/feed
Folder: Technology
Description: Example feed description
Created at: 2024-01-09
Last fetched at: 2024-01-09
Count: 42
Is private: false
Auto add to library: true
Fetch content: true
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OMNIVORE_API_TOKEN` | Your Omnivore API token |
| `OMNIVORE_HOST` | Omnivore API host (usually `api-prod.omnivore.app`) |
| `OMNIVORE_GRAPH_QL_PATH` | GraphQL endpoint path (usually `/api/graphql`) |

## Error Handling

The script includes comprehensive error handling:
- Validates required environment variables
- Reports API errors with detailed messages
- Provides debugging information for API responses
- Handles invalid dates and missing fields gracefully

## License

[MIT License](LICENSE)