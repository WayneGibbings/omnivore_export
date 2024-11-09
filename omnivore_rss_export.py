import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
import os

@dataclass
class Subscription:
    name: str
    url: Optional[str] = None
    folder: Optional[str] = None
    created_at: Optional[datetime] = None
    last_fetched_at: Optional[datetime] = None
    description: Optional[str] = None
    newsletter_email: Optional[str] = None
    refreshed_at: Optional[datetime] = None
    count: Optional[int] = None
    icon: Optional[str] = None
    is_private: Optional[bool] = None
    auto_add_to_library: Optional[bool] = None
    fetch_content: Optional[bool] = None
    failed_at: Optional[datetime] = None

class OmnivoreClient:
    def __init__(self, token: str, host: str, graphql_path: str):
        self.token = token
        # Construct the base URL from components
        self.base_url = f"https://{host}{graphql_path}"
        self.headers = {
            "Authorization": token,  # No 'Bearer' prefix
            "Content-Type": "application/json",
        }

    def get_subscriptions(self) -> List[Subscription]:
        """
        Fetch all RSS subscriptions from Omnivore.
        
        Returns:
            List of Subscription objects
        """
        query = """
        query GetSubscriptions {
            subscriptions {
                ... on SubscriptionsSuccess {
                    subscriptions {
                        name
                        url
                        folder
                        createdAt
                        lastFetchedAt
                        description
                        newsletterEmail
                        refreshedAt
                        count
                        icon
                        isPrivate
                        autoAddToLibrary
                        fetchContent
                        failedAt
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query}
            )
            
            # Print debug information
            print(f"Status Code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response Headers: {response.headers}")
                print(f"Response Text: {response.text[:500]}...")
            
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            
            # Check for errors in the response
            if "errors" in data:
                raise Exception(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}")

            result = data["data"]["subscriptions"]
            
            if "errorCodes" in result:
                raise Exception(f"Subscription error: {result['errorCodes']}")

            subscriptions = []
            for sub in result["subscriptions"]:
                created_at = datetime.fromisoformat(sub["createdAt"].replace("Z", "+00:00")) if sub.get("createdAt") else None
                last_fetched_at = datetime.fromisoformat(sub["lastFetchedAt"].replace("Z", "+00:00")) if sub.get("lastFetchedAt") else None
                refreshed_at = datetime.fromisoformat(sub["refreshedAt"].replace("Z", "+00:00")) if sub.get("refreshedAt") else None
                failed_at = datetime.fromisoformat(sub["failedAt"].replace("Z", "+00:00")) if sub.get("failedAt") else None
                
                subscription = Subscription(
                    name=sub["name"],
                    url=sub.get("url"),
                    folder=sub.get("folder"),
                    created_at=created_at,
                    last_fetched_at=last_fetched_at,
                    description=sub.get("description"),
                    newsletter_email=sub.get("newsletterEmail"),
                    refreshed_at=refreshed_at,
                    count=sub.get("count"),
                    icon=sub.get("icon"),
                    is_private=sub.get("isPrivate"),
                    auto_add_to_library=sub.get("autoAddToLibrary"),
                    fetch_content=sub.get("fetchContent"),
                    failed_at=failed_at
                )
                subscriptions.append(subscription)

            return subscriptions

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise

    def export_to_opml(self, subscriptions: List[Subscription], filename: str) -> None:
        """
        Export subscriptions to OPML format
        
        Args:
            subscriptions: List of Subscription objects
            filename: Output filename
        """
        opml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        opml += '<opml version="2.0">\n'
        opml += '  <head>\n'
        opml += f'    <title>Omnivore RSS Subscriptions Export - {datetime.now().strftime("%Y-%m-%d")}</title>\n'
        opml += '  </head>\n'
        opml += '  <body>\n'

        # Group subscriptions by folder
        folders: Dict[str, List[Subscription]] = {}
        for sub in subscriptions:
            folder = sub.folder or "Uncategorized"
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(sub)

        # Write each folder and its subscriptions
        for folder, subs in folders.items():
            if folder != "Uncategorized":
                opml += f'    <outline text="{folder}" title="{folder}">\n'
            
            for sub in subs:
                if sub.url:  # Only include subscriptions with URLs
                    opml += f'      <outline type="rss" text="{sub.name}" title="{sub.name}" xmlUrl="{sub.url}"/>\n'
            
            if folder != "Uncategorized":
                opml += '    </outline>\n'

        opml += '  </body>\n'
        opml += '</opml>'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(opml)

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get required environment variables
    token = os.getenv("OMNIVORE_API_TOKEN")
    host = os.getenv("OMNIVORE_HOST")
    graphql_path = os.getenv("OMNIVORE_GRAPH_QL_PATH")

    # Validate all required environment variables are present
    missing_vars = []
    if not token:
        missing_vars.append("OMNIVORE_API_TOKEN")
    if not host:
        missing_vars.append("OMNIVORE_HOST")
    if not graphql_path:
        missing_vars.append("OMNIVORE_GRAPH_QL_PATH")

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    import argparse
    parser = argparse.ArgumentParser(description='Export Omnivore RSS subscriptions to OPML')
    parser.add_argument('--exclude-unfetched', action='store_true', 
                      help='Exclude feeds that have never been fetched after creation')
    args = parser.parse_args()
    
    try:
        client = OmnivoreClient(token, host, graphql_path)
        print("Fetching subscriptions...")
        subscriptions = client.get_subscriptions()
        
        # Filter out unfetched subscriptions if requested
        if args.exclude_unfetched:
            original_count = len(subscriptions)
            subscriptions = [sub for sub in subscriptions if not (
                sub.last_fetched_at is None or 
                (sub.created_at and sub.last_fetched_at and 
                 abs((sub.last_fetched_at - sub.created_at).total_seconds()) < 60)  # Within 1 minute
            )]
            filtered_count = original_count - len(subscriptions)
            if filtered_count > 0:
                print(f"\nFiltered out {filtered_count} never-fetched subscriptions")
        
        # Print subscriptions
        print(f"\nFound {len(subscriptions)} RSS subscriptions:")
        for sub in subscriptions:
            print(f"\nName: {sub.name}")
            if sub.url:
                print(f"URL: {sub.url}")
            if sub.folder:
                print(f"Folder: {sub.folder}")
            if sub.description:
                print(f"Description: {sub.description}")
            if sub.newsletter_email:
                print(f"Newsletter email: {sub.newsletter_email}")
            if sub.created_at:
                print(f"Created at: {sub.created_at.strftime('%Y-%m-%d')}")
            if sub.last_fetched_at:
                print(f"Last fetched at: {sub.last_fetched_at.strftime('%Y-%m-%d')}")
            if sub.refreshed_at:
                print(f"Refreshed at: {sub.refreshed_at.strftime('%Y-%m-%d')}")
            if sub.count is not None:
                print(f"Count: {sub.count}")
            if sub.icon:
                print(f"Icon: {sub.icon}")
            if sub.is_private is not None:
                print(f"Is private: {sub.is_private}")
            if sub.auto_add_to_library is not None:
                print(f"Auto add to library: {sub.auto_add_to_library}")
            if sub.fetch_content is not None:
                print(f"Fetch content: {sub.fetch_content}")
            if sub.failed_at:
                print(f"Failed at: {sub.failed_at.strftime('%Y-%m-%d')}")
        
        # Export to OPML
        output_file = f"omnivore_rss_export_{datetime.now().strftime('%Y%m%d')}.opml"
        client.export_to_opml(subscriptions, output_file)
        print(f"\nExported subscriptions to {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

if __name__ == "__main__":
    main()