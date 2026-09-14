# MeetWise 🗓️

## Intelligent Meeting Scheduling & Management Platform

MeetWise is a web-based meeting management platform designed to make scheduling easier by considering participant availability, existing meetings, working-hour constraints, time preferences, meeting priority, optional participants, and scheduling buffers.

The project combines a web frontend with a **Python Flask backend** and a custom **rule-based scheduling engine** that generates and ranks suitable meeting slots.

---

# 🎯 Problem Statement

Scheduling a meeting between multiple people can become difficult when everyone has different availability, working hours, preferences, and existing commitments.

MeetWise aims to simplify this process by automatically checking these constraints and suggesting suitable meeting slots instead of requiring users to manually compare schedules.

---

# 💡 Solution

MeetWise provides a centralized platform where users can:

* Manage their profiles
* Set their availability
* Create meetings
* Add participants
* Define meeting duration and priority
* Set scheduling constraints
* Find suitable meeting slots automatically
* Select a proposed meeting slot
* Accept or decline meeting invitations
* Handle emergency unavailability
* Create and manage communities

The scheduling engine evaluates possible time slots and ranks them according to multiple factors.

---

# ✨ Features

## 👤 User & Profile Management

Users can create and update profile information including:

* Name
* Profile picture
* Email
* Phone number
* Preferred meeting platform
* Notification preferences
* Theme preference

### API

```text
GET  /api/users
POST /api/users
PUT  /api/users/<user_id>
```

---

# ⏰ Availability Management

Users can specify when they are available or unavailable.

Availability information contains:

* User ID
* Date
* Start time
* End time
* Status

Supported statuses include:

```text
available
unavailable
emergency
```

### API

```text
POST /api/availability
GET  /api/availability/<user_id>
```

The scheduler uses this information when searching for suitable meeting slots.

---

# 📅 Meeting Management

Meetings can contain:

* Title
* Agenda
* Organizer
* Participants
* Date
* Duration
* Priority
* Buffer time
* Scheduling constraints
* Selected slot
* Meeting status

### API

```text
GET  /api/meetings
POST /api/meetings
```

---

# 🧠 Intelligent Meeting Scheduler

The core feature of MeetWise is its scheduling engine.

The scheduler is implemented in:

```text
backend/scheduler.py
```

It searches for suitable meeting times at **15-minute intervals**.

For every possible slot, it checks:

1. Working-hour restrictions
2. Required participant availability
3. Existing meeting conflicts
4. Scheduling buffers
5. Optional participant availability
6. Preferred time periods
7. Meeting priority

Valid slots are then given a score and ranked from best to worst.

---

# 📊 Scheduling Scoring

The scheduler starts each valid slot with a base score.

Additional points can be added for:

### Meeting Priority

```text
High     → +30
Medium   → +20
Low      → +10
```

### Preferred Time

```text
Morning     → +20
Afternoon   → +20
Evening     → +20
```

### Optional Participants

Each available optional participant contributes:

```text
+5
```

The resulting slots are sorted by score and assigned a rank.

---

# 🔍 Meeting Slot Search

The main scheduling endpoint is:

```text
POST /api/meetings/find-slots
```

It accepts information such as:

* Participants
* Date
* Duration
* Priority
* Buffer
* Scheduling constraints

The backend sends these parameters to the scheduling engine and returns ranked available slots.

---

# ✅ Selecting a Meeting Slot

After suitable slots have been generated, a user can select one.

### API

```text
PUT /api/meetings/<meeting_id>/select-slot
```

The selected slot is stored in the corresponding meeting.

---

# ✉️ Accepting or Declining Meetings

Participants can respond to meeting invitations.

Supported responses include the response value supplied by the client, along with an optional reason.

### API

```text
PUT /api/meetings/<meeting_id>/response
```

The response is associated with the corresponding participant.

---

# 🚨 Emergency Unavailability

MeetWise supports emergency situations where a participant suddenly becomes unavailable.

### API

```text
POST /api/emergency
```

The endpoint:

1. Records the emergency unavailability period.
2. Adds it to the user's availability information.
3. Finds meetings involving the affected user.
4. Returns the IDs of affected meetings.

---

# 👥 Communities

Users can create communities and add members.

A community contains:

* Community name
* Description
* Members
* Recurring meeting information

### API

```text
GET  /api/communities
POST /api/communities
POST /api/communities/<community_id>/members
```

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │   HTML / CSS / JS   │
                    └──────────┬──────────┘
                               │
                               │ HTTP Requests
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    │       app.py        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
          User APIs        Meeting APIs      Community APIs
              │                │
              │                ▼
              │       ┌─────────────────┐
              │       │ Scheduling      │
              │       │ Engine          │
              │       │ scheduler.py    │
              │       └────────┬────────┘
              │                │
              │                ▼
              │        Ranked Time Slots
              │
              ▼
        In-Memory Data
```

---

# 🛠️ Technology Stack

| Technology        | Purpose                             |
| ----------------- | ----------------------------------- |
| HTML5             | Frontend structure                  |
| CSS3              | Frontend styling                    |
| JavaScript        | Frontend functionality              |
| Python            | Backend programming                 |
| Flask             | Web framework and API               |
| Python `datetime` | Time-related operations             |
| Custom Scheduler  | Meeting-slot generation and ranking |

---

# 📁 Project Structure

```text
C9/
│
├── backend/
│   │
│   ├── app.py
│   │
│   ├── scheduler.py
│   │
│   ├── static/
│   │
│   ├── templates/
│   │
│   └── __pycache__/
│
├── index.html
├── style.css
├── script.js
│
├── README.md
│
└── LICENSE
```

> `__pycache__` is generated automatically by Python and should ideally be excluded from version control.

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python 3 installed
* Git installed
* A modern web browser
* VS Code (recommended)

You can check Python with:

```bash
python --version
```

You should get something similar to:

```text
Python 3.x.x
```

---

# 📥 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/iTrax-Adaptathon/C9.git
```

Then move into the project:

```bash
cd C9
```

---

# 📂 2. Enter the Backend Folder

```bash
cd backend
```

Your terminal should now be inside:

```text
C9/backend
```

---

# 🐍 3. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

This creates:

```text
backend/
└── venv/
```

The virtual environment keeps the project's Python packages separate from your system Python installation.

---

# ▶️ 4. Activate the Virtual Environment

## Windows — Command Prompt

```cmd
venv\Scripts\activate
```

## Windows — PowerShell

```powershell
venv\Scripts\Activate.ps1
```

After activation, your terminal should look similar to:

```text
(venv) C:\...\C9\backend>
```

---

# 📦 5. Install Flask

The backend currently requires Flask.

Install it using:

```bash
pip install flask
```

You can verify the installation:

```bash
pip show flask
```

---

# ▶️ 6. Run the Backend

From inside the `backend` folder:

```bash
python app.py
```

The Flask development server should start.

You should see something similar to:

```text
* Running on http://127.0.0.1:5000
```

---

# 🌐 7. Open MeetWise

Open your browser and visit:

```text
http://127.0.0.1:5000
```

The Flask application serves the page through its root route.

---

# 🔄 Complete Setup From Scratch

If you're starting from zero, these are the commands you need:

```bash
git clone https://github.com/iTrax-Adaptathon/C9.git

cd C9

cd backend

python -m venv venv

venv\Scripts\activate

pip install flask

python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

# 🔌 API Documentation

## 👤 Users

### Get all users

```http
GET /api/users
```

### Create a user

```http
POST /api/users
```

Example request body:

```json
{
  "name": "Hiba",
  "email": "hiba@example.com",
  "phone": "1234567890",
  "preferred_platform": "Google Meet",
  "notification_preferences": {},
  "theme": "light"
}
```

### Update a user

```http
PUT /api/users/<user_id>
```

---

# ⏰ Availability

### Add availability

```http
POST /api/availability
```

Example:

```json
{
  "user_id": 1,
  "date": "2026-09-20",
  "start_time": "09:00",
  "end_time": "17:00",
  "status": "available"
}
```

### Get user availability

```http
GET /api/availability/<user_id>
```

---

# 📅 Meetings

### Get meetings

```http
GET /api/meetings
```

### Create meeting

```http
POST /api/meetings
```

Example:

```json
{
  "title": "Project Meeting",
  "agenda": [
    "Project discussion",
    "Task allocation"
  ],
  "organizer_id": 1,
  "participants": [
    {
      "user_id": 2,
      "type": "required"
    },
    {
      "user_id": 3,
      "type": "optional"
    }
  ],
  "date": "2026-09-20",
  "duration": 60,
  "priority": "high",
  "buffer": 15,
  "constraints": {
    "working_hours_only": true,
    "working_start": "09:00",
    "working_end": "17:00",
    "preferred_period": "morning"
  }
}
```

---

# 🧠 Find Available Meeting Slots

```http
POST /api/meetings/find-slots
```

Example:

```json
{
  "participants": [
    {
      "user_id": 1,
      "type": "required"
    },
    {
      "user_id": 2,
      "type": "optional"
    }
  ],
  "date": "2026-09-20",
  "duration": 60,
  "priority": "high",
  "buffer": 15,
  "constraints": {
    "working_hours_only": true,
    "working_start": "09:00",
    "working_end": "17:00",
    "preferred_period": "morning",
    "search_start": "08:00",
    "search_end": "20:00"
  }
}
```

The response contains available slots with information such as:

```text
date
start_time
end_time
duration
score
rank
priority
buffer
optional_participants_available
```

---

# 📌 Select a Meeting Slot

```http
PUT /api/meetings/<meeting_id>/select-slot
```

Example:

```json
{
  "selected_slot": {
    "date": "2026-09-20",
    "start_time": "10:00",
    "end_time": "11:00"
  }
}
```

---

# ✉️ Meeting Response

```http
PUT /api/meetings/<meeting_id>/response
```

Example:

```json
{
  "user_id": 2,
  "response": "accepted",
  "reason": ""
}
```

---

# 🚨 Emergency Unavailability

```http
POST /api/emergency
```

Example:

```json
{
  "user_id": 2,
  "date": "2026-09-20",
  "unavailable_from": "13:00",
  "unavailable_until": "15:00",
  "reason": "Emergency"
}
```

---

# 👥 Communities

### Get communities

```http
GET /api/communities
```

### Create community

```http
POST /api/communities
```

Example:

```json
{
  "name": "Development Team",
  "description": "Software development community",
  "members": [],
  "recurring_meetings": []
}
```

### Add community member

```http
POST /api/communities/<community_id>/members
```

Example:

```json
{
  "user_id": 2
}
```

---

# ⚙️ Scheduling Algorithm

The scheduling engine is implemented in:

```text
backend/scheduler.py
```

## Step 1 — Convert Time

Times such as:

```text
09:30
```

are converted into minutes:

```text
570
```

This makes time comparison easier.

---

## Step 2 — Generate Candidate Slots

The scheduler searches between the configured search start and search end times.

Candidate slots are generated every:

```text
15 minutes
```

For example:

```text
09:00
09:15
09:30
09:45
10:00
...
```

---

## Step 3 — Check Working Hours

If working-hour restrictions are enabled, the proposed meeting must fit completely within the configured working hours.

Example:

```text
09:00 → 17:00
```

---

## Step 4 — Check Participant Availability

Every participant is checked against their availability.

Required participants must be available.

Optional participants are counted when available.

---

## Step 5 — Check Existing Meeting Conflicts

The scheduler checks existing meetings involving the participant.

Meeting buffers are applied before comparing time periods.

---

## Step 6 — Calculate Score

The slot receives points based on:

```text
Base score
+ Priority score
+ Preferred-period score
+ Optional participant score
+ Additional constraint score
```

---

## Step 7 — Rank Results

All valid slots are sorted by score.

The highest-scoring slot receives:

```text
rank = 1
```

The next receives:

```text
rank = 2
```

and so on.

---

# 💾 Data Storage

### Current Implementation

The current backend uses Python lists as temporary in-memory storage.

The following collections are created when the Flask application starts:

```python
users = []

meetings = []

availability = []

communities = []
```

Therefore, data is **not permanently stored**.

### Important

Restarting the Flask server resets the stored data.

---

# 🗄️ Future Database Integration

The backend contains a planned transition toward SQLite/database storage.

A future version can replace the current in-memory lists with:

```text
SQLite
   ↓
Users
Meetings
Availability
Communities
Participants
Responses
```

This would provide persistent storage between application restarts.

---

# 🔐 Security & Production Considerations

The current version is a hackathon prototype.

For production deployment, the following can be added:

* User authentication
* Password hashing
* Authorization
* Input validation
* Database persistence
* Environment variables
* HTTPS
* CSRF protection
* API authentication
* Proper error handling
* Production WSGI server

---

# 🧪 Testing the Backend

After starting Flask:

```bash
python app.py
```

you can test the API using tools such as:

* Browser
* Postman
* Thunder Client
* VS Code REST Client
* Frontend JavaScript `fetch()`

For example:

```text
GET http://127.0.0.1:5000/api/users
```

should return the current users.

---

# 🛑 Troubleshooting

## `python` is not recognized

Try:

```bash
py --version
```

If that works, use:

```bash
py -m venv venv
```

and:

```bash
py app.py
```

---

## `No module named flask`

Install Flask:

```bash
pip install flask
```

If you created a virtual environment, make sure it is activated first.

---

## PowerShell does not allow activation

If PowerShell blocks:

```powershell
venv\Scripts\Activate.ps1
```

you can use Command Prompt instead:

```cmd
venv\Scripts\activate
```

Then run:

```bash
python app.py
```

---

## Port 5000 is already in use

Stop the other Flask/Python process or change the port in `app.py`.

For example:

```python
app.run(debug=True, port=5001)
```

Then open:

```text
http://127.0.0.1:5001
```

---

# 🧹 Recommended `.gitignore`

Create a `.gitignore` file in the project root:

```gitignore
__pycache__/
*.pyc
venv/
.env
```

This prevents Python cache files and the virtual environment from being committed to GitHub.

---

# 🔮 Future Scope

MeetWise can be extended with:

* 🗄️ SQLite/PostgreSQL database
* 🔐 Authentication and authorization
* 📧 Email invitations
* 🔔 Notifications and reminders
* 📅 Calendar integration
* 🔄 Real-time scheduling updates
* 🔁 Advanced recurring meetings
* ☁️ Cloud deployment
* 📱 Improved mobile responsiveness
* 🤝 Real-time collaboration
* 🎥 Integration with meeting platforms
* 📊 Meeting analytics
* 🔄 Automatic rescheduling after emergency conflicts

---

# 🏆 Hackathon Value

MeetWise focuses on reducing the complexity of coordinating meetings by treating scheduling as a **constraint-based optimization problem**.

Instead of simply finding a free time, the scheduling engine considers:

```text
Participant Availability
        +
Existing Meetings
        +
Working Hours
        +
Time Preferences
        +
Meeting Priority
        +
Optional Participants
        +
Scheduling Buffers
        ↓
Ranked Meeting Slots
```

This allows users to make scheduling decisions based on multiple real-world constraints.

---

# 👨‍💻 Team

## Team C9 — iTrax Adaptathon

Built as part of the **Adaptathon Hackathon**.

---

# 📄 License

This project is licensed under the Apache License 2.0.


This version uses browser localStorage, so it is ideal for a mini-project/demo/prototype.
For a full multi-user project, you can later connect it to Java/Spring Boot, Node.js, PHP, Firebase, MySQL, etc.
