# Superpowered AI SMS Assistant built on AWS (infra) and Twilio (sms)

_Superpowered AI is in a free research beta phase. Please join our Discord server for asking questions, giving feedback, talking about ideas, or just to say hey!: https://discord.com/invite/PD6qE85kch_

**In this demo, we will build an AI assistant with a dedicated phone number (issued via Twilio).**

**Users simply text the AI's number and an individual  "[chat thread](!https://docs.superpowered.ai/api/rest/index.html#tag/Chat)" will be created and tied to the end-user's phone number using the API's `supp_id` field. No need to maintain chat histories on your own. That is taken care of by Superpowered.**

Feel free to text 844-603-7222 to interact with an AI assistant we've created from the steps outlined below.

**Tech stack is AWS Serverless. No need to keep a server up and running to respond to Twilio webhooks.**

To get more familiar with the key concepts behind Superpowered, please visit our conceptual docs: https://superpoweredai.notion.site/

Take a look at our API Reference: https://docs.superpowered.ai/api/rest/index.html



### High-level overview

Set up Twilio account so you have can access their services via API. This will allow us to receive and respond to text messages from a specific number.

Set up AWS account because that's where we'll host our service. We are deploying via AWS SAM (Serverless Application Model). This way, you only pay for what you use and AWS has a generous free tier.

_NOTE: We're using AWS SAM here because of the general ease to get things deployed into production quickly and reliably. You could certainly set up a server in some other way to receive webhooks and respond to SMS messages._

The following resources will be created from `resources.yaml`

- A Lambda function (with it's own URL) that will take the incoming message and use the Superpowered AI API `/chat/threads/{thread_id}/get_response` endpoint to get an AI response to the message a user sent to your Twilio number.

Things you'll need to do before you can deploy your AI SMS Assistant:

1. Setup your Twilio account and register a phone number:
    - https://www.twilio.com/try-twilio
    - Get your "Account SID" and "Auth Token" from the Twilio Console: https://twilio.com/console
    - Create a phone number via the console or via the CLI: https://www.twilio.com/blog/register-phone-number-send-sms-twilio-cli
2. Create an AWS account and download the SAM CLI:
    - https://aws.amazon.com/free/
    - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    - https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Create your Superpowered.ai account and API keys:
    - https://superpowered.ai/
    - Login and click "Account" on the left navigation and then click "Create new API key"
    - Run `aws configure` on the command line to configure AWS credentials and default region.
4. Make sure you have `jq` enabled to run the `deploy.sh` script: https://jqlang.github.io/jq/download/

5. Deploy your SMS Assistant.

Be sure to pass your secret parameters (as shown below) the first time you run the deployment to make sure the secrets get saved in AWS properly.

```bash
sh deploy.sh \ 
    --twilio-phone-number +1XXXXXXXXXX \                # REQUIRED
    --twilio-account-sid INSERT_TWILIO_ACCOUNT_SID \    # OPTIONAL (make sure you set this the first time you run the script)
    --twilio-auth-token INSERT_TWILIO_AUTH_TOKEN \      # OPTIONAL (make sure you set this the first time you run the script)
    --sp-api-key-id INSERT_SP_API_KEY_ID \              # OPTIONAL (make sure you set this the first time you run the script)
    --sp-api-key-secret INSERT_SP_API_KEY_SECRET        # OPTIONAL (make sure you set this the first time you run the script)
```

This script will perform the following steps:

- Create secure parameters in AWS System's Manager Parameter Store (will be accessed by our responder)
- Deploy our AWS resources defined in `resources.yaml`
- Updates webhook to match the URL of the webhook listener Lambda function

### Extending The SMS AI Assistant

Here are some ideas for how you can use this demo to create a full-fledge product or business:

##### Multi-Channel Conversations

Instead of just mapping a phone number to a Superpowered [Chat Thread](!https://docs.superpowered.ai/api/rest/index.html#tag/Chat), you can have any number of identifiers for users. For example, if you map email, phone, Discord username, etc. to the same chat thread, the AI agent will maintain a single conversational thread across multiple channels.


##### Customer Support

Add [knowledge bases](!https://docs.superpowered.ai/api/rest/index.html#tag/Create-Knowledge-Base) with information specific to your organization. Your AI assistant will be able to text existing and potential customers.


##### Add custom utilities

Create a list of tools/utilities so that users can send messages with a particular keyword, emoji, etc. to get a specific kind of response.

Some ideas:

- A :art: emoji could connect to an image generation API and reply to users with an image based on the prompt they give.
- A :gear: emoji could be a settings/account indicator
- A :wrench: emoji could be a way to alter some settings
- A :wastebasket: emoji to reset chat thread options


##### Add a billing workflow when users text the SMS assistant for the first time

One idea is to use Stripe's "Payment Links" feature: https://stripe.com/payments/payment-links

