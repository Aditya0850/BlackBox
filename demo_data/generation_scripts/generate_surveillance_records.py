#!/usr/bin/env python3
"""
BlackBox SIH26189 Surveillance Record Generator
Generates 2,500+ synthetic surveillance records
"""

import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class SurveillanceRecordGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # Surveillance types
        self.surveillance_types = [
            ('PHYSICAL', 0.35, 'Physical Surveillance'),
            ('TECHNICAL', 0.25, 'Technical/Electronic Surveillance'),
            ('COMMUNICATION', 0.20, 'Communication Interception'),
            ('FINANCIAL', 0.10, 'Financial Transaction Monitoring'),
            ('MOVEMENT', 0.10, 'Movement/Vehicle Tracking')
        ]
        
        # Equipment types
        self.equipment_types = [
            'CCTV Camera', 'Audio Recorder', 'GPS Tracker',
            'Mobile Tower Dump', 'Call Intercept Equipment',
            'ANPR Camera', 'Facial Recognition System',
            'Drone/UAV', 'Binoculars', 'Night Vision Gear',
            'Radio Scanner', 'SIM Card Reader', 'Data Extraction Tool'
        ]
    
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
        print(f"  {len(self.canonical_entities['vehicles'])} vehicles")
        print(f"  {len(self.canonical_entities['locations'])} locations")
        print(f"  {len(self.canonical_entities['organizations'])} organizations")
        print(f"  {len(self.criminal_networks)} criminal networks")
        print(f"  {len(self.cases)} cases")
    
    def generate_surveillance_id(self, sequence):
        """Generate a unique surveillance record ID"""
        return f"SURV/{sequence:08d}"
    
    def generate_timestamp(self, duration_hours=None):
        """Generate a realistic timestamp for surveillance operation"""
        # Random time in our range (2024-01-01 to 2026-06-30)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2026, 6, 30)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        start_timestamp = start_date + timedelta(days=random_days)
        
        # Add time of day (surveillance often starts evening/night)
        if random.random() < 0.6:  # 60% during evening/night hours
            hour = random.randint(18, 23)  # 6 PM to 11 PM
        else:
            hour = random.randint(0, 23)
            
        start_timestamp = start_timestamp.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Calculate end time if duration specified
        if duration_hours is None:
            # Random duration between 2 and 24 hours
            duration_hours = random.randint(2, 24)
        
        end_timestamp = start_timestamp + timedelta(hours=duration_hours)
        
        return start_timestamp, end_timestamp, duration_hours
    
    def select_subjects(self, is_suspicious=False, network_id=None, case_id=None):
        """Select subjects under surveillance"""
        subjects = {
            'people': [],
            'vehicles': [],
            'locations': [],
            'phone_numbers': []
        }
        
        # Get people from criminal networks if case/network-related
        if (case_id and case_id in self.cases) or (network_id and network_id in self.criminal_networks):
            # Try to get subjects from case or network
            target_ids = []
            
            if case_id and case_id in self.cases:
                case = self.cases[case_id]
                # Get primary network from case
                primary_network = case.get('primary_network')
                if primary_network and primary_network in self.criminal_networks:
                    target_ids.extend(self.criminal_networks[primary_network].get('members', []))
            
            if network_id and network_id in self.criminal_networks:
                target_ids.extend(self.criminal_networks[network_id].get('members', []))
            
            # Remove duplicates
            target_ids = list(set(target_ids))
            
            if target_ids:
                # Select 1-5 subjects from network
                num_subjects = min(len(target_ids), random.randint(1, 5))
                selected_people = random.sample(target_ids, num_subjects)
                subjects['people'] = selected_people
                
                # Get related vehicles, phones, locations for these people
                for person_id in selected_people:
                    person = self.canonical_entities['people'].get(person_id, {})
                    
                    # Add phone numbers
                    person_phones = person.get('phone_numbers', [])
                    if person_phones:
                        subjects['phone_numbers'].extend(random.sample(person_phones, 
                                                                       min(len(person_phones), random.randint(1, 2))))
                    
                    # Add vehicles
                    person_vehicles = person.get('vehicles', [])
                    if person_vehicles:
                        subjects['vehicles'].extend(random.sample(person_vehicles, 
                                                                min(len(person_vehicles), random.randint(0, 2))))
                    
                    # Add locations/addresses
                    person_locations = person.get('addresses', [])
                    if person_locations:
                        subjects['locations'].extend(random.sample(person_locations, 
                                                                   min(len(person_locations), random.randint(0, 2))))
        
        # If no network subjects, select random subjects
        if not subjects['people']:
            all_people = list(self.canonical_entities['people'].keys())
            if all_people:
                num_people = random.randint(1, 3)
                subjects['people'] = random.sample(all_people, min(num_people, len(all_people)))
                
                # Get related entities for these people
                for person_id in subjects['people']:
                    person = self.canonical_entities['people'].get(person_id, {})
                    
                    # Add phone numbers
                    person_phones = person.get('phone_numbers', [])
                    if person_phones:
                        subjects['phone_numbers'].extend(random.sample(person_phones, 
                                                                       min(len(person_phones), random.randint(1, 2))))
                    
                    # Add vehicles
                    person_vehicles = person.get('vehicles', [])
                    if person_vehicles:
                        subjects['vehicles'].extend(random.sample(person_vehicles, 
                                                                min(len(person_vehicles), random.randint(0, 2))))
                    
                    # Add locations/addresses
                    person_locations = person.get('addresses', [])
                    if person_locations:
                        subjects['locations'].extend(random.sample(person_locations, 
                                                                   min(len(person_locations), random.randint(0, 2))))
        
        # Add some random locations as surveillance points
        all_locations = list(self.canonical_entities['locations'].keys())
        if all_locations:
            num_locations = random.randint(1, 4)
            subjects['locations'].extend(random.sample(all_locations, 
                                                       min(num_locations, len(all_locations))))
        
        # Add some random phone numbers as monitored lines
        all_phones = list(self.canonical_entities['phone_numbers'].keys())
        if all_phones:
            num_phones = random.randint(1, 3)
            subjects['phone_numbers'].extend(random.sample(all_phones, 
                                                           min(num_phones, len(all_phones))))
        
        # Add some random vehicles as tracked vehicles
        all_vehicles = list(self.canonical_entities['vehicles'].keys())
        if all_vehicles:
            num_vehicles = random.randint(1, 3)
            subjects['vehicles'].extend(random.sample(all_vehicles, 
                                                      min(num_vehicles, len(all_vehicles))))
        
        # Remove duplicates
        for key in subjects:
            subjects[key] = list(set(subjects[key]))
        
        return subjects
    
    def generate_surveillance_record(self, sequence, is_suspicious=False, network_id=None, case_id=None):
        """Generate a single surveillance record"""
        
        # Generate timestamp and duration
        start_time, end_time, duration_hours = self.generate_timestamp()
        
        # Select surveillance type based on weights
        surv_types = [t[0] for t in self.surveillance_types]
        surv_weights = [t[1] for t in self.surveillance_types]
        surv_type = random.choices(surv_types, weights=surv_weights)[0]
        surv_type_desc = [t[2] for t in self.surveillance_types if t[0] == surv_type][0]
        
        # Select subjects
        subjects = self.select_subjects(is_suspicious, network_id, case_id)
        
        # Select equipment used
        num_equipment = random.randint(1, 4)
        equipment_used = random.sample(self.equipment_types, min(num_equipment, len(self.equipment_types)))
        
        # Generate location of surveillance (primary location)
        all_locations = list(self.canonical_entities['locations'].keys())
        primary_location_id = random.choice(all_locations) if all_locations else None
        primary_location = self.canonical_entities['locations'].get(primary_location_id, {}) if primary_location_id else {}
        
        # Determine objectives based on type and subjects
        objectives = self.generate_objectives(surv_type, subjects, is_suspicious)
        
        # Generate findings
        findings = self.generate_findings(surv_type, subjects, is_suspicious, duration_hours)
        
        # Generate assessment
        assessment = self.generate_assessment(is_suspicious, findings)
        
        # Create surveillance record
        surveillance_record = {
            'surveillance_id': self.generate_surveillance_id(sequence),
            'operation_code': f"OP{random.randint(100, 999)}/{random.randint(20, 26)}",
            'start_timestamp': start_time.isoformat(),
            'end_timestamp': end_time.isoformat(),
            'duration_hours': duration_hours,
            'surveillance_type': surv_type,
            'surveillance_type_description': surv_type_desc,
            'objectives': objectives,
            'subjects_under_surveillance': subjects,
            'equipment_used': equipment_used,
            'location': {
                'location_id': primary_location_id,
                'address': primary_location.get('address', 'UNKNOWN'),
                'area': primary_location.get('area', 'UNKNOWN'),
                'city': primary_location.get('city', 'UNKNOWN'),
                'state': primary_location.get('state', 'UNKNOWN')
            },
            'findings': findings,
            'assessment': assessment,
            'is_suspicious': is_suspicious,
            'network_id': network_id if is_suspicious else None,
            'case_id': case_id,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0',
                'analyst_id': f"ANAL{random.randint(1000, 9999)}",
                'classification': 'CONFIDENTIAL' if is_suspicious else 'RESTRICTED'
            }
        }
        
        return surveillance_record
    
    def generate_objectives(self, surv_type, subjects, is_suspicious):
        """Generate surveillance objectives based on type and subjects"""
        
        objectives = []
        
        # Base objectives by type
        base_objectives = {
            'PHYSICAL': [
                'Monitor subject movements and activities',
                'Document interactions with other individuals',
                'Identify patterns of behavior and routines',
                'Gather visual evidence of suspicious activities'
            ],
            'TECHNICAL': [
                'Monitor electronic communications',
                'Track digital footprints and online activities',
                'Intercept and analyze electronic signals',
                'Gather technical evidence for investigation'
            ],
            'COMMUNICATION': [
                'Intercept and monitor telephone communications',
                'Analyze call patterns and frequency',
                'Identify communication networks and contacts',
                'Gather evidence of planned activities through communications'
            ],
            'FINANCIAL': [
                'Monitor financial transactions and money flows',
                'Identify sources and destinations of funds',
                'Detect suspicious financial patterns',
                'Trace money trails related to criminal activities'
            ],
            'MOVEMENT': [
                'Track vehicle movements and travel patterns',
                'Monitor entry/exit from specific locations',
                'Identify meeting points and rendezvous locations',
                'Gather evidence of transportation of contraband or persons'
            ]
        }
        
        # Add base objectives
        if surv_type in base_objectives:
            objectives.extend(random.sample(base_objectives[surv_type], 
                                          min(2, len(base_objectives[surv_type]))))
        
        # Add subject-specific objectives
        if subjects['people']:
            objectives.append('Establish identity and background of subjects under surveillance')
            if is_suspicious:
                objectives.append('Gather evidence linking subjects to criminal activities')
        
        if subjects['vehicles']:
            objectives.append('Monitor vehicle usage patterns and routes')
            objectives.append('Identify vehicles used for suspicious activities')
        
        if subjects['locations']:
            objectives.append('Monitor activities at locations of interest')
            objectives.append('Identify frequent visitors to locations under surveillance')
        
        if subjects['phone_numbers']:
            objectives.append('Monitor communication patterns of target numbers')
            objectives.append('Identify contacts and associates through communication analysis')
        
        # Add some generic objectives
        generic_objectives = [
            'Establish pattern of life for subjects',
            'Identify associates and network connections',
            'Gather intelligence for threat assessment',
            'Support ongoing investigations with concrete evidence',
            'Monitor for escalation in criminal activities',
            'Verify information received from informants',
            'Establish timeline of events and activities'
        ]
        
        if len(objectives) < 4:
            needed = 4 - len(objectives)
            objectives.extend(random.sample(generic_objectives, min(needed, len(generic_objectives))))
        
        return objectives[:6]  # Limit to 6 objectives
    
    def generate_findings(self, surv_type, subjects, is_suspicious, duration_hours):
        """Generate surveillance findings"""
        
        findings = []
        
        # Determine if we should generate positive findings (more likely for suspicious)
        positive_findings_chance = 0.7 if is_suspicious else 0.3
        
        if random.random() < positive_findings_chance:
            # Generate positive/suspicious findings
            positive_findings = [
                f"Subjects observed meeting with known criminals at {random.choice(['residential area', 'commercial establishment', 'isolated location'])}",
                f"Communication patterns indicate coordination between multiple subjects",
                f"Subjects observed exchanging packages or envelopes of unknown contents",
                f"Unusual travel patterns observed - subjects visiting known criminal hotspots",
                f"Financial transactions detected that do not match subjects' known income sources",
                f"Subjects observed conducting surveillance on potential targets",
                f"Evidence of counter-surveillance measures detected",
                f"Subjects observed using multiple SIM cards and frequently changing devices",
                f"Meeting patterns suggest planning of illegal activities",
                f"Subjects observed transporting unknown substances in vehicles",
                f"Communication intercepted indicates discussion of illegal activities",
                f"Subjects observed paying cash amounts inconsistent with stated occupations",
                f"Vehicles observed visiting locations associated with criminal enterprises",
                f"Subjects observed receiving payments through unconventional methods",
                f"Patterns suggest possible money laundering activities",
                f"Subjects observed engaging in activities inconsistent with legitimate business",
                f"Evidence of subject coordination through pre-arranged signals",
                f"Subjects observed conducting reconnaissance of potential targets",
                f"Financial records show unexplained large deposits or withdrawals",
                f"Subjects observed using aliases and false identities"
            ]
            
            num_findings = random.randint(1, min(4, len(positive_findings)))
            findings.extend(random.sample(positive_findings, num_findings))
        else:
            # Generate negative/neutral findings
            negative_findings = [
                f"No suspicious activities observed during surveillance period",
                f"Subjects engaged in routine daily activities consistent with stated occupations",
                f"Communication patterns normal and consistent with legitimate contacts",
                f"Travel patterns consistent with normal commuting and personal activities",
                f"No evidence of contact with known criminals or suspicious individuals",
                f"Financial transactions appear consistent with declared income sources",
                f"Subjects appeared unaware of surveillance and behaved normally",
                f"Activities observed consistent with lawful business or personal matters",
                f"No evidence of counter-surveillance or evasive behavior detected",
                f"Subjects maintained regular schedules and routines throughout observation",
                f"Communication limited to family, friends, and legitimate business contacts",
                f"Vehicle usage consistent with personal transportation needs",
                f"No observations suggesting involvement in illegal activities",
                f"Subjects conducted themselves in accordance with local laws and norms",
                f"No evidence of coordination with known criminal enterprises detected",
                f"Activities appeared to be legitimate personal or business matters",
                f"Subjects observed engaging in lawful recreational activities",
                f"Financial activity consistent with subjects' known financial profiles",
                f"Subjects appeared to be gainfully employed in legitimate occupations",
                f"No evidence suggesting preparation for illegal activities observed"
            ]
            
            num_findings = random.randint(1, min(3, len(negative_findings)))
            findings.extend(random.sample(negative_findings, num_findings))
        
        # Add some technical findings based on surveillance type
        if surv_type == 'TECHNICAL':
            tech_findings = [
                f"Technical monitoring revealed encrypted communications requiring further analysis",
                f"Digital footprint analysis shows subjects accessing suspicious websites",
                f"Metadata analysis reveals geolocation patterns of interest",
                f"Communication interception subject to legal procedures and approvals",
                f"Technical equipment functioned normally throughout surveillance period",
                f"Data collected requires specialized analysis for full interpretation",
                f"Signal strength and quality varied based on environmental factors",
                f"Some communications may have been lost due to technical limitations"
            ]
            findings.extend(random.sample(tech_findings, min(1, len(tech_findings))))
        
        elif surv_type == 'COMMUNICATION':
            comm_findings = [
                f"Call duration and frequency patterns analyzed for anomalies",
                f"SMS/text message metadata collected and analyzed",
                f"Communication logs show patterns consistent with {random.choice(['business', 'personal', 'potentially suspicious'])} activities",
                f"No evidence of encrypted communication platforms detected",
                f"Communication patterns suggest regular contact with {random.choice(['family members', 'business associates', 'unknown individuals'])}",
                f"International calls detected representing {random.randint(0, 5)}% of total communications",
                f"Peak calling hours observed between {random.randint(8, 10)}:00 and {random.randint(19, 21)}:00 hours",
                f"Call duration averaged {random.randint(30, 300)} seconds per call"
            ]
            findings.extend(random.sample(comm_findings, min(1, len(comm_findings))))
        
        return findings
    
    def generate_assessment(self, is_suspicious, findings):
        """Generate surveillance assessment based on findings"""
        
        if is_suspicious:
            assessments = [
                "ASSESSMENT: Surveillance suggests possible involvement in activities requiring further investigation.",
                "ASSESSMENT: Patterns observed warrant continued surveillance and additional investigative steps.",
                "ASSESSMENT: Evidence gathered suggests possible connection to criminal enterprises.",
                "ASSESSMENT: Subjects exhibit behaviors consistent with those under investigation for similar offenses.",
                "ASSESSMENT: Further surveillance recommended to establish complete pattern of activities.",
                "ASSESSMENT: Corroborative evidence being gathered from multiple sources.",
                "ASSESSMENT: Immediate action may be required based on developing situation.",
                "ASSESSMENT: Long-term monitoring recommended to establish complete network connections.",
                "ASSESSMENT: Cross-referencing with other intelligence sources recommended.",
                "ASSESSMENT: Financial angle of activities requires detailed examination."
            ]
        else:
            assessments = [
                "ASSESSMENT: No evidence of illegal activities detected during surveillance period.",
                "ASSESSMENT: Subjects appear to be engaged in legitimate personal or business activities.",
                "ASSESSMENT: Surveillance did not reveal any suspicious or criminal behavior.",
                "ASSESSMENT: Activities observed consistent with lawful occupations and lifestyles.",
                "ASSESSMENT: No further action recommended based on current surveillance results.",
                "ASSESSMENT: Subjects appear to be cooperating members of the community.",
                "ASSESSMENT: Surveillance conducted as part of routine monitoring yielded negative results.",
                "ASSESSMENT: No evidence suggesting warrant for continued surveillance at this time.",
                "ASSESSMENT: Activities appear to be consistent with declared professions and lifestyles.",
                "ASSESSMENT: Subjects under surveillance pose no apparent threat to public safety."
            ]
        
        return random.choice(assessments)
    
    def generate_surveillance_records(self, count=3200, output_dir='demo_data/full_dataset/surveillance_records'):
        """Generate multiple surveillance records"""
        
        print(f"Generating {count} surveillance records...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get network and case IDs for assigning some records
        network_ids = list(self.criminal_networks.keys()) if self.criminal_networks else [None]
        case_ids = list(self.cases.keys()) if self.cases else [None]
        
        records = []
        suspicious_count = 0
        
        for i in range(count):
            # Determine if this record should be suspicious (12% chance)
            is_suspicious = random.random() < 0.12
            network_id = None
            case_id = None
            
            if is_suspicious:
                # Try to associate with network or case
                if random.random() < 0.5 and network_ids[0] is not None:  # 50% network-related
                    network_id = random.choice(network_ids)
                elif random.random() < 0.3 and case_ids[0] is not None:  # 30% case-related
                    case_id = random.choice(case_ids)
                # 20% remain unassociated (generic suspicious)
                
                if network_id is not None or case_id is not None:
                    suspicious_count += 1
            
            # Generate record
            record_sequence = i + 1
            record = self.generate_surveillance_record(
                sequence=record_sequence,
                is_suspicious=is_suspicious,
                network_id=network_id,
                case_id=case_id
            )
            
            if record is not None:
                records.append(record)
            
            # Progress indicator
            if (i + 1) % 250 == 0:
                print(f"  Generated {i + 1} records...")
        
        # Save records as JSON file (structured format)
        output_file = os.path.join(output_dir, 'surveillance_records.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(records)} surveillance records")
        print(f"  {suspicious_count} records marked as suspicious")
        print(f"  Saved to: {output_file}")
        
        # Also create CSV file for easier analysis
        self.create_csv_file(records, output_dir)
        
        return records
    
    def create_csv_file(self, records, output_dir):
        """Create CSV file for surveillance records"""
        
        csv_file = os.path.join(output_dir, 'surveillance_records.csv')
        
        if not records:
            print("  No records to write to CSV")
            return
        
        # Define CSV headers (flattened structure)
        headers = [
            'surveillance_id', 'operation_code', 'start_timestamp', 'end_timestamp',
            'duration_hours', 'surveillance_type', 'surveillance_type_description',
            'location_id', 'address', 'area', 'city', 'state',
            'is_suspicious', 'network_id', 'case_id'
        ]
        
        # Write CSV
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for record in records:
                # Flatten the record for CSV
                location = record.get('location', {})
                csv_record = {
                    'surveillance_id': record['surveillance_id'],
                    'operation_code': record['operation_code'],
                    'start_timestamp': record['start_timestamp'],
                    'end_timestamp': record['end_timestamp'],
                    'duration_hours': record['duration_hours'],
                    'surveillance_type': record['surveillance_type'],
                    'surveillance_type_description': record['surveillance_type_description'],
                    'location_id': location.get('location_id', ''),
                    'address': location.get('address', ''),
                    'area': location.get('area', ''),
                    'city': location.get('city', ''),
                    'state': location.get('state', ''),
                    'is_suspicious': record['is_suspicious'],
                    'network_id': record['network_id'] or '',
                    'case_id': record['case_id'] or ''
                }
                writer.writerow(csv_record)
        
        print(f"  Created CSV file: {csv_file}")


def main():
    """Main function to generate surveillance records"""
    print("Starting Surveillance Record Generation")
    print("=" * 45)
    
    # Initialize generator
    generator = SurveillanceRecordGenerator()
    
    # Generate records
    records = generator.generate_surveillance_records(count=3200)
    
    print("\nSurveillance record generation completed!")
    print(f"Total records generated: {len(records)}")
    
    # Show sample
    if records:
        sample = records[0]
        print(f"\nSample Surveillance Record:")
        print(f"  ID: {sample['surveillance_id']}")
        print(f"  Type: {sample['surveillance_type_description']}")
        print(f"  Duration: {sample['duration_hours']} hours")
        print(f"  Location: {sample['location'].get('address', 'UNKNOWN')}")
        print(f"  Suspicious: {sample['is_suspicious']}")
        print(f"  Objectives: {len(sample['objectives'])} defined")
        print(f"  Findings: {len(sample['findings'])} items")
        print(f"  Assessment: {sample['assessment'][:100]}...")


if __name__ == "__main__":
    main()