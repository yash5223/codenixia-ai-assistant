from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3, os, smtplib
from email.mime.text import MIMEText
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="Codenixia AI Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYSTEM_PROMPT = (
    "You are a professional AI business assistant for Codenixia, a tech services company. "
    "Help users with business queries, services, pricing, tech solutions, and general business topics. "
    "Be concise, helpful, and professional."
)

def db():
    c = sqlite3.connect(Path(__file__).parent / "data.db")
    c.row_factory = sqlite3.Row
    return c

with db() as c:
    c.execute("CREATE TABLE IF NOT EXISTS leads(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT,phone TEXT,company TEXT,message TEXT,ts TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY AUTOINCREMENT,user TEXT,bot TEXT,ts TEXT)")

class Lead(BaseModel):
    name: str
    email: str
    phone: str
    company: str = ""
    message: str = ""

class Chat(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
async def chat(req: Chat):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += req.history[-10:]
    messages.append({"role": "user", "content": req.message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=800,
    )
    reply = response.choices[0].message.content

    with db() as c:
        c.execute("INSERT INTO chats(user,bot,ts) VALUES(?,?,?)", (req.message, reply, datetime.now().isoformat()))
    return {"reply": reply}

@app.post("/api/leads")
async def create_lead(req: Lead):
    with db() as c:
        c.execute("INSERT INTO leads(name,email,phone,company,message,ts) VALUES(?,?,?,?,?,?)",
                  (req.name, req.email, req.phone, req.company, req.message, datetime.now().isoformat()))
    notify(req)
    return {"status": "success", "msg": "Thank you! Our team will contact you within 24 hours."}

def notify(lead: Lead):
    u, p = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")
    if not u or not p:
        return
    try:
        body = f"New Lead Captured\n\nName: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone}\nCompany: {lead.company}\n\nMessage:\n{lead.message}"
        m = MIMEText(body)
        m["Subject"] = f"New Lead: {lead.name} — Codenixia"
        m["From"] = u
        m["To"] = u
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(u, p)
            s.send_message(m)
    except Exception:
        pass

@app.get("/api/leads")
async def get_leads():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM leads ORDER BY ts DESC").fetchall()]

@app.get("/api/stats")
async def stats():
    with db() as c:
        leads = c.execute("SELECT COUNT(*) as n FROM leads").fetchone()["n"]
        chats = c.execute("SELECT COUNT(*) as n FROM chats").fetchone()["n"]
        today = datetime.now().date().isoformat()
        today_leads = c.execute("SELECT COUNT(*) as n FROM leads WHERE ts LIKE ?", (f"{today}%",)).fetchone()["n"]
        return {"leads": leads, "chats": chats, "today_leads": today_leads}

app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "static"), html=True), name="static")
