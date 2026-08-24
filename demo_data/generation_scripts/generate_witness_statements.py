#!/usr/bin/env python3
"""
BlackBox SIH26189 Witness Statement Generator
Generates 1,500+ synthetic witness statements
"""

import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class WitnessStatementGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # Statement types
        self.statement_types = [
            ('EYEWITNESS', 0.4, 'Eyewitness Account'),
            ('CHARACTER', 0.2, 'Character Witness'),
            ('EXPERT', 0.1, 'Expert Witness'),
            ('HEARSAY', 0.15, 'Hearsay/Second-hand Information'),
            ('ALIBI', 0.15, 'Alibi Statement')
        ]
        
        # Relationship to case/subject
        self.relationships = [
            ('Direct Eyewitness', 0.25),
            ('Heard About Incident', 0.20),
            ('Saw Before/After', 0.15),
            ('Knows Accused Personally', 0.10),
            ('Knows Victim Personally', 0.10),
            ('Neighbor', 0.08),
            ('Colleague/Co-worker', 0.07),
            ('Friend', 0.05),
            ('Family Member', 0.03),
            ('Stranger/Passerby', 0.02)
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
    
    def generate_statement_id(self, sequence):
        """Generate a unique witness statement ID"""
        return f"WS/{sequence:08d}"
    
    def generate_timestamp(self, incident_date=None):
        """Generate a realistic timestamp for when statement was given"""
        if incident_date:
            # Statement typically given after incident
            incident_dt = datetime.fromisoformat(incident_date)
            # Statement given 0-30 days after incident
            days_after = random.randint(0, 30)
            statement_date = incident_dt + timedelta(days=days_after)
        else:
            # Random time in our range (2024-01-01 to 2026-06-30)
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2026, 6, 30)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            statement_date = start_date + timedelta(days=random_days)
        
        # Add time of day
        statement_date = statement_date.replace(
            hour=random.randint(8, 20),  # Statements usually taken during day
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return statement_date
    
    def select_witness_and_related_entities(self, case_id=None, is_suspicious=False, network_id=None):
        """Select witness and entities related to the statement"""
        
        # Select witness (could be anyone from population)
        all_people = list(self.canonical_entities['people'].keys())
        witness_id = random.choice(all_people) if all_people else None
        
        # Get witness details
        witness = self.canonical_entities['people'].get(witness_id, {}) if witness_id else {}
        
        # Select entities related to what witness saw/knows
        related_entities = {
            'people': [],
            'vehicles': [],
            'locations': [],
            'phone_numbers': []
        }
        
        # If statement is about a specific case/network, select related entities
        if case_id and case_id in self.cases:
            case = self.cases[case_id]
            primary_network = case.get('primary_network')
            
            # Add people from case/network
            if primary_network and primary_network in self.criminal_networks:
                network = self.criminal_networks[primary_network]
                network_members = network.get('members', [])
                if network_members:
                    # Witness might know 0-3 people involved
                    num_known = min(len(network_members), random.randint(0, 3))
                    if num_known > 0:
                        related_entities['people'] = random.sample(network_members, num_known)
            
            # Add locations from case
            case_locations = case.get('locations', [])
            if case_locations:
                related_entities['locations'].extend(random.sample(case_locations, 
                                                               min(len(case_locations), random.randint(0, 2))))
        
        elif is_suspicious and network_id and network_id in self.criminal_networks:
            # Statement about suspicious network activity
            network = self.criminal_networks[network_id]
            network_members = network.get('members', [])
            if network_members:
                # Witness might know 0-2 network members
                num_known = min(len(network_members), random.randint(0, 2))
                if num_known > 0:
                    related_entities['people'] = random.sample(network_members, num_known)
        
        # If no specific connections, witness might still have observed general activity
        if not related_entities['people'] and not related_entities['locations']:
            # Witness might have seen random people/vehicles/locations
            if all_people and random.random() < 0.3:
                num_random_people = random.randint(1, 2)
                related_entities['people'] = random.sample(all_people, 
                                                         min(num_random_people, len(all_people)))
            
            all_locations = list(self.canonical_entities['locations'].keys())
            if all_locations and random.random() < 0.4:
                num_random_locations = random.randint(1, 2)
                related_entities['locations'] = random.sample(all_locations, 
                                                          min(num_random_locations, len(all_locations)))
            
            all_vehicles = list(self.canonical_entities['vehicles'].keys())
            if all_vehicles and random.random() < 0.2:
                num_random_vehicles = random.randint(0, 1)
                related_entities['vehicles'] = random.sample(all_vehicles, 
                                                           min(num_random_vehicles, len(all_vehicles)))
        
        # Get witness's own contact info
        if witness_id:
            witness_phones = witness.get('phone_numbers', [])
            if witness_phones:
                related_entities['phone_numbers'].extend(witness_phones)
            
            witness_locations = witness.get('addresses', [])
            if witness_locations:
                related_entities['locations'].extend(witness_locations)
        
        # Remove duplicates
        for key in related_entities:
            related_entities[key] = list(set(related_entities[key]))
        
        return witness_id, witness, related_entities
    
    def generate_witness_statement(self, sequence, case_id=None, is_suspicious=False, network_id=None):
        """Generate a single witness statement"""
        
        # Get incident date if case-related
        incident_date = None
        if case_id and case_id in self.cases:
            incident_date = self.cases[case_id].get('opening_date')
        
        # Generate statement timestamp
        statement_timestamp = self.generate_timestamp(incident_date)
        
        # Select statement type
        statement_types, weights, _ = zip(*self.statement_types)
        statement_type = random.choices(statement_types, weights=weights)[0]
        statement_type_desc = [t[2] for t in self.statement_types if t[0] == statement_type][0]
        
        # Select witness and related entities
        witness_id, witness, related_entities = self.select_witness_and_related_entities(
            case_id, is_suspicious, network_id
        )
        
        # Select relationship to case/subject
        relationships, rel_weights = zip(*self.relationships)
        relationship = random.choices(relationships, weights=rel_weights)[0]
        
        # Determine if statement is considered reliable/suspicious
        is_reliable = random.random() < 0.7  # 70% baseline reliability
        if is_suspicious:
            is_reliable = random.random() < 0.4  # Suspicious statements less likely reliable
        
        # Generate statement content
        statement_content = self.generate_statement_content(
            statement_type, relationship, witness, related_entities, 
            incident_date, statement_timestamp, is_reliable, is_suspicious
        )
        
        # Create witness statement record
        witness_record = {
            'statement_id': self.generate_statement_id(sequence),
            'statement_type': statement_type,
            'statement_type_description': statement_type_desc,
            'timestamp': statement_timestamp.isoformat(),
            'incident_date': incident_date,
            'case_id': case_id,
            'witness_id': witness_id,
            'witness_name': witness.get('canonical_name', 'Anonymous'),
            'witness_age': witness.get('age', 'Unknown'),
            'witness_gender': witness.get('gender', 'Unknown'),
            'witness_occupation': witness.get('occupation', 'Unknown'),
            'relationship_to_case': relationship,
            'statement_content': statement_content,
            'related_entities': related_entities,
            'is_reliable': is_reliable,
            'is_suspicious': is_suspicious,
            'network_id': network_id if is_suspicious else None,
            'metadata': {
                'word_count': len(statement_content.split()),
                'character_count': len(statement_content),
                'generated_at': datetime.now().isoformat(),
                'version': '1.0',
                'recording_officer': f"OFF{random.randint(1000, 9999)}",
                'statement_taken_at': random.choice([
                    'Police Station', 'Witness Home', 'Witness Workplace', 
                    'Court Premises', 'Legal Aid Office', 'Mobile Police Van'
                ])
            }
        }
        
        return witness_record
    
    def generate_statement_content(self, statement_type, relationship, witness, 
                                 related_entities, incident_date, statement_timestamp, 
                                 is_reliable, is_suspicious):
        """Generate realistic witness statement content"""
        
        # Get witness details
        witness_name = witness.get('canonical_name', 'Anonymous Witness')
        witness_age = witness.get('age', 'Unknown')
        witness_gender = witness.get('gender', 'Unknown')
        witness_occupation = witness.get('occupation', 'Unknown')
        
        # Get related entity details
        people_details = []
        for person_id in related_entities['people'][:3]:
            person = self.canonical_entities['people'].get(person_id, {})
            if person:
                name = person.get('canonical_name', 'Unknown')
                age = person.get('age', 'Unknown')
                people_details.append(f"{name} (Age: {age})")
        
        vehicle_details = []
        for vehicle_id in related_entities['vehicles'][:2]:
            vehicle = self.canonical_entities['vehicles'].get(vehicle_id, {})
            if vehicle:
                reg = vehicle.get('registration_number', 'Unknown')
                model = vehicle.get('model', 'Unknown')
                vehicle_details.append(f"{reg} ({model})")
        
        location_details = []
        for location_id in related_entities['locations'][:2]:
            location = self.canonical_entities['locations'].get(location_id, {})
            if location:
                address = location.get('address', 'Unknown')
                area = location.get('area', 'Unknown')
                city = location.get('city', 'Unknown')
                location_details.append(f"{address}, {area}, {city}")
        
        # Base opening
        openings = [
            f"I, {witness_name}, aged {witness_age} years, residing at {witness.get('addresses', ['Unknown'])[0] if witness.get('addresses') else 'Unknown'}, ",
            f"On {statement_timestamp.strftime('%d-%m-%Y')} at approximately {statement_timestamp.strftime('%H:%M hours')}, ",
            f"This statement is being recorded in connection with an incident that occurred ",
            f"I hereby state that on or about ",
            f"In my capacity as a {witness_occupation}, I wish to state that "
        ]
        
        opening = random.choice(openings)
        
        # Build statement based on type
        if statement_type == 'EYEWITNESS':
            content = self._generate_eyewitness_content(
                opening, witness_name, relationship, people_details, 
                vehicle_details, location_details, incident_date, is_reliable, is_suspicious
            )
        elif statement_type == 'CHARACTER':
            content = self._generate_character_content(
                opening, witness_name, witness_occupation, relationship, 
                people_details, is_reliable, is_suspicious
            )
        elif statement_type == 'EXPERT':
            content = self._generate_expert_content(
                opening, witness_name, witness_occupation, relationship, 
                people_details, is_reliable, is_suspicious
            )
        elif statement_type == 'HEARSAY':
            content = self._generate_hearsay_content(
                opening, witness_name, relationship, people_details, 
                is_reliable, is_suspicious
            )
        else:  # ALIBI
            content = self._generate_alibi_content(
                opening, witness, relationship, people_details, 
                location_details, incident_date, statement_timestamp, 
                is_reliable, is_suspicious
            )
        
        # Add closing
        closings = [
            "I verify that the contents of this statement are true and correct to the best of my knowledge and belief.",
            "I solemnly affirm that what I have stated above is true and correct.",
            "I declare that the foregoing statement is true and correct to the best of my knowledge.",
            "I affirm that I have stated the facts truly and correctly.",
            "I confirm that the contents of this statement are true and accurate."
        ]
        
        content += " " + random.choice(closings) + "."
        
        return content
    
    def _generate_eyewitness_content(self, opening, witness_name, relationship, 
                                   people_details, vehicle_details, location_details, 
                                   incident_date, is_reliable, is_suspicious):
        """Generate eyewitness statement content"""
        
        content = opening
        
        if incident_date:
            content += f"the incident of {incident_date} "
        else:
            content += f"an incident "
        
        content += f"that I witnessed while {self._get_witness_activity()}. "
        
        # What they saw
        if people_details:
            content += f"I observed {', '.join(people_details[:2])}"
            if len(people_details) > 2:
                content += f" and others"
            content += " "
        
        if vehicle_details:
            content += f"in association with vehicle(s) {', '.join(vehicle_details)} "
        
        if location_details:
            content += f"at or near {location_details[0]} "
        
        # Action observed
        actions = [
            "engaged in a heated argument",
            "exchanging items or packages",
            "appearing to conduct a transaction",
            "behaving suspiciously and looking around frequently",
            "entering and exiting a building rapidly",
            "loading/unloading items from a vehicle",
            "engaged in what appeared to be a physical altercation",
            "communicating via mobile phones in a secretive manner",
            "appearing to scout or survey the area",
            "attempting to conceal their identities or activities"
        ]
        
        content += f"I observed them {random.choice(actions)}. "
        
        # Time and duration
        if random.random() < 0.7:
            duration = random.randint(5, 120)  # 5 seconds to 2 minutes
            content += f"The incident lasted approximately {duration} seconds. "
        
        # Additional observations
        if random.random() < 0.4:
            observations = [
                "I noticed they were wearing similar clothing.",
                "They appeared to know each other well.",
                "There was tension in their body language.",
                "One person seemed to be giving instructions to others.",
                "They were speaking in hushed tones.",
                "I observed hand signals being exchanged.",
                "One individual kept watch while others were active.",
                "They left the scene in different directions."
            ]
            content += f"Additionally, {random.choice(observations)} "
        
        # Reliability qualifier
        if not is_reliable:
            qualifiers = [
                "However, I must state that my view was partially obstructed.",
                "It was dark/dimly lit at the time, so my observation may not be complete.",
                "I was at a considerable distance, so I cannot identify individuals with certainty.",
                "The event happened quickly, and I may have missed some details.",
                "I was distracted at the moment and may not have seen everything clearly.",
                "There were obstructions that limited my field of view.",
                "I was under stress at the time, which may affect my recollection.",
                "It has been some time since the incident, and my memory may have faded."
            ]
            content += f" {random.choice(qualifiers)}"
        elif is_suspicious and random.random() < 0.5:
            content += f" What I observed appeared suspicious and warranted reporting to authorities."
        
        return content
    
    def _generate_character_content(self, opening, witness_name, occupation, 
                                  relationship, people_details, is_reliable, is_suspicious):
        """Generate character witness statement content"""
        
        content = opening
        
        content += f"I have known {witness_name if relationship == 'Knows Accused Personally' else 'the subject'} "
        content += f"for approximately {random.randint(1, 15)} years in my capacity as a {occupation}. "
        
        if people_details:
            content += f"During this time, I have observed {people_details[0]} "
            content += f"to be {random.choice(['peaceful and law-abiding', 'responsible and reliable', 'helpful and cooperative', 'quiet and reserved'])}. "
        
        # Character traits
        positive_traits = [
            "honest and trustworthy",
            "peaceful in nature",
            "respectful of others and property",
            "helpful to neighbors and community",
            "responsible in personal and professional life",
            "law-abiding citizen",
            "of good moral character",
            "not given to violence or aggression",
            "respectful of law and authority",
            "known for integrity and honesty"
        ]
        
        negative_traits = [
            "known to have a volatile temper",
            "has been observed in questionable company",
            "has associations with persons of dubious character",
            "has been seen in suspicious circumstances",
            "known to associate with known offenders",
            "has a reputation for being unreliable",
            "has been involved in minor disputes previously",
            "known to have financial difficulties",
            "associates with persons involved in illegal activities",
            "has shown disregard for rules and regulations"
        ]
        
        if is_suspicious and not is_reliable:
            trait = random.choice(negative_traits)
        else:
            trait = random.choice(positive_traits)
        
        content += f"I believe {witness_name if relationship == 'Knows Accused Personally' else 'the subject'} "
        content += f"to be {trait}. "
        
        # Specific examples
        if random.random() < 0.3:
            examples = [
                "For instance, I have seen them help elderly neighbors with groceries.",
                "They regularly participate in community clean-up activities.",
                "I have observed them resolving conflicts peacefully.",
                "They maintain their property well and respect neighborhood rules.",
                "They are known to be punctual and reliable in their commitments."
            ]
            content += f" {random.choice(examples)}"
        
        return content
    
    def _generate_expert_content(self, opening, witness_name, occupation, 
                                 relationship, people_details, is_reliable, is_suspicious):
        """Generate expert witness statement content"""
        
        content = opening
        
        content += f"I am a qualified {occupation} with {random.randint(5, 25)} years of experience. "
        content += f"I was consulted to provide expert opinion on certain aspects of the case. "
        
        # Expertise areas
        expertise_areas = [
            "handwriting analysis and document examination",
            "financial transaction patterns and money laundering detection",
            "digital forensics and electronic evidence analysis",
            "ballistics and firearms examination",
            "narcotics and chemical substance identification",
            "audio enhancement and voice identification",
            "video surveillance analysis and authentication",
            "financial statement analysis and fraud detection",
            "communication pattern analysis and network mapping",
            "behavioral analysis and threat assessment"
        ]
        
        expertise = random.choice(expertise_areas)
        content += f"My area of expertise includes {expertise}. "
        
        # Analysis performed
        if people_details:
            content += f"I have examined evidence related to {people_details[0] if people_details else 'the subject'} "
        else:
            content += f"I have examined the evidence provided in this case. "
        
        analysis_types = [
            "document authenticity and alteration",
            "financial irregularities and suspicious patterns",
            "communication timing and frequency analysis",
            "audio/video authenticity and tampering",
            "substance composition and purity",
            "timeline reconstruction from available evidence",
            "link analysis between individuals and entities",
            "pattern recognition in sequential events",
            "risk assessment and threat evaluation",
            "evidence correlation and corroboration"
        ]
        
        content += f"My analysis focused on {random.choice(analysis_types)}. "
        
        # Findings
        if is_suspicious and not is_reliable:
            findings = [
                "I observed irregularities that require further investigation.",
                "The evidence shows patterns consistent with illicit activities.",
                "There are inconsistencies that cannot be explained by legitimate means.",
                "The financial transactions demonstrate structuring patterns.",
                "Communication patterns suggest coordination of activities.",
                "Physical evidence shows signs of tampering or alteration.",
                "The digital footprint indicates attempts to conceal activities.",
                "Behavioral patterns are consistent with those involved in similar offenses.",
                "There are gaps in the evidence that suggest undisclosed activities.",
                "The materials examined show characteristics of controlled substances."
            ]
        else:
            findings = [
                "No irregularities were detected in the examined materials.",
                "The evidence appears consistent with legitimate activities.",
                "Financial transactions align with declared income sources.",
                "Communication patterns show normal personal/business contacts.",
                "No evidence of tampering or alteration was found.",
                "The timeline of events is coherent and plausible.",
                "No link to criminal enterprises could be established from the evidence.",
                "Materials examined show no signs of illicit substances.",
                "Digital evidence appears authentic and unaltered.",
                "Behavioral observations are within normal parameters."
            ]
        
        content += f"I found that {random.choice(findings)}. "
        
        # Conclusion
        if is_suspicious and not is_reliable:
            conclusions = [
                "Based on my analysis, further forensic examination is warranted.",
                "The evidence requires additional expert analysis from related disciplines.",
                "My findings suggest the need for expanded investigation scope.",
                "The irregularities observed merit law enforcement attention.",
                "Based on the evidence examined, suspicious activities cannot be ruled out."
            ]
        else:
            conclusions = [
                "Based on my analysis, no evidence of illegal activity was detected.",
                "The materials examined appear to be genuine and unaltered.",
                "Financial records show no signs of money laundering or fraud.",
                "Communication patterns are consistent with legitimate associations.",
                "Based on the evidence, no connection to criminal enterprises could be established."
            ]
        
        content += f" {random.choice(conclusions)}"
        
        return content
    
    def _generate_hearsay_content(self, opening, witness_name, relationship, 
                                  people_details, is_reliable, is_suspicious):
        """Generate hearsay/second-hand statement content"""
        
        content = opening
        
        content += f"I did not personally witness the incident but received information "
        sources = [
            "from a reliable source who was present at the scene.",
            "through conversation with individuals who observed the events.",
            "from multiple accounts that were consistent with each other.",
            "via communication from someone who was in the vicinity at the time.",
            "through information shared by coworkers/acquaintances who were present."
        ]
        content += f"{random.choice(sources)} "
        
        if people_details:
            content += f"The information I received pertains to {people_details[0] if people_details else 'certain individuals'} "
        else:
            content += f"The information I received pertains to the reported incident. "
        
        content += f"According to what I was told, "
        
        # What they heard
        heard_information = [
            "there was an exchange of items or money between individuals.",
            "a heated argument escalated into a physical confrontation.",
            "suspicious packages were transferred between individuals.",
            "individuals were seen entering and exiting a location rapidly.",
            "there was discussion about plans for future activities.",
            "money or valuables appeared to change hands.",
            "individuals were using coded language or signals.",
            "there was movement of vehicles in a coordinated manner.",
            "individuals appeared to be conducting surveillance on a location.",
            "there was discussion about avoiding detection by authorities."
        ]
        
        content += f"{random.choice(heard_information)}. "
        
        # Source reliability
        if not is_reliable:
            source_notes = [
                "However, I must emphasize that this is second-hand information.",
                "I cannot verify the accuracy of what I was told.",
                "The reliability of my source is unknown to me.",
                "I have not personally confirmed the information received.",
                "This information should be verified through direct observation or evidence."
            ]
            content += f" {random.choice(source_notes)}"
        elif is_suspicious and random.random() < 0.4:
            content += f" The information received appeared credible and warranted further inquiry. "
        
        return content
    
    def _generate_alibi_content(self, opening, witness, relationship, 
                                people_details, location_details, incident_date, 
                                statement_timestamp, is_reliable, is_suspicious):
        """Generate alibi statement content"""
        
        content = opening
        
        if incident_date:
            content += f"on {incident_date} "
        else:
            content += f"at the time of the reported incident "
        
        witness_name = witness.get("canonical_name", "Anonymous")
        content += f"I can confirm that {witness_name} "
        
        # Alibi details
        alibi_scenarios = [
            "was in my company at [location] from [start time] to [end time].",
            "was at [location] engaged in [activity] during the relevant time period.",
            "was residing at their home address and did not leave the premises.",
            "was at [workplace] performing their regular duties.",
            "was attending a [event/function] at [location] with others.",
            "was traveling between [location1] and [location2] during the stated period.",
            "was engaged in [activity] at [location] and can provide corroborating evidence.",
            "was with family members at [location] during the entire time period.",
            "was receiving medical treatment at [facility] and was unable to move.",
            "was participating in [regular activity] at [location] as per their routine."
        ]
        
        scenario = random.choice(alibi_scenarios)
        
        # Fill in details
        if location_details:
            location = location_details[0]
        else:
            location = witness.get('addresses', ['Unknown Location'])[0] if witness.get('addresses') else 'Unknown Location'
        
        if people_details:
            activity_context = f"with {people_details[0]}" if people_details else ""
        else:
            activity_context = ""
        
        times = [
            f"between {random.randint(8, 10)}:00 and {random.randint(16, 18)}:00 hours",
            f"from {random.randint(9, 11)}:00 to {random.randint(17, 19)}:00 hours",
            f"during the evening hours of {random.randint(18, 20)}:00 to {random.randint(22, 24)}:00",
            f"throughout the daytime period of {random.randint(6, 8)}:00 to {random.randint(18, 20)}:00",
            f"during business hours of {random.randint(9, 10)}:00 to {random.randint(17, 18)}:00 hours"
        ]
        time_period = random.choice(times)
        
        activities = [
            "watching television",
            "having dinner with family",
            "performing household chores",
            "engaged in office work",
            "attending a meeting",
            "participating in religious activities",
            "engaged in physical exercise",
            "receiving visitors at home",
            "talking on telephone",
            "resting at home"
        ]
        activity = random.choice(activities)
        
        # Replace placeholders
        scenario = scenario.replace("[location]", location)
        scenario = scenario.replace("[start time]", time_period.split(" to ")[0] if " to " in time_period else time_period.split(" of ")[0] if " of " in time_period else "09:00")
        scenario = scenario.replace("[end time]", time_period.split(" to ")[1] if " to " in time_period else time_period.split(" of ")[1] if " of " in time_period else "17:00")
        scenario = scenario.replace("[activity]", activity)
        scenario = scenario.replace("[event/function]", random.choice(["family function", "community meeting", "religious ceremony", "office seminar"]))
        scenario = scenario.replace("[location1]", location)
        scenario = scenario.replace("[location2]", random.choice(location_details) if location_details else "Nearby Area")
        scenario = scenario.replace("[facility]", random.choice(["Government Hospital", "Private Clinic", "Nursing Home", "Health Center"]))
        scenario = scenario.replace("[regular activity]", activity)
        
        content += scenario + ". "
        
        # Corroborating evidence
        if random.random() < 0.3 and is_reliable:
            evidence = [
                "I can provide CCTV footage from the location as corroborating evidence.",
                "Others present can confirm this alibi.",
                "Transaction records show their presence at the location.",
                "Mobile phone location data can verify their whereabouts.",
                "Attendance records from the venue can confirm presence.",
                "Witnesses at the location can corroborate this statement."
            ]
            content += f" {random.choice(evidence)}"
        elif not is_reliable:
            content += " However, I acknowledge that this alibi should be verified through independent means. "
        
        return content
    
    def _get_witness_activity(self):
        """Get what witness was doing when they observed incident"""
        activities = [
            "walking home from work",
            "waiting for public transport",
            "standing at my balcony/window",
            "driving past the location",
            "getting groceries from nearby store",
            "dropping/picking up children from school",
            "out for a morning/evening walk",
            "waiting for someone at a nearby location",
            "engaged in my regular morning jog",
            "returning from a visit to a relative/friend",
            "standing in a queue for services",
            "waiting for my turn at an office counter",
            "sitting in a park/garden nearby",
            "waiting for my vehicle to be serviced",
            "having tea/coffee at a nearby stall"
        ]
        return random.choice(activities)
    
    def generate_witness_statements(self, count=2000, output_dir='demo_data/full_dataset/witness_statements'):
        """Generate multiple witness statements"""
        
        print(f"Generating {count} witness statements...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get case IDs for assigning some statements to cases
        case_ids = list(self.cases.keys()) if self.cases else [None]
        network_ids = list(self.criminal_networks.keys()) if self.criminal_networks else [None]
        
        statements = []
        case_assigned_count = 0
        suspicious_count = 0
        
        for i in range(count):
            # Determine assignment
            case_id = None
            network_id = None
            is_suspicious = False
            
            # 30% chance of being case-related
            if random.random() < 0.3 and case_ids[0] is not None:
                case_id = random.choice(case_ids)
                case_assigned_count += 1
                
                # 20% chance of case-related statement being suspicious
                if random.random() < 0.2:
                    is_suspicious = True
                    suspicious_count += 1
                    # Get network from case
                    if case_id in self.cases:
                        primary_network = self.cases[case_id].get('primary_network')
                        if primary_network and primary_network in self.criminal_networks:
                            network_id = primary_network
            
            # 10% chance of being network-related but not case-specific
            elif random.random() < 0.1 and network_ids[0] is not None:
                network_id = random.choice(network_ids)
                is_suspicious = True
                suspicious_count += 1
            
            # Generate statement
            stmt_sequence = i + 1
            statement = self.generate_witness_statement(
                sequence=stmt_sequence,
                case_id=case_id,
                is_suspicious=is_suspicious,
                network_id=network_id
            )
            
            statements.append(statement)
            
            # Progress indicator
            if (i + 1) % 150 == 0:
                print(f"  Generated {i + 1} statements...")
        
        # Save statements as JSON file (structured format)
        output_file = os.path.join(output_dir, 'witness_statements.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statements, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(statements)} witness statements")
        print(f"  {case_assigned_count} statements assigned to cases")
        print(f"  {suspicious_count} statements marked as suspicious")
        print(f"  Saved to: {output_file}")
        
        # Also create CSV file for easier analysis
        self.create_csv_file(statements, output_dir)
        
        return statements
    
    def create_csv_file(self, statements, output_dir):
        """Create CSV file for witness statements"""
        
        csv_file = os.path.join(output_dir, 'witness_statements.csv')
        
        if not statements:
            print("  No statements to write to CSV")
            return
        
        # Define CSV headers (flattened structure)
        headers = [
            'statement_id', 'statement_type', 'timestamp', 'incident_date', 'case_id',
            'witness_id', 'witness_name', 'witness_age', 'witness_gender', 'witness_occupation',
            'relationship_to_case', 'is_reliable', 'is_suspicious', 'network_id',
            'word_count', 'character_count'
        ]
        
        # Write CSV
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for statement in statements:
                # Flatten the statement for CSV
                csv_record = {
                    'statement_id': statement['statement_id'],
                    'statement_type': statement['statement_type'],
                    'timestamp': statement['timestamp'],
                    'incident_date': statement['incident_date'] or '',
                    'case_id': statement['case_id'] or '',
                    'witness_id': statement['witness_id'] or '',
                    'witness_name': statement['witness_name'],
                    'witness_age': statement['witness_age'],
                    'witness_gender': statement['witness_gender'],
                    'witness_occupation': statement['witness_occupation'],
                    'relationship_to_case': statement['relationship_to_case'],
                    'is_reliable': statement['is_reliable'],
                    'is_suspicious': statement['is_suspicious'],
                    'network_id': statement['network_id'] or '',
                    'word_count': statement['metadata']['word_count'],
                    'character_count': statement['metadata']['character_count']
                }
                writer.writerow(csv_record)
        
        print(f"  Created CSV file: {csv_file}")


def main():
    """Main function to generate witness statements"""
    print("Starting Witness Statement Generation")
    print("=" * 40)
    
    # Initialize generator
    generator = WitnessStatementGenerator()
    
    # Generate statements
    statements = generator.generate_witness_statements(count=2000)
    
    print("\nWitness statement generation completed!")
    print(f"Total statements generated: {len(statements)}")
    
    # Show sample
    if statements:
        sample = statements[0]
        print(f"\nSample Witness Statement:")
        print(f"  ID: {sample['statement_id']}")
        print(f"  Type: {sample['statement_type_description']}")
        print(f"  Witness: {sample['witness_name']} (Age: {sample['witness_age']})")
        print(f"  Relationship: {sample['relationship_to_case']}")
        print(f"  Reliable: {sample['is_reliable']}")
        print(f"  Suspicious: {sample['is_suspicious']}")
        print(f"  Word Count: {sample['metadata']['word_count']}")
        print(f"  Preview: {sample['statement_content'][:100]}...")


if __name__ == "__main__":
    main()