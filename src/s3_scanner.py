import boto3
import json
import os
from google import genai


def lambda_handler(event, context):
    """Scan S3 buckets for encryption and use AI to explain risks"""

    s3_client = boto3.client('s3')

    print("Scanning S3 buckets for encryption...")

    response = s3_client.list_buckets()
    buckets = response['Buckets']

    print(f"Found {len(buckets)} buckets to scan\n")

    scan_results = []

    for bucket in buckets:
        bucket_name = bucket['Name']

        # Check if bucket has encryption enabled
        try:
            encryption = s3_client.get_bucket_encryption(
                Bucket=bucket_name
            )

            encrypted = True

            encryption_type = (
                encryption['ServerSideEncryptionConfiguration']
                ['Rules'][0]
                ['ApplyServerSideEncryptionByDefault']
                ['SSEAlgorithm']
            )

        except s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
            encrypted = False
            encryption_type = 'None'

        # Store result
        scan_results.append({
            'bucket_name': bucket_name,
            'encrypted': encrypted,
            'encryption_type': encryption_type
        })

        status = "Encrypted" if encrypted else "Not Encrypted"
        print(f"{status}: {bucket_name} ({encryption_type})")

    # Count unencrypted buckets
    unencrypted_count = len([
        r for r in scan_results
        if not r['encrypted']
    ])

    unencrypted_buckets = [
        r['bucket_name']
        for r in scan_results
        if not r['encrypted']
    ]

    # Use Gemini AI to analyze security findings
    print("\nAnalyzing security findings with Gemini AI...")

    # Get Gemini API key
    api_key = os.environ.get('GOOGLE_API_KEY')

    if not api_key:
        ai_analysis = (
            "AI analysis skipped: "
            "google_api_key not configured"
        )

    else:
        client = genai.Client(api_key=api_key)

        prompt = f"""You are an AWS security expert. Analyze this S3 encryption scan and provide a brief security assessment.

Scan Results:

- Total Buckets: {len(buckets)}

- Encrypted: {len(buckets) - unencrypted_count}

- Unencrypted: {unencrypted_count}

- Unencrypted Bucket Names: {', '.join(unencrypted_buckets) if unencrypted_buckets else 'None'}

Provide a 2-3 sentence analysis:

1. What's the security risk of unencrypted buckets?

2. What encryption should be enabled? (AES256 or aws:kms)

3. What action should the user take immediately?

Be concise and actionable."""

        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            ai_analysis = response.text

        except Exception as e:
            ai_analysis = f"AI analysis failed: {str(e)}"

    # Build final result
    result = {
        'total_buckets': len(buckets),
        'unencrypted_buckets': unencrypted_count,
        'encrypted_buckets': len(buckets) - unencrypted_count,
        'scan_results': scan_results,
        'ai_analysis': ai_analysis,
        'alert': unencrypted_count > 0
    }

    print(
        f"\nScan complete: "
        f"{unencrypted_count}/{len(buckets)} buckets need encryption"
    )

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
