# Botpress Webchat Integration Guide

This guide explains how to connect the Botpress webchat widget to the SmileBot FastAPI backend.

## Overview

Botpress acts as the **frontend chat UI only**. All AI logic lives in your FastAPI backend on Render. Botpress sends every user message to your `/chat` endpoint and displays the response.

## Step-by-Step Setup

### 1. Create a Botpress Bot

1. Go to [botpress.com](https://botpress.com) and sign up (free).
2. Create a new bot (e.g., "SmileBot").

### 2. Create the Webhook Flow

In the Botpress Studio:

1. **Add a "Start" node** (auto-created).
2. **Add an "Execute Code" card** that sends the user message to your Render backend:

```javascript
// Execute Code card in Botpress
const axios = require('axios');

const BACKEND_URL = 'https://smilebot-api.onrender.com/chat';  // Replace with your Render URL

// Generate a session ID per conversation
const sessionId = event.userId || event.conversationId || 'default';

try {
  const response = await axios.post(BACKEND_URL, {
    session_id: sessionId,
    message: event.preview  // The user's message text
  });

  // Store the reply so a Text card can display it
  workflow.botReply = response.data.reply;
} catch (error) {
  workflow.botReply = "I'm sorry, I'm having a little trouble right now. Please call us at 1-910-347-9100 and we'll be happy to help!";
}
```

3. **Add a "Text" card** after the Execute Code card that displays `{{workflow.botReply}}`.
4. **Loop back** to the same node so the conversation continues.

### 3. Alternative: Use the Botpress API Integration (Webhook)

If you prefer using Botpress's built-in **Webhook** or **API** integration:

1. In your bot settings, go to **Integrations** → **Webhook**.
2. Set the webhook URL to: `https://smilebot-api.onrender.com/chat`
3. Configure it to POST the user message in the format:
   ```json
   {
     "session_id": "{{event.conversationId}}",
     "message": "{{event.preview}}"
   }
   ```

### 4. Embed the Widget on the Clinic Website

Once your bot is published in Botpress, grab the embed code from **Integrations → Webchat** and paste it into the clinic's website HTML:

```html
<!-- Paste this just before </body> -->
<script src="https://cdn.botpress.cloud/webchat/v2.3/inject.js"></script>
<script src="https://files.bpcontent.cloud/YOUR_BOT_ID/webchat/v2.3/config.js"></script>
```

Replace `YOUR_BOT_ID` with your actual Botpress bot ID.

### 5. Customize the Widget (Optional)

You can customize colors and branding in the Botpress dashboard under **Webchat Settings**:
- Bot name: `SmileBot`
- Avatar: Use the clinic logo
- Primary color: Match the clinic's branding
- Welcome message: `Hi there! 😊 Welcome to A Beautiful Smile. How can I help you today?`

## Testing

1. Make sure your Render backend is running (`/health` returns `{"status": "ok"}`).
2. Open the Botpress webchat preview.
3. Send a test message like "What services do you offer?"
4. Verify the response comes from Gemini via your backend.
5. Test the full booking flow — confirm the email arrives at the configured address.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Bot shows error message | Check that your Render service is awake (free tier sleeps after inactivity) |
| CORS error in browser | The backend already allows all origins; verify the Render URL is correct |
| No email received | Check `SMTP_EMAIL` and `SMTP_APP_PASSWORD` env vars on Render |
| Slow first response | Free-tier Render services spin down after ~15 min of inactivity; first request takes ~30s |
