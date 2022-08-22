# Integrated Value Challenges for CTFd

Salesforce integrated challenge base. This is a two phase challenge that posts an HMAC signed request to a challenge evaluator endpoint and accepts a redirect back from the challenge evaluator endpoint with a flag result in the URL parameter *testResult*.  


# Installation

**REQUIRES: CTFd >= v3.5.0**

1. Clone this repository to `CTFd/plugins`. It is important that the folder is
named `integrated_challenges` so CTFd can serve the files in the `assets`
directory.
2. Implement the evaluator service that meets the OpenAPI specification included in this repository
3. Create integrated challenges for your CTF
 
