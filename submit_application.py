#!/usr/bin/env python3
"""
Submission script for B12 application.
Posts to https://b12.io/apply/submission with required signature.
"""

import json
import os
import sys
import hmac
import hashlib
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def get_iso_timestamp():
    """Generate current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def create_payload(name, email, resume_link, repository_link, action_run_link):
    """Create the JSON payload with sorted keys and no extra whitespace."""
    payload = {
        "action_run_link": action_run_link,
        "email": greencode4523@gmail.com,
        "name": Steven Lee,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": get_iso_timestamp()
    }
    # Sort keys alphabetically and create compact JSON (no extra whitespace)
    return json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False).encode('utf-8')


def calculate_signature(json_body, secret):
    """Calculate HMAC-SHA256 signature for the JSON body."""
    signature = hmac.new(
        secret.encode('utf-8'),
        json_body,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def submit_application(name, email, resume_link, repository_link, action_run_link, signing_secret):
    """Submit the application to B12."""
    url = "https://b12.io/apply/submission"
    
    # Create compact JSON payload
    json_body = create_payload(name, email, resume_link, repository_link, action_run_link)
    
    # Calculate signature
    signature = calculate_signature(json_body, signing_secret)
    
    # Create request with headers
    request = Request(url, data=json_body, method='POST')
    request.add_header('Content-Type', 'application/json; charset=utf-8')
    request.add_header('X-Signature-256', signature)
    
    try:
        with urlopen(request) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            if response_data.get('success'):
                print(response_data.get('receipt', ''))
                return 0
            else:
                print(f"Error: Submission was not successful. Response: {response_data}", file=sys.stderr)
                return 1
    except HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else 'No error details'
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        return 1
    except URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    # Get required fields from environment variables
    name = os.environ.get('APPLICATION_NAME')
    email = os.environ.get('APPLICATION_EMAIL')
    resume_link = os.environ.get('APPLICATION_RESUME_LINK')
    repository_link = os.environ.get('APPLICATION_REPOSITORY_LINK')
    action_run_link = os.environ.get('APPLICATION_ACTION_RUN_LINK')
    signing_secret = os.environ.get('SIGNING_SECRET', 'hello-there-from-b12')
    
    # Validate required fields
    required_fields = {
        'name': name,
        'email': email,
        'resume_link': resume_link,
        'repository_link': repository_link,
        'action_run_link': action_run_link
    }
    
    missing_fields = [key for key, value in required_fields.items() if not value]
    if missing_fields:
        print(f"Error: Missing required environment variables: {', '.join(missing_fields)}", file=sys.stderr)
        print("\nRequired environment variables:", file=sys.stderr)
        print("  APPLICATION_NAME", file=sys.stderr)
        print("  APPLICATION_EMAIL", file=sys.stderr)
        print("  APPLICATION_RESUME_LINK", file=sys.stderr)
        print("  APPLICATION_REPOSITORY_LINK", file=sys.stderr)
        print("  APPLICATION_ACTION_RUN_LINK", file=sys.stderr)
        sys.exit(1)
    
    return submit_application(name, email, resume_link, repository_link, action_run_link, signing_secret)


if __name__ == '__main__':
    sys.exit(main())

