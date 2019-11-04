## Steps for creating a Lambda function

* Create the function on console
* Add git layer (to enable git commands)
* On Amazon Linux and same python version, pip install required packages into a directory
* Add a lambda_function.py stub inside
* Zip it and upload

## Reacting to events

* Create to a CloudWatch rule to trigger the lambda function
* A cron rule that triggers at regular intervals is "15 9 * * ? *", every day at 9:15 UTC