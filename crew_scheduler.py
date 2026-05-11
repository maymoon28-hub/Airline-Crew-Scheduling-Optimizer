import pandas as pd
import numpy as np

# Load data
flights = pd.read_csv('flights.csv')
crew = pd.read_csv('crew.csv')
constraints = pd.read_csv('constraints.csv')

print("=" * 70)
print("FLYDUBAI CREW SCHEDULING OPTIMIZER")
print("=" * 70)
print(f"\n📋 Loaded {len(flights)} flights and {len(crew)} crew members")
print(f"📊 Constraints: Max {constraints.iloc[0]['value']}hrs/week, Min {constraints.iloc[1]['value']}hrs rest\n")

# Initialize tracking
crew_hours = {c: 0 for c in crew['crew_id']}
crew_flights = {c: [] for c in crew['crew_id']}
assignments = []
coverage_issues = []

# Separate pilots and cabin crew
pilots = crew[crew['qualification'] == 'Pilot']['crew_id'].tolist()
cabin_crew_list = crew[crew['qualification'] == 'Cabin Crew']['crew_id'].tolist()

# Assignment algorithm
for idx, flight in flights.iterrows():
    flight_assignments = []
    
    # Assign pilots
    available_pilots = [p for p in pilots if crew_hours[p] + flight['duration_hours'] <= 40]
    assigned_pilots = available_pilots[:flight['required_pilots']]
    
    if len(assigned_pilots) < flight['required_pilots']:
        coverage_issues.append({
            'flight_id': flight['flight_id'],
            'issue': f"Insufficient pilots ({len(assigned_pilots)}/{flight['required_pilots']})"
        })
    
    for pilot in assigned_pilots:
        crew_hours[pilot] += flight['duration_hours']
        crew_flights[pilot].append(flight['flight_id'])
        flight_assignments.append({
            'flight_id': flight['flight_id'],
            'day': flight['day'],
            'departure_time': flight['departure_time'],
            'crew_id': pilot,
            'crew_name': crew[crew['crew_id'] == pilot]['name'].values[0],
            'qualification': 'Pilot',
            'duration_hours': flight['duration_hours']
        })
    
    # Assign cabin crew
    available_cabin = [c for c in cabin_crew_list if crew_hours[c] + flight['duration_hours'] <= 40]
    assigned_cabin = available_cabin[:flight['required_cabin_crew']]
    
    if len(assigned_cabin) < flight['required_cabin_crew']:
        coverage_issues.append({
            'flight_id': flight['flight_id'],
            'issue': f"Insufficient cabin crew ({len(assigned_cabin)}/{flight['required_cabin_crew']})"
        })
    
    for cabin in assigned_cabin:
        crew_hours[cabin] += flight['duration_hours']
        crew_flights[cabin].append(flight['flight_id'])
        flight_assignments.append({
            'flight_id': flight['flight_id'],
            'day': flight['day'],
            'departure_time': flight['departure_time'],
            'crew_id': cabin,
            'crew_name': crew[crew['crew_id'] == cabin]['name'].values[0],
            'qualification': 'Cabin Crew',
            'duration_hours': flight['duration_hours']
        })
    
    assignments.extend(flight_assignments)

# Create assignments dataframe
assignments_df = pd.DataFrame(assignments)

# Calculate metrics
total_flights = len(flights)
flights_covered = len(assignments_df['flight_id'].unique())
coverage_rate = (flights_covered / total_flights) * 100

crew_utilization = []
for c in crew['crew_id']:
    util_rate = (crew_hours[c] / 40) * 100
    crew_utilization.append({
        'crew_id': c,
        'crew_name': crew[crew['crew_id'] == c]['name'].values[0],
        'qualification': crew[crew['crew_id'] == c]['qualification'].values[0],
        'hours_worked': crew_hours[c],
        'max_hours': 40,
        'utilization_percent': round(util_rate, 1),
        'flights_assigned': len(crew_flights[c])
    })

utilization_df = pd.DataFrame(crew_utilization)
avg_utilization = utilization_df['utilization_percent'].mean()

# Display results
print("=" * 70)
print("KEY PERFORMANCE INDICATORS")
print("=" * 70)
print(f"✈️  Flight Coverage: {flights_covered}/{total_flights} flights ({coverage_rate:.1f}%)")
print(f"👥 Average Crew Utilization: {avg_utilization:.1f}%")
print(f"⚠️  Coverage Issues: {len(coverage_issues)}")
print(f"📊 Total Assignments Made: {len(assignments_df)}")

print("\n" + "=" * 70)
print("CREW UTILIZATION SUMMARY")
print("=" * 70)
print(utilization_df.to_string(index=False))

if coverage_issues:
    print("\n" + "=" * 70)
    print("⚠️  COVERAGE ISSUES DETECTED")
    print("=" * 70)
    issues_df = pd.DataFrame(coverage_issues)
    print(issues_df.to_string(index=False))

# Save outputs
assignments_df.to_csv('crew_assignments.csv', index=False)
utilization_df.to_csv('crew_utilization.csv', index=False)

print("\n" + "=" * 70)
print("✅ FILES SAVED")
print("=" * 70)
print("📄 crew_assignments.csv - Full flight-to-crew assignment matrix")
print("📄 crew_utilization.csv - Crew workload and utilization metrics")

print("\n" + "=" * 70)
print("SAMPLE ASSIGNMENTS (First 15):")
print("=" * 70)
print(assignments_df.head(15).to_string(index=False))

print("\n✅ Crew scheduling optimization complete!")