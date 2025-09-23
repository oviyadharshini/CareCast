"""
Synthetic Data Generator for Hospital Resource Optimization
Generates realistic time-series data for hospital operations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class HospitalDataGenerator:
    def __init__(self):
        self.base_date = datetime.now() - timedelta(days=30)
        
    def generate_admissions_discharges(self, days=30, freq='1H'):
        """Generate synthetic admission and discharge data"""
        date_range = pd.date_range(start=self.base_date, periods=days*24, freq=freq)
        
        # Base patterns with realistic variations
        np.random.seed(42)
        base_admissions = []
        base_discharges = []
        
        for dt in date_range:
            hour = dt.hour
            day_of_week = dt.weekday()
            
            # Higher admissions during day hours and weekends
            admission_multiplier = 1.0
            if 8 <= hour <= 20:  # Day time
                admission_multiplier = 1.5
            if day_of_week >= 5:  # Weekend
                admission_multiplier *= 1.3
                
            # Base admission rate: 3-15 patients per hour
            admissions = max(0, int(np.random.poisson(7 * admission_multiplier)))
            
            # Discharge rate typically lower and more during day hours
            discharge_multiplier = 0.8
            if 9 <= hour <= 17:  # Business hours
                discharge_multiplier = 1.2
                
            discharges = max(0, int(np.random.poisson(5 * discharge_multiplier)))
            
            base_admissions.append(admissions)
            base_discharges.append(discharges)
        
        return pd.DataFrame({
            'timestamp': date_range,
            'admissions': base_admissions,
            'discharges': base_discharges
        })
    
    def generate_bed_occupancy(self, admissions_data):
        """Generate bed occupancy based on admissions/discharges"""
        initial_occupancy = 150  # Starting bed occupancy
        total_beds = 250
        
        occupancy = [initial_occupancy]
        
        for i in range(1, len(admissions_data)):
            prev_occupancy = occupancy[-1]
            admissions = admissions_data.iloc[i]['admissions']
            discharges = admissions_data.iloc[i]['discharges']
            
            new_occupancy = prev_occupancy + admissions - discharges
            # Keep within realistic bounds
            new_occupancy = max(50, min(total_beds - 10, new_occupancy))
            occupancy.append(new_occupancy)
        
        occupancy_rate = [(occ / total_beds) * 100 for occ in occupancy]
        
        return pd.DataFrame({
            'timestamp': admissions_data['timestamp'],
            'bed_occupancy': occupancy,
            'occupancy_rate': occupancy_rate,
            'total_beds': total_beds
        })
    
    def generate_oxygen_levels(self, days=30, freq='1H'):
        """Generate oxygen tank level data"""
        date_range = pd.date_range(start=self.base_date, periods=days*24, freq=freq)
        
        # Start with high levels, gradual consumption with refills
        initial_level = 2000  # liters
        max_capacity = 2500
        
        levels = [initial_level]
        consumption_rates = []
        refill_events = []
        
        for i in range(1, len(date_range)):
            prev_level = levels[-1]
            
            # Consumption varies by time of day and occupancy
            hour = date_range[i].hour
            base_consumption = 15  # liters per hour
            
            if 6 <= hour <= 22:  # Day time - higher consumption
                consumption = np.random.normal(base_consumption * 1.4, 3)
            else:  # Night time
                consumption = np.random.normal(base_consumption * 0.8, 2)
            
            consumption = max(5, consumption)  # Minimum consumption
            consumption_rates.append(consumption)
            
            # Check if refill needed
            new_level = prev_level - consumption
            refilled = False
            
            if new_level < 500:  # Critical level - emergency refill
                new_level = max_capacity
                refilled = True
            elif new_level < 1000 and np.random.random() < 0.3:  # Scheduled refill
                new_level = max_capacity
                refilled = True
            
            levels.append(new_level)
            refill_events.append(refilled)
        
        return pd.DataFrame({
            'timestamp': date_range,
            'oxygen_level': levels,
            'consumption_rate': [0] + consumption_rates,
            'refill_event': [False] + refill_events,
            'max_capacity': max_capacity
        })
    
    def generate_staff_schedules(self, days=30):
        """Generate staff schedule data"""
        date_range = pd.date_range(start=self.base_date, periods=days, freq='D')
        
        staff_data = []
        staff_types = ['Nurses', 'Doctors', 'Support_Staff']
        shift_types = ['Morning', 'Evening', 'Night']
        
        for date in date_range:
            for staff_type in staff_types:
                for shift in shift_types:
                    # Base staff numbers with variations
                    if staff_type == 'Nurses':
                        base_count = {'Morning': 25, 'Evening': 20, 'Night': 15}[shift]
                    elif staff_type == 'Doctors':
                        base_count = {'Morning': 15, 'Evening': 12, 'Night': 8}[shift]
                    else:  # Support staff
                        base_count = {'Morning': 10, 'Evening': 8, 'Night': 5}[shift]
                    
                    # Add variation and weekend adjustments
                    variation = np.random.randint(-2, 3)
                    if date.weekday() >= 5:  # Weekend
                        variation -= 2
                    
                    scheduled = max(1, base_count + variation)
                    present = scheduled - max(0, np.random.binomial(scheduled, 0.05))  # 5% absence rate
                    
                    staff_data.append({
                        'date': date,
                        'staff_type': staff_type,
                        'shift': shift,
                        'scheduled_count': scheduled,
                        'present_count': present,
                        'utilization_rate': min(100, (present / scheduled) * 100)
                    })
        
        return pd.DataFrame(staff_data)
    
    def generate_complete_dataset(self, days=30):
        """Generate complete hospital dataset"""
        print(f"Generating {days} days of hospital data...")
        
        # Generate all components
        admissions_data = self.generate_admissions_discharges(days)
        bed_data = self.generate_bed_occupancy(admissions_data)
        oxygen_data = self.generate_oxygen_levels(days)
        staff_data = self.generate_staff_schedules(days)
        
        # Merge time-series data
        hospital_data = admissions_data.merge(bed_data, on='timestamp')
        hospital_data = hospital_data.merge(oxygen_data, on='timestamp')
        
        # Add derived features for ML
        hospital_data['hour'] = hospital_data['timestamp'].dt.hour
        hospital_data['day_of_week'] = hospital_data['timestamp'].dt.dayofweek
        hospital_data['is_weekend'] = hospital_data['day_of_week'] >= 5
        hospital_data['month'] = hospital_data['timestamp'].dt.month
        
        # Add resource stress indicators
        hospital_data['bed_stress'] = hospital_data['occupancy_rate'] > 85
        hospital_data['oxygen_stress'] = hospital_data['oxygen_level'] < 800
        
        return hospital_data, staff_data
    
    def save_data(self, hospital_data, staff_data, data_dir='data'):
        """Save generated data to files"""
        os.makedirs(data_dir, exist_ok=True)
        
        # Save main dataset
        hospital_data.to_csv(f'{data_dir}/hospital_data.csv', index=False)
        staff_data.to_csv(f'{data_dir}/staff_data.csv', index=False)
        
        # Save metadata
        metadata = {
            'total_records': len(hospital_data),
            'date_range': {
                'start': hospital_data['timestamp'].min().isoformat(),
                'end': hospital_data['timestamp'].max().isoformat()
            },
            'features': list(hospital_data.columns),
            'generation_time': datetime.now().isoformat()
        }
        
        with open(f'{data_dir}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Data saved to {data_dir}/")
        print(f"Hospital records: {len(hospital_data)}")
        print(f"Staff records: {len(staff_data)}")

if __name__ == "__main__":
    generator = HospitalDataGenerator()
    hospital_data, staff_data = generator.generate_complete_dataset(days=30)
    generator.save_data(hospital_data, staff_data)