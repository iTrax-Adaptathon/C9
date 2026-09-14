from flask import Flask, request, jsonify, render_template
from datetime import datetime

# Import scheduling functions
from scheduler import find_available_slots


# --------------------------------------------------
# CREATE FLASK APPLICATION
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# TEMPORARY DATA
# --------------------------------------------------
# We will move this into SQLite database later.
# For now, this helps us test the application.

users = []

meetings = []

availability = []

communities = []


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# USER / PROFILE
# ==================================================

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)


@app.route("/api/users", methods=["POST"])
def create_user():

    data = request.json

    user = {
        "id": len(users) + 1,
        "name": data.get("name"),
        "profile_picture": data.get("profile_picture"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "preferred_platform": data.get("preferred_platform"),
        "notification_preferences": data.get(
            "notification_preferences"
        ),
        "theme": data.get("theme", "light")
    }

    users.append(user)

    return jsonify({
        "message": "User created successfully",
        "user": user
    }), 201


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    data = request.json

    for user in users:

        if user["id"] == user_id:

            user.update({
                "name": data.get("name", user["name"]),
                "profile_picture": data.get(
                    "profile_picture",
                    user["profile_picture"]
                ),
                "email": data.get("email", user["email"]),
                "phone": data.get("phone", user["phone"]),
                "preferred_platform": data.get(
                    "preferred_platform",
                    user["preferred_platform"]
                ),
                "notification_preferences": data.get(
                    "notification_preferences",
                    user["notification_preferences"]
                ),
                "theme": data.get(
                    "theme",
                    user["theme"]
                )
            })

            return jsonify({
                "message": "Profile updated",
                "user": user
            })

    return jsonify({
        "error": "User not found"
    }), 404


# ==================================================
# AVAILABILITY
# ==================================================

@app.route("/api/availability", methods=["POST"])
def add_availability():

    data = request.json

    availability_data = {
        "id": len(availability) + 1,
        "user_id": data.get("user_id"),
        "date": data.get("date"),
        "start_time": data.get("start_time"),
        "end_time": data.get("end_time"),
        "status": data.get("status", "available")
    }

    availability.append(availability_data)

    return jsonify({
        "message": "Availability added",
        "availability": availability_data
    }), 201


@app.route("/api/availability/<int:user_id>", methods=["GET"])
def get_availability(user_id):

    user_availability = [
        item for item in availability
        if item["user_id"] == user_id
    ]

    return jsonify(user_availability)


# ==================================================
# MEETINGS
# ==================================================

@app.route("/api/meetings", methods=["GET"])
def get_meetings():

    return jsonify(meetings)


@app.route("/api/meetings", methods=["POST"])
def create_meeting():

    data = request.json

    meeting = {
        "id": len(meetings) + 1,

        "title": data.get("title"),

        "agenda": data.get("agenda", []),

        "organizer_id": data.get("organizer_id"),

        "participants": data.get("participants", []),

        "date": data.get("date"),

        "duration": data.get("duration"),

        "priority": data.get("priority", "medium"),

        "buffer": data.get("buffer", 0),

        "constraints": data.get(
            "constraints",
            {}
        ),

        "status": "proposed",

        "selected_slot": None
    }

    meetings.append(meeting)

    return jsonify({
        "message": "Meeting created",
        "meeting": meeting
    }), 201


# ==================================================
# FIND AVAILABLE MEETING SLOTS
# ==================================================

@app.route("/api/meetings/find-slots", methods=["POST"])
def find_slots():

    data = request.json

    participants = data.get(
        "participants",
        []
    )

    date = data.get("date")

    duration = data.get(
        "duration",
        60
    )

    priority = data.get(
        "priority",
        "medium"
    )

    buffer = data.get(
        "buffer",
        0
    )

    constraints = data.get(
        "constraints",
        {}
    )

    # Existing meetings that may cause conflicts
    existing_meetings = meetings

    # Call the scheduling engine
    slots = find_available_slots(
        participants=participants,
        date=date,
        duration=duration,
        priority=priority,
        buffer=buffer,
        constraints=constraints,
        availability=availability,
        existing_meetings=existing_meetings
    )

    return jsonify({
        "message": "Available slots generated",
        "slots": slots
    })


# ==================================================
# SELECT A MEETING SLOT
# ==================================================

@app.route("/api/meetings/<int:meeting_id>/select-slot",
           methods=["PUT"])
def select_slot(meeting_id):

    data = request.json

    selected_slot = data.get(
        "selected_slot"
    )

    for meeting in meetings:

        if meeting["id"] == meeting_id:

            meeting["selected_slot"] = selected_slot

            meeting["status"] = "proposed"

            return jsonify({
                "message": "Meeting slot selected",
                "meeting": meeting
            })

    return jsonify({
        "error": "Meeting not found"
    }), 404


# ==================================================
# ACCEPT / DECLINE MEETING
# ==================================================

@app.route(
    "/api/meetings/<int:meeting_id>/response",
    methods=["PUT"]
)
def meeting_response(meeting_id):

    data = request.json

    user_id = data.get("user_id")

    response = data.get(
        "response"
    )

    reason = data.get(
        "reason",
        ""
    )

    for meeting in meetings:

        if meeting["id"] == meeting_id:

            for participant in meeting["participants"]:

                if participant["user_id"] == user_id:

                    participant["response"] = response

                    participant["reason"] = reason

                    return jsonify({
                        "message": "Response recorded",
                        "meeting": meeting
                    })

            return jsonify({
                "error": "Participant not found"
            }), 404

    return jsonify({
        "error": "Meeting not found"
    }), 404


# ==================================================
# EMERGENCY UNAVAILABILITY
# ==================================================

@app.route(
    "/api/emergency",
    methods=["POST"]
)
def emergency():

    data = request.json

    user_id = data.get(
        "user_id"
    )

    unavailable_from = data.get(
        "unavailable_from"
    )

    unavailable_until = data.get(
        "unavailable_until"
    )

    reason = data.get(
        "reason",
        "Emergency"
    )

    # Add emergency period to availability
    emergency_data = {
        "id": len(availability) + 1,
        "user_id": user_id,
        "date": data.get("date"),
        "start_time": unavailable_from,
        "end_time": unavailable_until,
        "status": "emergency",
        "reason": reason
    }

    availability.append(
        emergency_data
    )

    # Find meetings involving this person
    affected_meetings = []

    for meeting in meetings:

        for participant in meeting["participants"]:

            if participant["user_id"] == user_id:

                affected_meetings.append(
                    meeting["id"]
                )

    return jsonify({
        "message": "Emergency availability updated",
        "affected_meetings": affected_meetings
    })


# ==================================================
# COMMUNITIES
# ==================================================

@app.route(
    "/api/communities",
    methods=["GET"]
)
def get_communities():

    return jsonify(communities)


@app.route(
    "/api/communities",
    methods=["POST"]
)
def create_community():

    data = request.json

    community = {
        "id": len(communities) + 1,

        "name": data.get("name"),

        "description": data.get(
            "description",
            ""
        ),

        "members": data.get(
            "members",
            []
        ),

        "recurring_meetings": data.get(
            "recurring_meetings",
            []
        )
    }

    communities.append(
        community
    )

    return jsonify({
        "message": "Community created",
        "community": community
    }), 201


@app.route(
    "/api/communities/<int:community_id>/members",
    methods=["POST"]
)
def add_community_member(
    community_id
):

    data = request.json

    user_id = data.get(
        "user_id"
    )

    for community in communities:

        if community["id"] == community_id:

            if user_id not in community["members"]:

                community["members"].append(
                    user_id
                )

            return jsonify({
                "message": "Member added",
                "community": community
            })

    return jsonify({
        "error": "Community not found"
    }), 404


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )