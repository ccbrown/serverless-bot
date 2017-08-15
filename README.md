# serverless-bot

* Create an AWS account, install the CLI, and configure your credentials via `aws configure`.
* Install the [Serverless Framework](https://serverless.com/): `npm install serverless -g`
* Clone this repo, `cd` to it, and run `npm install` to install the [serverless-python-requirements](https://www.npmjs.com/package/serverless-python-requirements) plugin for Serverless.
* Deploy the bot: `serverless deploy -v`
* Use the URL in the output of the deploy command as an outgoing webhook in Slack or Mattermost.
