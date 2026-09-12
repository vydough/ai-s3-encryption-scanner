# Threat Detection Using AWS GuardDuty
This repo is showcases my hands-on cloud security epxloration where I deployed a deliverately vulnerable web app on AWS, attacked it and used Amazon GuardDuty to detect and analyse attacks

## Overview

In this project, I deployed an intentionally insecure copy of the [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) web app on AWS using an AWS CloudFormation template. Once it was running, I switched into "attacker mode" and exploited two real, well-known web vulnerabilities — SQL injection and command injection — to steal temporary AWS credentials from the web server and use them to access private data stored in an S3 bucket.

After completing the attack, I switched back to the defender's perspective and used **Amazon GuardDuty**, AWS's threat detection service, to check whether it picked up on the attack, and to work through exactly what it found and why.

This project is based on the *Threat Detection with GuardDuty* project from [NextWork](https://learn.nextwork.org/projects/aws-security-guardduty), which I completed as part of my own learning in AWS and cloud security.

## Project Purpose

I did this project to get hands-on experience with how common web application attacks actually work, why they succeed against poorly secured infrastructure, and how AWS's built-in threat detection tools can identify that kind of activity after the fact. It also gave me practical, guided experience with several core AWS services that come up constantly in cloud and security-focused roles: CloudFormation, EC2, S3, CloudFront, IAM, CloudShell and GuardDuty.

## Objectives

- Deploy a multi-resource AWS environment from a CloudFormation template instead of creating everything manually.
- Exploit an SQL injection vulnerability to bypass a login form without a valid password.
- Exploit a command injection vulnerability to steal temporary IAM credentials from an EC2 instance.
- Use the stolen credentials to access a private S3 bucket and read confidential data, simulating a real data breach.
- Enable and analyse GuardDuty findings to confirm the exact attack that took place.
- (Secret mission) Enable GuardDuty Malware Protection for S3 and confirm it flags a test malware file.

## Key Concepts & Technologies Used

- **Amazon GuardDuty** — a threat detection service that uses machine learning to continuously monitor an AWS account for suspicious activity, such as unusual API calls or credential use. It's the main service this project is built around, since the whole point of the lab is to see what GuardDuty catches.
- **AWS CloudFormation** — an infrastructure-as-code service. Instead of clicking through the console to create every resource by hand, CloudFormation reads a template file and creates, updates or deletes the described resources automatically. This project uses a template to deploy all 27 resources that make up the vulnerable web app in one go.
- **Amazon EC2** — the virtual server that hosts the Juice Shop web app and processes incoming requests.
- **Amazon S3** — used here as a storage bucket holding a file that simulates confidential company data, which becomes the target of the simulated data breach.
- **Amazon CloudFront** — a content delivery network that AWS uses in this template to serve the web app through a public URL.
- **AWS IAM** — manages the permissions (temporary credentials) that let the EC2 instance talk to other AWS services, and which end up being the credentials stolen during the attack.
- **AWS CloudShell** — a browser-based terminal built into the AWS Management Console, used here to run AWS CLI commands with the stolen credentials.
- **OWASP Juice Shop** — an intentionally vulnerable web application built by the OWASP Foundation for security training. It's a safe, legal target to practise attacking.

## Architecture

The CloudFormation template deploys 27 resources, grouped into three categories:

1. **Web app infrastructure** — an EC2 instance running the Juice Shop app, along with its own dedicated VPC, subnets, security group, load balancer, auto scaling group and a CloudFront distribution that gives the app a public URL.
2. **S3 storage** — a bucket containing a text file that stands in for sensitive company data, which the EC2 instance has permission to read.
3. **Security monitoring** — GuardDuty, enabled automatically to monitor the whole environment for threats.

A full breakdown of how these pieces connect is in [`docs/architecture.md`](docs/architecture.md).

## Repository Structure

```
threat-detection-aws-guardduty/
├── README.md                  # Project overview (this file)
├── LICENSE                    # MIT license
├── .gitignore                 # Files excluded from version control
├── docs/                      # Detailed write-ups of each stage of the project
│   ├── architecture.md            # How the deployed AWS resources fit together
│   ├── attack-methodology.md      # Step-by-step walkthrough of the simulated attack
│   ├── guardduty-findings.md      # GuardDuty's findings and what they mean
│   ├── security-considerations.md # Why the app was vulnerable and how to fix it
│   ├── secret-mission-malware-protection.md # Optional GuardDuty Malware Protection extension
│   ├── cleanup-and-cost-management.md       # Resources deleted after the project
│   └── reflection-log.md          # My own answers and takeaways from each stage
├── scripts/                   # Reference commands used during the project
│   └── cloudshell-attack-commands.sh
├── infrastructure/            # Notes on the CloudFormation template used
│   └── README.md
└── assets/
    └── screenshots/           # Evidence captured while completing the project
        └── README.md
```

## Methodology

The project was split into five main steps, carried out in order:

1. **Deploy the web app** — Uploaded the CloudFormation template through the AWS Console and deployed the vulnerable Juice Shop environment.
2. **Log into the web app** — Opened the deployed app and used an SQL injection payload (`' or 1=1;--`) in the email field to bypass the login form and access the admin account without a valid password.
3. **Exploit the web app** — Injected a malicious JavaScript command into the admin profile's username field. Because the app didn't sanitise this input, the server executed it, pulling the EC2 instance's temporary IAM credentials from the instance metadata service and saving them to a publicly accessible file.
4. **Steal data with stolen credentials** — Used AWS CloudShell to download the exposed credentials file, configured a new AWS CLI profile with them, and used that profile to copy and read a confidential file from the S3 bucket.
5. **Detect the attack with GuardDuty** — Switched back to the defender's role and reviewed the GuardDuty finding that was generated, analysing what it detected and how.

The full walkthrough, including the exact commands and payloads used, is documented in [`docs/attack-methodology.md`](docs/attack-methodology.md).

## GuardDuty Findings

GuardDuty flagged the attack as `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.InsideAWS` — meaning it detected that credentials belonging to the EC2 instance were being used from a different AWS account (CloudShell runs under a temporary, separate account ID), which is exactly what happened when the stolen credentials were used to access the S3 bucket. Full details, including severity and what each part of the finding means, are in [`docs/guardduty-findings.md`](docs/guardduty-findings.md).

## Evidence

Screenshots taken while completing each step (stack deployment, the SQL injection login, the exposed credentials file, the CloudShell attack, and the GuardDuty finding) are stored in [`assets/screenshots/`](assets/screenshots/), along with a checklist describing what each one shows.

## Security Considerations

This project deliberately targets an insecure application, so it's a good example of how small gaps add up to a serious breach:

- **No input sanitisation** on the login form allowed SQL injection to bypass authentication entirely.
- **No input validation** on the username field allowed command injection, letting arbitrary code run on the server.
- **Overly broad IAM permissions and exposed instance metadata** meant that once the server was compromised, its AWS credentials were compromised too.
- **No encryption or access restrictions** on the file created by the malicious script meant the stolen credentials were publicly downloadable.

In a real environment, this chain could be broken at several points: using parameterised queries and an ORM to prevent SQL injection, validating and sanitising all user input, enforcing IMDSv2 (which makes instance metadata harder to steal via SSRF-style attacks), applying least-privilege IAM roles so a compromised instance can't reach sensitive resources, and adding a Web Application Firewall (AWS WAF) in front of the app. More detail is in [`docs/security-considerations.md`](docs/security-considerations.md).

## Secret Mission: Malware Protection

As an extension, I also enabled GuardDuty's Malware Protection for S3, uploaded a harmless EICAR test file to the bucket, and confirmed that GuardDuty flagged it. Notes on this are in [`docs/secret-mission-malware-protection.md`](docs/secret-mission-malware-protection.md).

## Cleanup & Cost Management

All resources created for this project were deleted after completion to avoid ongoing AWS charges, including the CloudFormation stack, the auto-generated S3 template bucket, and any temporary credential files created during the attack. Details are in [`docs/cleanup-and-cost-management.md`](docs/cleanup-and-cost-management.md).

## What I Learned

See [`docs/reflection-log.md`](docs/reflection-log.md) for my own notes and takeaways from each stage of the project.

## Future Improvements

- Add an AWS WAF in front of CloudFront to block common injection payloads before they reach the app.
- Set up an EventBridge rule to automatically notify a Slack channel or email address when GuardDuty raises a new finding.
- Try GuardDuty's other protection plans (such as EKS Protection or RDS Protection) in a similar guided lab.
- Explore more of the OWASP Juice Shop's built-in challenges to practise identifying other vulnerability types.

## References

- [Amazon GuardDuty documentation](https://aws.amazon.com/guardduty/)
- [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
- [Amazon S3 documentation](https://aws.amazon.com/s3/)
- [Amazon CloudFront documentation](https://aws.amazon.com/cloudfront/)
- [OWASP Juice Shop project](https://owasp.org/www-project-juice-shop/)

