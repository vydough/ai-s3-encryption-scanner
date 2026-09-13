# AI-Based (Gemini) S3 Encryption Scanner (With Daily Scheduler)

A serverless security tool that scans every S3 bucket in an AWS account for missing encryption, then uses Google Gemini to turn the raw findings into a plain-english security assessment. Built using AWS Lambda, with an optional Amazon EventBridge schedule so the scan runs automatically every 24 hours daily instead of only on manual invocation.

## Overview
Checking every S3 bucket in an account for encryption by hand doesn't scale
past a handful of buckets, and even when you do check, a raw
`get_bucket_encryption` API response doesn't tell you what to actually do
about it. This project automates both parts: a Lambda function scans every
bucket for server-side encryption, and Gemini AI reads the results and
writes a short explanation in plain english of the risk and what to fix first. 

## Project Purpose

I did this project to get hands-on experience with learning how to configure lambda functions, IAM roles and APIs altogether to lead to a real world AWS deployment tool. I wanted to create a simple scanner base tool that is able to offer AI capabilities and insight for users for greater maintainability of cloud-based systems.

## Objectives

- Write a Lambda function that lists S3 buckets and checks each one for
  server-side encryption.
- Integrate the Gemini API so scan results are explained in plain language,
  not just raw JSON.
- Scope an IAM role down to only the permissions the function needs.
- Package Python dependencies for a Lambda deployment.
- Automate the scan on a schedule using Amazon EventBridge.

## Features
- **Encryption scanning** - checks every bucket in the account for
  server-side encryption (`AES256` or `aws:kms`) and records the result.
- **AI-generated summaries** — sends the scan results to Gemini, which
  explains the risk of any unencrypted buckets and what to do next in 2–3
  sentences.
- **Scheduled automation** - an EventBridge rule can trigger the scan every
  12 hours without anyone needing to run it manually.
- **Centralised logging** - every run (manual or scheduled) writes its
  output to Amazon CloudWatch Logs.


## Technologies Used

- **Python 3.12** — the language the Lambda function is written in.
- **AWS Lambda** — runs the scanner function without needing a dedicated
  server. AWS only charges for the time the code actually runs.
- **Amazon S3** (`boto3`) — the service being scanned. `boto3` is AWS's
  Python SDK, used here to list buckets and read each one's encryption
  configuration.
- **AWS IAM** — defines exactly what the Lambda function is allowed to do
  (read-only access to bucket lists and encryption settings, plus
  permission to write logs).
- **Google Gemini AI** (`google-generativeai`) — a large language model used
  to turn the structured scan results into a short, readable security
  assessment.
- **Amazon EventBridge** — schedules the Lambda function to run
  automatically on a recurring basis, instead of only when triggered
  manually.
- **Amazon CloudWatch Logs** — stores the output of every Lambda execution
  so scan results can be checked after the fact.

## Architecture

EventBridge triggers the Lambda function on a schedule. Lambda uses its IAM
role to list S3 buckets and check each one's encryption settings, sends
those findings to Gemini for analysis, and writes the full result: scan
data plus Gemini AI summary to CloudWatch Logs.

## Repository Structure

```
ai-security-scanner-s3/
├── README.md                  # This file
├── requirements.txt            # Python dependencies (boto3, google-genai)
├── .env.example                # Documents the GOOGLE_API_KEY variable (not real key)
├── .gitignore                  # Excludes venv/, package/, zips, .env, OS junk
├── src/
│   └── s3_scanner.py           # The Lambda function: scan + AI analysis
├── infrastructure/
│   ├── iam/
│   │   ├── s3-encryption-read-policy.json  # Read-only S3 permissions
│   │   └── lambda-trust-policy.json        # Lets Lambda assume the role
│   └── eventbridge-schedule.md # Secret mission: scheduled scan config
├── scripts/
│   └── test_event.json                    # Sample event for manual testing

```

## Methodology

The project was split into five main steps, carried out in order:

1. **Getting Gemini API Key**: Obtaining the key from Google AI Studio
2. **Cursor Project Creation**: Creating the project folder in Cursor (aws monitor gemini)
3. **Creating the scanner.py file**: Adding he code to connect to S3, list buckets and encryption check, calling out to Gemini to turn raw scan results into readable risk summaries.
4. **Creating IAM Policy**: read-only access to bucket, attaching it to Lambda role
5. **Building Python depedencies**: creating zip file as Lambda does not have boto3 or google-genai pre-installed
6. **Deployment and testing**: Uploading zip to Lambda function and pointing handler at the right file, adding environment variable, running manual test
7. **Automation for 24 hours**: Using EventBridge scheduler to trigger scan every24 hours (daily) instead of relying on manual invocations, results are outputted in CloudWatch Logs

## Challenges and Solutions / What I learned 

## Future Improvements / Considerations
- Add SNS or Slack notifications instead of relying on someone checking
  CloudWatch Logs.
- Extend scanning to cover public access settings and bucket policies, not
  just encryption.
- Add automated tests using `moto` to mock S3 responses.
- Add optional auto-remediation (enabling default encryption) behind an
  approval step.

## References
- [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon S3 encryption documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html)
- [Amazon EventBridge documentation](https://docs.aws.amazon.com/eventbridge/)
- [Google Gemini API documentation](https://ai.google.dev/)


