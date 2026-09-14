from datetime import datetime, timedelta


# =========================================================
# TIME CONVERSION
# =========================================================

def time_to_minutes(time_string):
    """
    Converts time such as '09:30' into minutes.

    09:30 → 570
    """

    hours, minutes = map(int, time_string.split(":"))

    return hours * 60 + minutes


def minutes_to_time(minutes):
    """
    Converts minutes back into HH:MM format.

    570 → '09:30'
    """

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# =========================================================
# CHECK WHETHER TWO TIME PERIODS OVERLAP
# =========================================================

def time_overlaps(start1, end1, start2, end2):
    """
    Returns True if two time periods overlap.
    """

    return start1 < end2 and end1 > start2


# =========================================================
# CHECK PARTICIPANT AVAILABILITY
# =========================================================

def participant_is_available(
    user_id,
    date,
    start_time,
    end_time,
    availability
):
    """
    Checks whether a participant is available
    during the requested time.
    """

    requested_start = time_to_minutes(start_time)
    requested_end = time_to_minutes(end_time)

    user_availability = [
        item for item in availability
        if item["user_id"] == user_id
        and item["date"] == date
    ]

    # No availability information
    if not user_availability:
        return False

    for item in user_availability:

        available_start = time_to_minutes(
            item["start_time"]
        )

        available_end = time_to_minutes(
            item["end_time"]
        )

        # Emergency/unavailable periods
        if item["status"] in ["unavailable", "emergency"]:
            if time_overlaps(
                requested_start,
                requested_end,
                available_start,
                available_end
            ):
                return False

        # Normal available period
        if item["status"] == "available":

            if (
                requested_start >= available_start
                and requested_end <= available_end
            ):
                return True

    return False


# =========================================================
# CHECK EXISTING MEETINGS
# =========================================================

def meeting_causes_conflict(
    user_id,
    date,
    start_time,
    end_time,
    buffer,
    existing_meetings
):
    """
    Checks whether the proposed meeting conflicts
    with an existing meeting.
    """

    proposed_start = time_to_minutes(start_time)
    proposed_end = time_to_minutes(end_time)

    # Apply buffer around proposed meeting
    proposed_start -= buffer
    proposed_end += buffer

    for meeting in existing_meetings:

        if meeting.get("date") != date:
            continue

        # Get participants
        participants = meeting.get(
            "participants",
            []
        )

        participant_ids = []

        for participant in participants:

            if isinstance(participant, dict):
                participant_ids.append(
                    participant.get("user_id")
                )

            else:
                participant_ids.append(
                    participant
                )

        # Organizer is also considered
        if meeting.get("organizer_id") is not None:
            participant_ids.append(
                meeting.get("organizer_id")
            )

        if user_id not in participant_ids:
            continue

        # No selected slot yet
        if not meeting.get("selected_slot"):
            continue

        selected_slot = meeting["selected_slot"]

        existing_start = time_to_minutes(
            selected_slot["start_time"]
        )

        existing_end = time_to_minutes(
            selected_slot["end_time"]
        )

        existing_buffer = meeting.get(
            "buffer",
            0
        )

        existing_start -= existing_buffer
        existing_end += existing_buffer

        if time_overlaps(
            proposed_start,
            proposed_end,
            existing_start,
            existing_end
        ):
            return True

    return False


# =========================================================
# CHECK WORKING HOURS
# =========================================================

def is_within_working_hours(
    start_time,
    end_time,
    constraints
):
    """
    Checks whether a meeting falls inside
    the user's preferred working hours.
    """

    if not constraints.get(
        "working_hours_only",
        False
    ):
        return True

    working_start = constraints.get(
        "working_start",
        "09:00"
    )

    working_end = constraints.get(
        "working_end",
        "17:00"
    )

    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)

    allowed_start = time_to_minutes(
        working_start
    )

    allowed_end = time_to_minutes(
        working_end
    )

    return (
        start >= allowed_start
        and end <= allowed_end
    )


# =========================================================
# PREFERENCE SCORE
# =========================================================

def calculate_preference_score(
    start_time,
    constraints
):
    """
    Gives extra points to preferred time periods.
    """

    preference = constraints.get(
        "preferred_period"
    )

    if not preference:
        return 0

    hour = int(
        start_time.split(":")[0]
    )

    # Morning preference
    if preference == "morning":

        if 8 <= hour < 12:
            return 20

    # Afternoon preference
    if preference == "afternoon":

        if 12 <= hour < 17:
            return 20

    # Evening preference
    if preference == "evening":

        if 17 <= hour < 21:
            return 20

    return 0


# =========================================================
# PRIORITY SCORE
# =========================================================

def calculate_priority_score(priority):
    """
    Gives higher score to higher-priority meetings.
    """

    if priority == "high":
        return 30

    if priority == "medium":
        return 20

    if priority == "low":
        return 10

    return 0


# =========================================================
# FIND AVAILABLE SLOTS
# =========================================================

def find_available_slots(
    participants,
    date,
    duration,
    priority,
    buffer,
    constraints,
    availability,
    existing_meetings
):
    """
    Main scheduling function.

    Finds possible meeting slots and ranks them.
    """

    possible_slots = []

    # -----------------------------------------------------
    # Check every 15 minutes
    # -----------------------------------------------------

    day_start = time_to_minutes(
        constraints.get(
            "search_start",
            "08:00"
        )
    )

    day_end = time_to_minutes(
        constraints.get(
            "search_end",
            "20:00"
        )
    )

    current_time = day_start

    while current_time + duration <= day_end:

        start_time = minutes_to_time(
            current_time
        )

        end_time = minutes_to_time(
            current_time + duration
        )

        # -------------------------------------------------
        # Working hours
        # -------------------------------------------------

        if not is_within_working_hours(
            start_time,
            end_time,
            constraints
        ):

            current_time += 15
            continue

        # -------------------------------------------------
        # Check participants
        # -------------------------------------------------

        required_available = True
        optional_available = 0

        for participant in participants:

            # Participant can be a dictionary
            if isinstance(participant, dict):

                user_id = participant.get(
                    "user_id"
                )

                participant_type = participant.get(
                    "type",
                    "required"
                )

            # Or simply a user ID
            else:

                user_id = participant
                participant_type = "required"

            available = participant_is_available(
                user_id,
                date,
                start_time,
                end_time,
                availability
            )

            # Check existing meetings
            if available:

                conflict = meeting_causes_conflict(
                    user_id,
                    date,
                    start_time,
                    end_time,
                    buffer,
                    existing_meetings
                )

                if conflict:
                    available = False

            # Required participant unavailable
            if (
                participant_type == "required"
                and not available
            ):
                required_available = False

            # Optional participant available
            if (
                participant_type == "optional"
                and available
            ):
                optional_available += 1

        # -------------------------------------------------
        # If required participant is unavailable,
        # reject this slot.
        # -------------------------------------------------

        if not required_available:

            current_time += 15
            continue

        # -------------------------------------------------
        # Calculate score
        # -------------------------------------------------

        score = 50

        # Priority
        score += calculate_priority_score(
            priority
        )

        # Preferred period
        score += calculate_preference_score(
            start_time,
            constraints
        )

        # Optional participant score
        score += optional_available * 5

        # Avoid back-to-back meetings
        if constraints.get(
            "avoid_back_to_back",
            False
        ):
            score += 5

        # -------------------------------------------------
        # Add slot
        # -------------------------------------------------

        possible_slots.append({

            "date": date,

            "start_time": start_time,

            "end_time": end_time,

            "duration": duration,

            "score": score,

            "optional_participants_available":
                optional_available,

            "priority": priority,

            "buffer": buffer

        })

        current_time += 15

    # =====================================================
    # SORT BEST SLOTS FIRST
    # =====================================================

    possible_slots.sort(
        key=lambda slot: slot["score"],
        reverse=True
    )

    # =====================================================
    # ADD RANK
    # =====================================================

    for index, slot in enumerate(
        possible_slots,
        start=1
    ):

        slot["rank"] = index

    return possible_slots