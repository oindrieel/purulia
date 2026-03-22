from collections import defaultdict


class TripPlanner:
    def __init__(self, all_locations):
        self.locations = all_locations

    def plan_trip(self, days=1, interests=None, specific_places=None):
        if interests is None: interests = []
        if specific_places is None: specific_places = []

        print(f"🗺️ Planning a {days}-day trip...")

        # 1. Score locations
        scored_places = []
        for place in self.locations:
            score = 1  # Base score

            # Bonus score for interest match
            place_tags = [t.lower() for t in place.get('tags', [])]
            for interest in interests:
                if interest.lower() in place_tags:
                    score += 5

                    # CONTEXT MEMORY OVERRIDE: If this place was in the context, boost it massively!
            if specific_places and place['name'] in specific_places:
                score += 100

            scored_places.append({
                "data": place,
                "score": score
            })

        # 2. Sort by score
        scored_places.sort(key=lambda x: x['score'], reverse=True)

        # 3. Group by Zone
        zones = defaultdict(list)
        for item in scored_places:
            zone_name = item['data']['location_data']['zone']
            zones[zone_name].append(item['data'])

        # 4. Allocate Zones to Days
        itinerary = {}
        sorted_zones = sorted(zones.keys(), key=lambda z: len(zones[z]), reverse=True)

        current_day = 1
        for zone in sorted_zones:
            if current_day > days: break

            days_places = zones[zone][:3]

            itinerary[f"Day {current_day}"] = {
                "Zone": zone,
                "Morning": days_places[0]['name'] if len(days_places) > 0 else "Relax",
                "Afternoon": days_places[1]['name'] if len(days_places) > 1 else "Local Exploration",
                "Evening": days_places[2]['name'] if len(days_places) > 2 else "Sunset View"
            }
            current_day += 1

        return itinerary