# AI-Based (Gemini) S3 Encryption Scanner (With Daily Scheduler)

A server-less security tool that scans every S3 bucket in an AWS account for missing encryption, then uses Google Gemini to turn the raw findings into a plain english security assessment. Built using AWS Lambda, with an optional Amazon EventBridge schedule so the scan runs automatically every 24 hours daily instead of only on manual invocation.

## Overview
Checking every S3 bucket in an account for encryption by hand doesn't scale
past a handful of buckets, and even when you do check, a raw
`get_bucket_encryption` API response doesn't tell you what to actually do
about it. This project automates both parts: a Lambda function scans every
bucket for server-side encryption, and Gemini AI reads the results and
writes a short explanation in plain english of the risk and what to fix first. 

## Project Purpose
I did this project to get hands-on experience with learning how to configure lambda functions, IAM roles and APIs altogether to lead to a real world AWS deployment tool. I wanted to create a simple scanner base tool that is able to offer AI capabilities and insight for users for greater maintainability of cloud-based systems.

## Challenges and Solutions / What I learned 
This project taught me how to check S3 bucket encryption programmatically via boto3, including handling cases where buckets have no encryption at all. I also learned how to package external python libraries for lambda as lambda itself does not come with anything pre-installed. For AWS specifically, I was able to refine my current understanding of IAM roles. I implemented least-priviledge to two policies instead of allowing broader S3 access. I also had to amend the handler setting, since Lambda defaults to looking for a file called lambda_function.py whereas my code was in s3_scanner.py instead, so I updated the handler to s3_scanner.lambda_handler. Initially, this caused issues in locating the handler when deploying the Lambda. 

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
  (read-only access to bucket lists and encryption settings, and 
  permission to write logs).
- **Google Gemini AI** (`google-generativeai`) — AI model used to turn the structured scan results into a short, readable security
  assessment.
- **Amazon EventBridge** — schedules the Lambda function to run
  automatically on a recurring basis, instead of only when triggered
  manually.
- **Amazon CloudWatch Logs** — stores the output of every Lambda execution
  so scan results can be checked.

## Additional Feature: EventBridge Scheduler Automation
EventBridge triggers the Lambda function on a schedule. Lambda uses its IAM
role to list S3 buckets and check each one's encryption settings, sends
those findings to Gemini for analysis, and writes the full result: scan
data plus Gemini AI summary to CloudWatch Logs.

## Methodology
1. **Getting Gemini API Key**: Obtaining the key from Google AI Studio
2. **Project Creation**: Creating the project folder in any code editor (aws monitor gemini)
3. **Creating the scanner.py file**: Adding he code to connect to S3, list buckets and encryption check, calling out to Gemini to turn raw scan results into readable risk summaries.
4. **Creating IAM Policy**: read-only access to bucket, attaching it to Lambda role
5. **Building Python depedencies**: creating zip file as Lambda does not have boto3 or google-genai pre-installed
6. **Deployment and testing**: Uploading zip to Lambda function and pointing handler at the right file, adding environment variable, running manual test
7. **Automation for 24 hours**: Using EventBridge scheduler to trigger scan every24 hours (daily) instead of relying on manual invocations, results are outputted in CloudWatch Logs

## Project Demo
![Creating the s3_scanner.py file](/images/01-scanner-code-02.png)
*Creating `s3_scanner.py` file in the*

![Creating the s3_scanner.py file](/images/01-scanner-code-02.png)
*Creating `s3_scanner.py` in the Cursor file explorer.*

![Listing S3 buckets](/images/01-scanner-code-03.png)
*Part 1 of the scanner: connecting to S3 and listing all buckets in the account.*

![Encryption check added](/images/01-scanner-code-04.png)
*Part 2 added: checking each bucket for server-side encryption.*

![Gemini AI analysis added](/images/01-scanner-code-05.png)
*The completed scanner, with the Gemini AI analysis step added to turn the raw findings into a security summary.*

![IAM role with required policies](/images/02-iam-role.png)
*The `LambdaS3ScannerRole` IAM role, showing both the custom `S3EncryptionReadPolicy` and the AWS-managed `AWSLambdaBasicExecutionRole` attached.*

![Lambda test event configuration](/images/03-lambda-test-event.png)
*The test event set up in the Lambda console before running a manual invocation.*

![Lambda test execution succeeded](/images/04-lambda-test-results-01.png)
*A successful test run, proved by the green "Executing function: succeeded" banner and outputs.*

![Lambda log output showing scan details](/images/04-lambda-test-results-02.png)
*Log output from the test run, showing each bucket's encryption status as it was scanned.*

![Lambda response with AI analysis](/images/04-lambda-test-results-03.png)
*The JSON response from the test run, including Gemini's AI-generated security analysis under `ai_analysis`.*

![EventBridge scheduled rule](/images/05-eventbridge-rule.png)
*The `daily-s3-security-scan` EventBridge rule, configured to trigger the Lambda function every 12 hours.*


## Repository Structure
```
ai-security-scanner-s3/
├── README.md                  # This file
├── requirements.txt            # Python dependencies (boto3, google-genai)
├── .gitignore                  # Excludes venv/, package/, zips, .env,
├── src/
│   └── s3_scanner.py           # The Lambda function: scan + AI analysis
├── infrastructure/
│   └── iam/
│       ├── s3-encryption-read-policy.json  # Read-only S3 permissions
│       └── lambda-trust-policy.json        # Lets Lambda assume the role
├── scripts/
│   └── test_event.json                    # Sample event for manual testing
└── images/                                # Images taken from the project
    ├── 01-scanner-code.png
    ├── 01-scanner-code-01.png
    ├── 01-scanner-code-02.png
    ├── 01-scanner-code-03.png
    ├── 01-scanner-code-04.png
    ├── 01-scanner-code-05.png
    ├── 02-iam-role.png
    ├── 03-lambda-test-event.png
    ├── 04-lambda-test-results-01.png
    ├── 04-lambda-test-results-02.png
    ├── 04-lambda-test-results-03.png
    ├── 04-lambda-test-results-03.png
    └── 05-eventbridge-rule.png 
       
```

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


