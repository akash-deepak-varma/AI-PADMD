# 🌐 Running the Project with ngrok (Demo Mode)

This project normally runs **locally** (Node.js + FastAPI + MySQL).  
For demo purposes, we can expose the local Node.js server to the internet using [ngrok](https://ngrok.com/).  

---

## ⚙️ Steps to Run with ngrok

### 1. Install ngrok
Download and install from [ngrok download page](https://ngrok.com/download) or via npm:
```bash
npm install -g ngrok

2. Authenticate ngrok

Add your authtoken (you get this from your ngrok dashboard):

ngrok config add-authtoken YOUR_AUTHTOKEN

3. Start Local Servers

Run your backend services:

# Start FastAPI (Python, port 8000)
uvicorn main:app --reload --port 8000

# Start Node.js (Express, port 8001)
node server.js

4. Expose Node.js with ngrok

Run:

ngrok http 8001


This will generate a public HTTPS URL, e.g.:

https://random-id.ngrok-free.app