import os
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pathlib

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

class GoogleDocsWriter:
    def __init__(self, document_id=None):
        self.document_id = document_id
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Docs API."""
        # Load tokens from environment variables
        access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        
        if access_token and refresh_token:
            from google.oauth2.credentials import Credentials
            self.creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
            )
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Check if credentials.json exists
                credentials_path = pathlib.Path("credentials.json")
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create a new project or select existing one\n"
                        "3. Enable Google Docs API\n"
                        "4. Create credentials (OAuth 2.0 Client ID)\n"
                        "5. Download as credentials.json and place in this directory"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                print(f"Access Token: {self.creds.token}")
                print(f"Refresh Token: {self.creds.refresh_token}")
            
            # Note: Tokens are now stored in environment variables
            # Add these to your .env file:
            # GOOGLE_ACCESS_TOKEN=your_access_token
            # GOOGLE_REFRESH_TOKEN=your_refresh_token
            # GOOGLE_CLIENT_ID=your_client_id
            # GOOGLE_CLIENT_SECRET=your_client_secret
        
        self.service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def _get_or_create_folder(self, folder_name="reddit_results"):
        """Get or create the reddit_results folder."""
        # Search for existing folder
        results = self.drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        if results['files']:
            return results['files'][0]['id']
        
        # Create folder if it doesn't exist
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
        print(f"[ok] Created folder: {folder_name}")
        return folder.get('id')
    
    def create_document(self, title="Reddit Monitoring Results"):
        """Create a new Google Doc and return its ID."""
        # Get or create the reddit_results folder
        folder_id = self._get_or_create_folder()
        
        document = {
            'title': title
        }
        doc = self.service.documents().create(body=document).execute()
        self.document_id = doc.get('documentId')
        
        # Move document to the folder
        self.drive_service.files().update(
            fileId=self.document_id,
            addParents=folder_id,
            removeParents='root'
        ).execute()
        
        print(f"[ok] Created new Google Doc: {title}")
        print(f"[ok] Document ID: {self.document_id}")
        print(f"[ok] Document URL: https://docs.google.com/document/d/{self.document_id}")
        return self.document_id
    
    def write_results(self, results, title="Reddit Monitoring Results"):
        """Write Reddit monitoring results to Google Doc."""
        if not self.document_id:
            self.create_document(title)
        
        # Prepare the content
        content = self._format_results(results)
        
        # Write to document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': content
                }
            }
        ]
        
        self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()
        
        print(f"[ok] Results written to Google Doc: https://docs.google.com/document/d/{self.document_id}")
    
    def _format_results(self, results):
        """Format results for Google Docs."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"Reddit Monitoring Results\n"
        content += f"Generated: {timestamp}\n"
        content += f"{'='*50}\n\n"
        
        if not results:
            content += "No new matches found.\n"
            return content
        
        content += f"Found {len(results)} new matches:\n\n"
        
        for i, result in enumerate(results, 1):
            content += f"{i}. **{result['title']}**\n"
            content += f"   Subreddit: r/{result['subreddit']}\n"
            content += f"   URL: {result['url']}\n"
            content += f"   Created: {result['created']}\n"
            content += f"   Keywords matched: {', '.join(result['keywords'])}\n"
            content += f"\n"
        
        return content
    
    def append_results(self, results):
        """Append new results to existing document."""
        if not self.document_id:
            raise ValueError("No document ID set. Use write_results() first.")
        
        # Get current document content
        document = self.service.documents().get(documentId=self.document_id).execute()
        current_index = len(document['body']['content'][0]['paragraph']['elements'][0]['textRun']['content'])
        
        # Format new results
        new_content = self._format_results(results)
        
        # Append to document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': current_index
                    },
                    'text': f"\n\n{new_content}"
                }
            }
        ]
        
        self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()
        
        print(f"[ok] Results appended to Google Doc: https://docs.google.com/document/d/{self.document_id}")
