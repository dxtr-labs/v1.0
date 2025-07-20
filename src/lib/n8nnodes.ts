// lib/n8nNodes.ts

export const NODE_LIST_RAW_JSON = `
[
  {
    "id": "ManualTrigger", // IDs are usually strings in n8n for nodes
    "name": "Manual Trigger",
    "type": "n8n-nodes-base.manualTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
 {
    "id": 2,
    "name": "Cron",
    "type": "n8n-nodes-base.cron",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 3,
    "name": "Interval",
    "type": "n8n-nodes-base.interval",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 4,
    "name": "Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 5,
    "name": "Error Trigger",
    "type": "n8n-nodes-base.errorTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 6,
    "name": "Execute Workflow",
    "type": "n8n-nodes-base.executeWorkflow",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 7,
    "name": "Code",
    "type": "n8n-nodes-base.code",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 8,
    "name": "Function",
    "type": "n8n-nodes-base.function",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 9,
    "name": "Function Item",
    "type": "n8n-nodes-base.functionItem",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 10,
    "name": "If",
    "type": "n8n-nodes-base.if",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 11,
    "name": "Switch",
    "type": "n8n-nodes-base.switch",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 12,
    "name": "Merge",
    "type": "n8n-nodes-base.merge",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 13,
    "name": "Move Binary Data",
    "type": "n8n-nodes-base.moveBinaryData",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 14,
    "name": "Edit Fields (Set)",
    "type": "n8n-nodes-base.editFields",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 15,
    "name": "Aggregate",
    "type": "n8n-nodes-base.aggregate",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 16,
    "name": "Summarize",
    "type": "n8n-nodes-base.summarize",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 17,
    "name": "Compare Datasets",
    "type": "n8n-nodes-base.compareDatasets",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 18,
    "name": "Wait",
    "type": "n8n-nodes-base.wait",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 19,
    "name": "HTTP Request",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 20,
    "name": "Send Email",
    "type": "n8n-nodes-base.sendEmail",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 21,
    "name": "Respond to Webhook",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 22,
    "name": "NoOp",
    "type": "n8n-nodes-base.noop",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 23,
    "name": "Slack",
    "type": "n8n-nodes-base.slack",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 24,
    "name": "Slack Trigger",
    "type": "n8n-nodes-base.slackTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 25,
    "name": "Discord",
    "type": "n8n-nodes-base.discord",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 26,
    "name": "Discord Trigger",
    "type": "n8n-nodes-base.discordTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 27,
    "name": "Microsoft Teams",
    "type": "n8n-nodes-base.microsoftTeams",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 28,
    "name": "Mattermost",
    "type": "n8n-nodes-base.mattermost",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 29,
    "name": "Telegram",
    "type": "n8n-nodes-base.telegram",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 30,
    "name": "Telegram Trigger",
    "type": "n8n-nodes-base.telegramTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 31,
    "name": "Twilio",
    "type": "n8n-nodes-base.twilio",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 32,
    "name": "Twilio Trigger",
    "type": "n8n-nodes-base.twilioTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 33,
    "name": "Gmail",
    "type": "n8n-nodes-base.gmail",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 34,
    "name": "Gmail Trigger",
    "type": "n8n-nodes-base.gmailTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 35,
    "name": "Outlook",
    "type": "n8n-nodes-base.outlook",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 36,
    "name": "Email Read Imap",
    "type": "n8n-nodes-base.emailReadImap",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 37,
    "name": "Email Send",
    "type": "n8n-nodes-base.emailSend",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 38,
    "name": "SMS77",
    "type": "n8n-nodes-base.sms77",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 39,
    "name": "PagerDuty",
    "type": "n8n-nodes-base.pagerduty",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 40,
    "name": "Vonage",
    "type": "n8n-nodes-base.vonage",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 41,
    "name": "WhatsApp",
    "type": "n8n-nodes-base.whatsapp",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 42,
    "name": "EmailJS",
    "type": "n8n-nodes-base.emailjs",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 43,
    "name": "Notion",
    "type": "n8n-nodes-base.notion",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 44,
    "name": "Notion Trigger",
    "type": "n8n-nodes-base.notionTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 45,
    "name": "Airtable",
    "type": "n8n-nodes-base.airtable",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 46,
    "name": "Airtable Trigger",
    "type": "n8n-nodes-base.airtableTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 47,
    "name": "Google Sheets",
    "type": "n8n-nodes-base.googleSheets",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 48,
    "name": "Google Sheets Trigger",
    "type": "n8n-nodes-base.googleSheetsTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 49,
    "name": "Google Calendar",
    "type": "n8n-nodes-base.googleCalendar",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 50,
    "name": "Google Drive",
    "type": "n8n-nodes-base.googleDrive",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 51,
    "name": "Google Drive Trigger",
    "type": "n8n-nodes-base.googleDriveTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 52,
    "name": "Microsoft Outlook",
    "type": "n8n-nodes-base.microsoftOutlook",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 53,
    "name": "Microsoft To Do",
    "type": "n8n-nodes-base.microsoftToDo",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 54,
    "name": "Trello",
    "type": "n8n-nodes-base.trello",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 55,
    "name": "Trello Trigger",
    "type": "n8n-nodes-base.trelloTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 56,
    "name": "Asana",
    "type": "n8n-nodes-base.asana",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 57,
    "name": "Asana Trigger",
    "type": "n8n-nodes-base.asanaTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 58,
    "name": "Monday.com",
    "type": "n8n-nodes-base.mondaycom",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 59,
    "name": "ClickUp",
    "type": "n8n-nodes-base.clickup",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 60,
    "name": "Jira",
    "type": "n8n-nodes-base.jira",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 61,
    "name": "Jira Trigger",
    "type": "n8n-nodes-base.jiraTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 62,
    "name": "Confluence",
    "type": "n8n-nodes-base.confluence",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 63,
    "name": "GitHub Issues",
    "type": "n8n-nodes-base.githubIssues",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 64,
    "name": "Todoist",
    "type": "n8n-nodes-base.todoist",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 65,
    "name": "Calendly",
    "type": "n8n-nodes-base.calendly",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 66,
    "name": "Zoom",
    "type": "n8n-nodes-base.zoom",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 67,
    "name": "Salesforce",
    "type": "n8n-nodes-base.salesforce",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 68,
    "name": "Salesforce Trigger",
    "type": "n8n-nodes-base.salesforceTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 69,
    "name": "HubSpot",
    "type": "n8n-nodes-base.hubspot",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 70,
    "name": "HubSpot Trigger",
    "type": "n8n-nodes-base.hubspotTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 71,
    "name": "Pipedrive",
    "type": "n8n-nodes-base.pipedrive",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 72,
    "name": "Pipedrive Trigger",
    "type": "n8n-nodes-base.pipedriveTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 73,
    "name": "Zoho CRM",
    "type": "n8n-nodes-base.zohoCrm",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 74,
    "name": "Copper",
    "type": "n8n-nodes-base.copper",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 75,
    "name": "Zendesk",
    "type": "n8n-nodes-base.zendesk",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 76,
    "name": "Zendesk Trigger",
    "type": "n8n-nodes-base.zendeskTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 77,
    "name": "Freshdesk",
    "type": "n8n-nodes-base.freshdesk",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 78,
    "name": "Insightly",
    "type": "n8n-nodes-base.insightly",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 79,
    "name": "Keap",
    "type": "n8n-nodes-base.keap",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 80,
    "name": "Zoho CRM",
    "type": "n8n-nodes-base.zohoCrm",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 81,
    "name": "ActiveCampaign",
    "type": "n8n-nodes-base.activecampaign",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 82,
    "name": "ActiveCampaign Trigger",
    "type": "n8n-nodes-base.activecampaignTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 83,
    "name": "Mailchimp",
    "type": "n8n-nodes-base.mailchimp",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 84,
    "name": "Mailchimp Trigger",
    "type": "n8n-nodes-base.mailchimpTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 85,
    "name": "Mautic",
    "type": "n8n-nodes-base.mautic",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 86,
    "name": "Marketo",
    "type": "n8n-nodes-base.marketo",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 87,
    "name": "SendinBlue",
    "type": "n8n-nodes-base.sendinblue",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 88,
    "name": "Google Analytics",
    "type": "n8n-nodes-base.googleAnalytics",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 89,
    "name": "Facebook Graph API",
    "type": "n8n-nodes-base.facebookGraphApi",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 90,
    "name": "Facebook Trigger",
    "type": "n8n-nodes-base.facebookTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 91,
    "name": "Twitter",
    "type": "n8n-nodes-base.twitter",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 92,
    "name": "Twitter Trigger",
    "type": "n8n-nodes-base.twitterTrigger",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 93,
    "name": "LinkedIn",
    "type": "n8n-nodes-base.linkedin",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 94,
    "name": "Instagram",
    "type": "n8n-nodes-base.instagram",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 95,
    "name": "YouTube",
    "type": "n8n-nodes-base.youtube",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 96,
    "name": "Pinterest",
    "type": "n8n-nodes-base.pinterest",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 97,
    "name": "MySQL",
    "type": "n8n-nodes-base.mysql",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 98,
    "name": "PostgreSQL",
    "type": "n8n-nodes-base.postgresql",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 99,
    "name": "Microsoft SQL",
    "type": "n8n-nodes-base.microsoftSql",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 100,
    "name": "MongoDB",
    "type": "n8n-nodes-base.mongodb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 101,
    "name": "Redis",
    "type": "n8n-nodes-base.redis",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 102,
    "name": "SQLite",
    "type": "n8n-nodes-base.sqlite",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 103,
    "name": "Oracle",
    "type": "n8n-nodes-base.oracle",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 104,
    "name": "InfluxDB",
    "type": "n8n-nodes-base.influxdb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 105,
    "name": "DynamoDB",
    "type": "n8n-nodes-base.dynamodb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 106,
    "name": "Google BigQuery",
    "type": "n8n-nodes-base.googleBigquery",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 107,
    "name": "Snowflake",
    "type": "n8n-nodes-base.snowflake",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 108,
    "name": "Firebase Realtime DB",
    "type": "n8n-nodes-base.firebaseRealtimeDb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 109,
    "name": "Firestore",
    "type": "n8n-nodes-base.firestore",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 110,
    "name": "ElasticSearch",
    "type": "n8n-nodes-base.elasticsearch",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 111,
    "name": "FaunaDB",
    "type": "n8n-nodes-base.faunadb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 112,
    "name": "AWS S3",
    "type": "n8n-nodes-base.awsS3",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 113,
    "name": "Dropbox",
    "type": "n8n-nodes-base.dropbox",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 114,
    "name": "Box",
    "type": "n8n-nodes-base.box",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 115,
    "name": "Nextcloud",
    "type": "n8n-nodes-base.nextcloud",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 116,
    "name": "FTP",
    "type": "n8n-nodes-base.ftp",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 117,
    "name": "SFTP",
    "type": "n8n-nodes-base.sftp",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 118,
    "name": "GitHub",
    "type": "n8n-nodes-base.github",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 119,
    "name": "Baserow",
    "type": "n8n-nodes-base.baserow",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 120,
    "name": "NocoDB",
    "type": "n8n-nodes-base.nocodb",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 121,
    "name": "Oracle Netsuite",
    "type": "n8n-nodes-base.oracleNetsuite",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 122,
    "name": "GitHub",
    "type": "n8n-nodes-base.github",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 123,
    "name": "GitLab",
    "type": "n8n-nodes-base.gitlab",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 124,
    "name": "Bitbucket",
    "type": "n8n-nodes-base.bitbucket",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 125,
    "name": "Jenkins",
    "type": "n8n-nodes-base.jenkins",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 126,
    "name": "CircleCI",
    "type": "n8n-nodes-base.circleci",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 127,
    "name": "Travis CI",
    "type": "n8n-nodes-base.travisCi",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 128,
    "name": "Docker",
    "type": "n8n-nodes-base.docker",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 129,
    "name": "Kubernetes",
    "type": "n8n-nodes-base.kubernetes",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 130,
    "name": "AWS Lambda",
    "type": "n8n-nodes-base.awsLambda",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 131,
    "name": "AWS EC2",
    "type": "n8n-nodes-base.awsEc2",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 132,
    "name": "Azure",
    "type": "n8n-nodes-base.azure",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 133,
    "name": "SSH",
    "type": "n8n-nodes-base.ssh",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 134,
    "name": "DigitalOcean",
    "type": "n8n-nodes-base.digitalocean",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 135,
    "name": "Docker Hub",
    "type": "n8n-nodes-base.dockerHub",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 136,
    "name": "Stripe",
    "type": "n8n-nodes-base.stripe",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 137,
    "name": "PayPal",
    "type": "n8n-nodes-base.paypal",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 138,
    "name": "Razorpay",
    "type": "n8n-nodes-base.razorpay",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 139,
    "name": "QuickBooks",
    "type": "n8n-nodes-base.quickbooks",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 140,
    "name": "Xero",
    "type": "n8n-nodes-base.xero",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 141,
    "name": "Zoho Books",
    "type": "n8n-nodes-base.zohoBooks",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 142,
    "name": "FreshBooks",
    "type": "n8n-nodes-base.freshbooks",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 143,
    "name": "CoinGecko",
    "type": "n8n-nodes-base.coingecko",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 144,
    "name": "Coinmarketcap",
    "type": "n8n-nodes-base.coinmarketcap",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 145,
    "name": "Binance",
    "type": "n8n-nodes-base.binance",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 146,
    "name": "Komodo",
    "type": "n8n-nodes-base.komodo",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 147,
    "name": "Mixpanel",
    "type": "n8n-nodes-base.mixpanel",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 148,
    "name": "Amplitude",
    "type": "n8n-nodes-base.amplitude",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 149,
    "name": "Matomo",
    "type": "n8n-nodes-base.matomo",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 150,
    "name": "OpenAI",
    "type": "n8n-nodes-base.openai",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 151,
    "name": "Azure OpenAI",
    "type": "n8n-nodes-base.azureOpenai",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 152,
    "name": "Hugging Face",
    "type": "n8n-nodes-base.huggingFace",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 153,
    "name": "LangChain",
    "type": "n8n-nodes-base.langchain",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 154,
    "name": "Stability",
    "type": "n8n-nodes-base.stability",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 155,
    "name": "ElevenLabs",
    "type": "n8n-nodes-base.elevenlabs",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 156,
    "name": "DeepL",
    "type": "n8n-nodes-base.deepl",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 157,
    "name": "IBM Watson",
    "type": "n8n-nodes-base.ibmWatson",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 158,
    "name": "Microsoft Azure AI",
    "type": "n8n-nodes-base.microsoftAzureAi",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 159,
    "name": "Google Vision",
    "type": "n8n-nodes-base.googleVision",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 160,
    "name": "AWS Rekognition",
    "type": "n8n-nodes-base.awsRekognition",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 161,
    "name": "AWS Comprehend",
    "type": "n8n-nodes-base.awsComprehend",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 162,
    "name": "Sentence Similarity",
    "type": "n8n-nodes-base.sentenceSimilarity",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 163,
    "name": "CrowdStrike Falcon",
    "type": "n8n-nodes-base.crowdstrikeFalcon",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 164,
    "name": "VirusTotal",
    "type": "n8n-nodes-base.virustotal",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 165,
    "name": "Have I Been Pwned",
    "type": "n8n-nodes-base.haveIBeenPwned",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 166,
    "name": "AWS Security Hub",
    "type": "n8n-nodes-base.awsSecurityHub",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 167,
    "name": "Azure Sentinel",
    "type": "n8n-nodes-base.azureSentinel",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 168,
    "name": "Cisco Webex",
    "type": "n8n-nodes-base.ciscoWebex",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 169,
    "name": "LDAP",
    "type": "n8n-nodes-base.ldap",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 170,
    "name": "Snyk",
    "type": "n8n-nodes-base.snyk",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 171,
    "name": "Tenable",
    "type": "n8n-nodes-base.tenable",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  },
  {
    "id": 172,
    "name": "GitHub Security",
    "type": "n8n-nodes-base.githubSecurity",
    "typeVersion": 1,
    "position": [
      0,
      0
    ],
    "parameters": {}
  }
]
`;

interface N8nNodeTemplate {
  id: string; // Ensure ID is string for n8n compatibility
  name: string;
  type: string;
  typeVersion: number;
  position: [number, number];
  parameters: { [key: string]: any };
}

export const NODE_TEMPLATES: { [name: string]: N8nNodeTemplate } = {};
export const KEYWORD_MAP: { [word: string]: string[] } = {};

try {
  const parsedNodes: N8nNodeTemplate[] = JSON.parse(NODE_LIST_RAW_JSON);
  parsedNodes.forEach(node => {
    NODE_TEMPLATES[node.name] = node;
    const words = node.name.toLowerCase().match(/[a-z]+/g) || [];
    words.forEach(word => {
      if (!KEYWORD_MAP[word]) {
        KEYWORD_MAP[word] = [];
      }
      KEYWORD_MAP[word].push(node.name);
    });
  });
} catch (e) {
  console.error("Failed to parse NODE_LIST_RAW_JSON:", e);
}


// Helper for KEYWORD_MAP.setdefault
if (!Object.prototype.hasOwnProperty.call(Object.prototype, 'setdefault')) {
  Object.defineProperty(Object.prototype, 'setdefault', {
    value: function(key: string, defaultValue: any) {
      if (!this.hasOwnProperty(key)) {
        this[key] = defaultValue;
      }
      return this[key];
    },
    enumerable: false
  });
}


export function matchNodes(text: string): N8nNodeTemplate[] {
  const words = new Set((text.toLowerCase().match(/[a-z]+/g) || []));
  const matchedNames = new Set<string>();
  for (const word of words) {
    (KEYWORD_MAP[word] || []).forEach(name => matchedNames.add(name));
  }
  return Array.from(matchedNames).map(name => NODE_TEMPLATES[name]);
}