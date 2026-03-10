def estimate_eta_minutes(distance_miles: float, avg_speed_mph: float = 25.0) -> int:
    if distance_miles <= 0:
        return 1

    hours = distance_miles / avg_speed_mph
    minutes = round(hours * 60)

    return max(minutes, 1)