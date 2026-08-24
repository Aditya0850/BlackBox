#!/usr/bin/env python3
"""
BlackBox SIH26189 CDR (Call Detail Record) Generator
Generates 5,000+ synthetic CDR records
"""

import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class CDRecordGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # CDR fields
        self.call_types = [
            ('VOICE_OUT', 0.4),
            ('VOICE_IN', 0.35),
            ('SMS_OUT', 0.15),
            ('SMS_IN', 0.1)
        ]
        
        self.call_durations = {
            'VOICE_OUT': (0, 1800),  # 0 to 30 minutes in seconds
            'VOICE_IN': (0, 1800),
            'SMS_OUT': (0, 0),  # SMS has zero duration
            'SMS_IN': (0, 0)
        }
    
    def load_world_model(self):
        """Load the pre-generated world model"""
        with open(self.world_model_path, 'r', encoding='utf-8') as f:
            world_model = json.load(f)
        
        self.canonical_entities = world_model['canonical_entities']
        self.criminal_networks = world_model['criminal_networks']
        self.cases = world_model['cases']
        
        print(f"Loaded world model with:")
        print(f"  {len(self.canonical_entities['people'])} people")
        print(f"  {len(self.canonical_entities['phone_numbers'])} phone numbers")
    
    def generate_cdr_id(self, sequence):
        """Generate a unique CDR ID"""
        return f"CDR/{sequence:08d}"
    
    def generate_timestamp(self, days_back=None):
        """Generate a realistic timestamp"""
        if days_back is None:
            # Random time in our range (2024-01-01 to 2026-06-30)
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2026, 6, 30)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            timestamp = start_date + timedelta(days=random_days)
        else:
            # Specific days back from now
            timestamp = datetime.now() - timedelta(days=days_back)
        
        # Add time of day
        timestamp = timestamp.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return timestamp
    
    def select_caller_receiver(self, is_suspicious=False, network_id=None):
        """Select caller and receiver phone numbers"""
        phone_numbers = list(self.canonical_entities['phone_numbers'].keys())
        
        if not phone_numbers:
            return None, None
        
        if is_suspicious and network_id and network_id in self.criminal_networks:
            # For suspicious calls, select people from the network and get their phones
            network = self.criminal_networks[network_id]
            network_members = network.get('members', [])
            
            if network_members:
                # Get phones of network members
                member_phones = []
                for person_id in network_members:
                    person = self.canonical_entities['people'].get(person_id, {})
                    person_phones = person.get('phone_numbers', [])
                    member_phones.extend(person_phones)
                
                if member_phones:
                    # Select caller and receiver from network member phones
                    if len(member_phones) >= 2:
                        caller, receiver = random.sample(member_phones, 2)
                    else:
                        caller = receiver = random.choice(member_phones)
                    return caller, receiver
        
        # For normal calls or if network selection failed, select random phones
        if len(phone_numbers) >= 2:
            caller, receiver = random.sample(phone_numbers, 2)
        else:
            caller = receiver = random.choice(phone_numbers)
        
        return caller, receiver
    
    def generate_cdr_record(self, sequence, is_suspicious=False, network_id=None):
        """Generate a single CDR record"""
        
        # Generate timestamp
        timestamp = self.generate_timestamp()
        
        # Select call type based on weights
        call_types, weights = zip(*self.call_types)
        call_type = random.choices(call_types, weights=weights)[0]
        
        # Generate duration based on call type
        min_duration, max_duration = self.call_durations[call_type]
        duration = random.randint(min_duration, max_duration) if max_duration > min_duration else 0
        
        # Select caller and receiver
        caller_id, receiver_id = self.select_caller_receiver(is_suspicious, network_id)
        
        if caller_id is None or receiver_id is None:
            return None
        
        # Get phone details
        caller_phone = self.canonical_entities['phone_numbers'].get(caller_id, {})
        receiver_phone = self.canonical_entities['phone_numbers'].get(receiver_id, {})
        
        # Generate cell tower/location info (simplified)
        cell_tower_id = f"TWR{random.randint(1000, 9999)}"
        location_area = random.choice([
            'Urban Center', 'Suburban Area', 'Industrial Zone', 
            'Residential Area', 'Commercial District', 'Highway Corridor',
            'Border Area', 'Coastal Region', 'Hilly Terrain', 'Forest Area'
        ])
        
        # Determine if it's a roaming call (low probability)
        is_roaming = random.random() < 0.02
        
        # Generate CDR record
        cdr_record = {
            'cdr_id': self.generate_cdr_id(sequence),
            'timestamp': timestamp.isoformat(),
            'call_type': call_type,
            'duration_seconds': duration,
            'caller_number': caller_phone.get('formatted_number', 'UNKNOWN'),
            'receiver_number': receiver_phone.get('formatted_number', 'UNKNOWN'),
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'cell_tower_id': cell_tower_id,
            'location_area': location_area,
            'is_roaming': is_roaming,
            'is_international': random.random() < 0.01,  # 1% international calls
            'is_suspicious': is_suspicious,
            'network_id': network_id if is_suspicious else None,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        return cdr_record
    
    def generate_cdr_records(self, count=7000, output_dir='demo_data/full_dataset/cdrs'):
        """Generate multiple CDR records"""
        
        print(f"Generating {count} CDR records...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get network IDs for assigning some records to networks (10% suspicious)
        network_ids = list(self.criminal_networks.keys()) if self.criminal_networks else [None]
        
        records = []
        suspicious_count = 0
        
        for i in range(count):
            # Determine if this record should be suspicious (10% chance)
            is_suspicious = random.random() < 0.1
            network_id = None
            
            if is_suspicious:
                network_id = random.choice(network_ids) if network_ids and network_ids[0] is not None else None
                if network_id is not None:
                    suspicious_count += 1
            
            # Generate record
            record_sequence = i + 1
            record = self.generate_cdr_record(
                sequence=record_sequence,
                is_suspicious=is_suspicious,
                network_id=network_id
            )
            
            if record is not None:
                records.append(record)
            
            # Progress indicator
            if (i + 1) % 500 == 0:
                print(f"  Generated {i + 1} records...")
        
        # Save records as JSON file (structured format)
        output_file = os.path.join(output_dir, 'cdr_records.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(records)} CDR records")
        print(f"  {suspicious_count} records marked as suspicious")
        print(f"  Saved to: {output_file}")
        
        # Also create CSV file for easier analysis
        self.create_csv_file(records, output_dir)
        
        return records
    
    def create_csv_file(self, records, output_dir):
        """Create CSV file for CDR records"""
        
        csv_file = os.path.join(output_dir, 'cdr_records.csv')
        
        if not records:
            print("  No records to write to CSV")
            return
        
        # Define CSV headers
        headers = [
            'cdr_id', 'timestamp', 'call_type', 'duration_seconds',
            'caller_number', 'receiver_number', 'caller_id', 'receiver_id',
            'cell_tower_id', 'location_area', 'is_roaming', 'is_international',
            'is_suspicious', 'network_id'
        ]
        
        # Write CSV
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for record in records:
                # Flatten the record for CSV
                csv_record = {
                    'cdr_id': record['cdr_id'],
                    'timestamp': record['timestamp'],
                    'call_type': record['call_type'],
                    'duration_seconds': record['duration_seconds'],
                    'caller_number': record['caller_number'],
                    'receiver_number': record['receiver_number'],
                    'caller_id': record['caller_id'],
                    'receiver_id': record['receiver_id'],
                    'cell_tower_id': record['cell_tower_id'],
                    'location_area': record['location_area'],
                    'is_roaming': record['is_roaming'],
                    'is_international': record['is_international'],
                    'is_suspicious': record['is_suspicious'],
                    'network_id': record['network_id'] or ''
                }
                writer.writerow(csv_record)
        
        print(f"  Created CSV file: {csv_file}")


def main():
    """Main function to generate CDR records"""
    print("Starting CDR Record Generation")
    print("=" * 40)
    
    # Initialize generator
    generator = CDRecordGenerator()
    
    # Generate records
    records = generator.generate_cdr_records(count=7000)
    
    print("\nCDR record generation completed!")
    print(f"Total records generated: {len(records)}")
    
    # Show sample
    if records:
        sample = records[0]
        print(f"\nSample CDR Record:")
        print(f"  ID: {sample['cdr_id']}")
        print(f"  Timestamp: {sample['timestamp']}")
        print(f"  Type: {sample['call_type']}")
        print(f"  Duration: {sample['duration_seconds']} seconds")
        print(f"  From: {sample['caller_number']}")
        print(f"  To: {sample['receiver_number']}")
        print(f"  Suspicious: {sample['is_suspicious']}")


if __name__ == "__main__":
    main()