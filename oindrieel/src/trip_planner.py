from collections import defaultdict


class TripPlanner:
    def __init__(self, all_locations):
        """
        :param all_locations: List of dicts (the raw data from locations.json)
        """
        self.locations = all_locations

    def plan_trip(self, days=1, interests=None):
        if interests is None:
            interests = []

        print(f"🗺️ Planning a {days}-day trip for interests: {interests}...")

        # 1. Score locations based on user interests
        # If user likes "Nature", Ayodhya gets +1 point.
        scored_places = []
        for place in self.locations:
            score = 0
            # Base score (every place has some value)
            score += 1

            # Bonus score for interest match
            place_tags = [t.lower() for t in place.get('tags', [])]
            for interest in interests:
                if interest.lower() in place_tags:
                    score += 5  # High priority for matches

            scored_places.append({
                "data": place,
                "score": score
            })

        # 2. Sort by score (High score first)
        scored_places.sort(key=lambda x: x['score'], reverse=True)

        # 3. Group by Zone (Clustering)
        # Result: {'South-West': [Ayodhya, Bamni, Charida], 'North-East': [Panchakot]}
        zones = defaultdict(list)
        for item in scored_places:
            zone_name = item['data']['location_data']['zone']
            zones[zone_name].append(item['data'])

        # 4. Allocate Zones to Days
        itinerary = {}
        sorted_zones = sorted(zones.keys(), key=lambda z: len(zones[z]), reverse=True)

        current_day = 1
        for zone in sorted_zones:
            if current_day > days:
                break

            # Assign this zone to the current day
            # We take the top 3 items in this zone to avoid over-scheduling
            days_places = zones[zone][:3]

            itinerary[f"Day {current_day}"] = {
                "Zone": zone,
                "Morning": days_places[0]['name'] if len(days_places) > 0 else "Relax",
                "Afternoon": days_places[1]['name'] if len(days_places) > 1 else "Local Exploration",
                "Evening": days_places[2]['name'] if len(days_places) > 2 else "Sunset View"
            }
            current_day += 1

        return itinerary


if __name__ == "__main__":
    # --- Manual Test Block ---
    # We create dummy data here so we can test the logic without loading the full JSON file
    mock_locations = [
        {
            "name": "Ayodhya Hills",
            "tags": ["Nature", "Adventure"],
            "location_data": {"zone": "South-West"}
        },
        {
            "name": "Bamni Falls",
            "tags": ["Nature", "Waterfall"],
            "location_data": {"zone": "South-West"}
        },
        {
            "name": "Charida Village",
            "tags": ["Culture", "Art"],
            "location_data": {"zone": "South-West"}
        },
        {
            "name": "Garh Panchakot",
            "tags": ["History", "Ruins"],
            "location_data": {"zone": "North-East"}
        },
        {
            "name": "Joychandi Pahar",
            "tags": ["Adventure", "Hiking"],
            "location_data": {"zone": "North-East"}
        }
    ]

    print("--- 🧪 Testing Trip Planner Module Independently ---")
    planner = TripPlanner(mock_locations)

    # Test: Plan a 2-day trip for someone who likes Nature
    plan = planner.plan_trip(days=2, interests=["Nature", "History"])

    import json

    print(json.dumps(plan, indent=2))