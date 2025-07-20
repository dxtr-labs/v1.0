# backend/mcp/node_specs.py
# Defines node type specs (parameters, optional fields, examples)

NODE_SPECS = {
    "manualTrigger": {
        "required": [],
        "optional": [],
        "example": {
            "name": "Manual Trigger",
            "type": "manualTrigger",
            "parameters": {}
        }
    },
    "cron": {
        "required": ["interval"],
        "optional": ["timezone"],
        "example": {
            "name": "Daily Trigger",
            "type": "cron",
            "parameters": {
                "interval": "0 9 * * *",
                "timezone": "UTC"
            }
        }
    },
    "if": {
        "required": ["valueA", "valueB", "operation"],
        "optional": [],
        "example": {
            "name": "Condition",
            "type": "if",
            "parameters": {
                "valueA": "{{setNode.status}}",
                "valueB": "active",
                "operation": "equals"
            }
        }
    },
    "set": {
        "required": ["fields"],
        "optional": [],
        "example": {
            "name": "Set Data",
            "type": "set",
            "parameters": {
                "fields": {
                    "status": "active",
                    "count": 5
                }
            }
        }
    },
    "emailSend": {
        "required": ["to", "subject", "body"],
        "optional": ["from"],
        "example": {
            "name": "Send Email",
            "type": "emailSend",
            "parameters": {
                "to": "user@example.com",
                "subject": "Welcome",
                "body": "Thanks for signing up!"
            }
        }
    },
    "emailReadIMAPTrigger": {
        "required": ["imap_host", "imap_port", "username", "password"],
        "optional": ["folder"],
        "example": {
            "name": "Read Email",
            "type": "emailReadIMAPTrigger",
            "parameters": {
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "username": "me@gmail.com",
                "password": "********",
                "folder": "INBOX"
            }
        }
    },
    "twilio": {
        "required": ["to", "message"],
        "optional": ["from"],
        "example": {
            "name": "Send SMS",
            "type": "twilio",
            "parameters": {
                "to": "+1234567890",
                "message": "Hello from Twilio"
            }
        }
    },
    "slack": {
        "required": ["channel", "message"],
        "optional": [],
        "example": {
            "name": "Slack Notify",
            "type": "slack",
            "parameters": {
                "channel": "#general",
                "message": "Deployment succeeded"
            }
        }
    },
    "discord": {
        "required": ["webhook_url", "message"],
        "optional": [],
        "example": {
            "name": "Discord Notify",
            "type": "discord",
            "parameters": {
                "webhook_url": "https://discord.com/api/webhooks/...",
                "message": "New order placed"
            }
        }
    },
    "pushNotification": {
        "required": ["to", "title", "message"],
        "optional": ["service"],
        "example": {
            "name": "Push Alert",
            "type": "pushNotification",
            "parameters": {
                "to": "user-id",
                "title": "Alert",
                "message": "Your task is complete"
            }
        }
    },
    "openai": {
        "required": ["prompt"],
        "optional": ["model", "temperature"],
        "example": {
            "name": "OpenAI",
            "type": "openai",
            "parameters": {
                "prompt": "Summarize this article.",
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
    },
    "claude": {
        "required": ["prompt"],
        "optional": ["version"],
        "example": {
            "name": "Claude Summary",
            "type": "claude",
            "parameters": {
                "prompt": "Summarize the meeting.",
                "version": "claude-2"
            }
        }
    },
    "summarizer": {
        "required": ["text"],
        "optional": [],
        "example": {
            "name": "Summarize",
            "type": "summarizer",
            "parameters": {
                "text": "Long article..."
            }
        }
    },
    "textSplitter": {
        "required": ["text"],
        "optional": ["chunk_size"],
        "example": {
            "name": "Split Text",
            "type": "textSplitter",
            "parameters": {
                "text": "Paragraph...",
                "chunk_size": 512
            }
        }
    },
    "promptRouter": {
        "required": ["input"],
        "optional": ["fallback_model"],
        "example": {
            "name": "Prompt Router",
            "type": "promptRouter",
            "parameters": {
                "input": "Classify sentiment",
                "fallback_model": "gpt-3.5"
            }
        }
    },
    "googleDrive": {
        "required": ["action", "fileId"],
        "optional": [],
        "example": {
            "name": "Download File",
            "type": "googleDrive",
            "parameters": {
                "action": "download",
                "fileId": "1A2B3C"
            }
        }
    },
    "s3Storage": {
        "required": ["bucket", "action"],
        "optional": ["key", "fileContent"],
        "example": {
            "name": "S3 Upload",
            "type": "s3Storage",
            "parameters": {
                "bucket": "my-bucket",
                "action": "upload",
                "key": "file.txt",
                "fileContent": "base64string=="
            }
        }
    },
    "pdfExtract": {
        "required": ["filePath"],
        "optional": [],
        "example": {
            "name": "Extract PDF",
            "type": "pdfExtract",
            "parameters": {
                "filePath": "/path/to/file.pdf"
            }
        }
    },
    "csvParser": {
        "required": ["csvData"],
        "optional": ["delimiter"],
        "example": {
            "name": "CSV Parse",
            "type": "csvParser",
            "parameters": {
                "csvData": "name,age\nAlice,30",
                "delimiter": ","
            }
        }
    },
    
    "googleSheets": {
        "required": ["sheetId", "action"],
        "optional": ["range", "values"],
        "example": {
            "name": "Append Row",
            "type": "googleSheets",
            "parameters": {
                "sheetId": "1xyz",
                "action": "append",
                "range": "Sheet1!A1:D1",
                "values": ["Name", "Email"]
            }
        }
    }    
}
