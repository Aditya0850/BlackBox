#!/usr/bin/env python3
"""
BlackBox SIH26189 FIR/Police/Intelligence Document Generator
Generates 2,000+ synthetic FIR/police/intelligence documents
"""

import json
import random
import uuid
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class FIRDocumentGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # Document types and their characteristics
        self.document_types = [
            ('FIR', 'First Information Report', 0.4),
            ('Police Report', 'Police Investigation Report', 0.3),
            ('Intelligence Note', 'Intelligence Bureau Note', 0.2),
            ('Surveillance Report', 'Surveillance Directorate Report', 0.1)
        ]
        
        # Sections typically found in these documents
        self.document_sections = [
            'Case Details',
            'Complainant Information', 
            'Accused/Suspect Details',
            'Incident Description',
            'Evidence Collected',
            'Witness Statements',
            'Investigating Officer Notes',
            'Action Taken',
            'Status/Next Steps'
        ]
        
        # Incident types for variety
        self.incident_types = [
            'Theft', 'Robbery', 'Burglary', 'Assault', 'Fraud', 
            'Cybercrime', 'Drug Offense', 'Human Trafficking', 
            'Wildlife Crime', 'Extortion', 'Kidnapping', 'Arson',
            'Counterfeiting', 'Money Laundering', 'Illegal Arms',
            'Wildlife Poaching', 'Terror Financing', 'Corruption'
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
    
    def generate_document_id(self, doc_type, sequence):
        """Generate a unique document ID"""
        type_prefix = {
            'FIR': 'FIR',
            'Police Report': 'PR',
            'Intelligence Note': 'IN',
            'Surveillance Report': 'SR'
        }[doc_type]
        return f"{type_prefix}/{sequence:06d}"
    
    def generate_incident_timestamp(self, case_opening_date=None):
        """Generate a realistic timestamp for an incident"""
        if case_opening_date:
            # Incident typically happens before case opening
            opening_dt = datetime.fromisoformat(case_opening_date)
            # Incident happens 1-30 days before case opening
            days_before = random.randint(1, 30)
            incident_date = opening_dt - timedelta(days=days_before)
        else:
            # Random time in our range
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2026, 6, 30)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            incident_date = start_date + timedelta(days=random_days)
        
        # Add time of day
        incident_date = incident_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return incident_date
    
    def select_related_entities(self, incident_type, case_id=None):
        """Select entities related to the incident based on type and case"""
        related_people = []
        related_phones = []
        related_vehicles = []
        related_locations = []
        related_organizations = []
        
        # Get people from criminal networks if case is network-related
        if case_id and case_id in self.cases:
            case = self.cases[case_id]
            primary_network = case.get('primary_network')
            if primary_network and primary_network in self.criminal_networks:
                network = self.criminal_networks[primary_network]
                # Select some members from the network
                network_members = network.get('members', [])
                if network_members:
                    # Select 1-4 members related to this incident
                    num_related = min(len(network_members), random.randint(1, 4))
                    related_people = random.sample(network_members, num_related)
        
        # If no network connection, select random people
        if not related_people:
            all_people = list(self.canonical_entities['people'].keys())
            num_people = random.randint(1, 3)
            related_people = random.sample(all_people, min(num_people, len(all_people)))
        
        # Get related phones for selected people
        for person_id in related_people:
            person = self.canonical_entities['people'].get(person_id, {})
            person_phones = person.get('phone_numbers', [])
            if person_phones:
                # Select 1-2 phones per person
                num_phones = min(len(person_phones), random.randint(1, 2))
                related_phones.extend(random.sample(person_phones, num_phones))
        
        # Get related vehicles for selected people
        for person_id in related_people:
            person = self.canonical_entities['people'].get(person_id, {})
            person_vehicles = person.get('vehicles', [])
            if person_vehicles:
                related_vehicles.extend(person_vehicles)
        
        # Get related locations (addresses) for selected people
        for person_id in related_people:
            person = self.canonical_entities['people'].get(person_id, {})
            person_locations = person.get('addresses', [])
            if person_locations:
                related_locations.extend(person_locations)
        
        # Get related organizations for selected people
        for person_id in related_people:
            person = self.canonical_entities['people'].get(person_id, {})
            person_orgs = person.get('organizations', [])
            if person_orgs:
                related_organizations.extend(person_orgs)
        
        # Add some random entities for realism (red herrings, connections, etc.)
        all_people = list(self.canonical_entities['people'].keys())
        all_phones = list(self.canonical_entities['phone_numbers'].keys())
        all_vehicles = list(self.canonical_entities['vehicles'].keys())
        all_locations = list(self.canonical_entities['locations'].keys())
        all_orgs = list(self.canonical_entities['organizations'].keys())
        
        # Add 0-2 random people as potential connections/witnesses
        if all_people and random.random() < 0.3:
            extra_people = random.sample(all_people, min(len(all_people), random.randint(0, 2)))
            related_people.extend(extra_people)
        
        # Add 0-1 random phones as wrong numbers or misdials
        if all_phones and random.random() < 0.2:
            extra_phones = random.sample(all_phones, min(len(all_phones), random.randint(0, 1)))
            related_phones.extend(extra_phones)
        
        # Add 0-1 random vehicles as sightings or unrelated vehicles
        if all_vehicles and random.random() < 0.15:
            extra_vehicles = random.sample(all_vehicles, min(len(all_vehicles), random.randint(0, 1)))
            related_vehicles.extend(extra_vehicles)
        
        # Add 0-1 random locations as incident locations or nearby places
        if all_locations and random.random() < 0.25:
            extra_locations = random.sample(all_locations, min(len(all_locations), random.randint(0, 1)))
            related_locations.extend(extra_locations)
        
        # Add 0-1 random organizations as businesses involved or fronts
        if all_orgs and random.random() < 0.1:
            extra_orgs = random.sample(all_orgs, min(len(all_orgs), random.randint(0, 1)))
            related_organizations.extend(extra_orgs)
        
        # Remove duplicates while preserving order
        def deduplicate_list(lst):
            seen = set()
            result = []
            for item in lst:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        
        related_people = deduplicate_list(related_people)
        related_phones = deduplicate_list(related_phones)
        related_vehicles = deduplicate_list(related_vehicles)
        related_locations = deduplicate_list(related_locations)
        related_organizations = deduplicate_list(related_organizations)
        
        return {
            'people': related_people,
            'phones': related_phones,
            'vehicles': related_vehicles,
            'locations': related_locations,
            'organizations': related_organizations
        }
    
    def generate_narrative_content(self, doc_type, incident_type, entities, incident_timestamp, case_id=None):
        """Generate realistic narrative content for the document"""
        
        # Get entity details for narrative
        people_details = []
        for person_id in entities['people'][:3]:  # Limit to first 3 for brevity
            person = self.canonical_entities['people'].get(person_id, {})
            if person:
                name = person.get('canonical_name', 'Unknown')
                age = person.get('age', 'Unknown')
                gender = person.get('gender', 'Unknown')
                people_details.append(f"{name} (Age: {age}, Gender: {gender})")
        
        phone_details = []
        for phone_id in entities['phones'][:2]:  # Limit to first 2
            phone = self.canonical_entities['phone_numbers'].get(phone_id, {})
            if phone:
                number = phone.get('formatted_number', 'Unknown')
                phone_type = phone.get('type', 'Unknown')
                phone_details.append(f"{number} ({phone_type})")
        
        vehicle_details = []
        for vehicle_id in entities['vehicles'][:2]:  # Limit to first 2
            vehicle = self.canonical_entities['vehicles'].get(vehicle_id, {})
            if vehicle:
                reg = vehicle.get('registration_number', 'Unknown')
                model = vehicle.get('model', 'Unknown')
                vehicle_details.append(f"{reg} ({model})")
        
        location_details = []
        for location_id in entities['locations'][:2]:  # Limit to first 2
            location = self.canonical_entities['locations'].get(location_id, {})
            if location:
                address = location.get('address', 'Unknown')
                area = location.get('area', 'Unknown')
                city = location.get('city', 'Unknown')
                location_details.append(f"{address}, {area}, {city}")
        
        org_details = []
        for org_id in entities['organizations'][:2]:  # Limit to first 2
            org = self.canonical_entities['organizations'].get(org_id, {})
            if org:
                name = org.get('name', 'Unknown')
                business_type = org.get('business_type', 'Unknown')
                org_details.append(f"{name} ({business_type})")
        
        # Generate narrative based on document type
        if doc_type == 'FIR':
            return self._generate_fir_narrative(incident_type, people_details, phone_details, 
                                              vehicle_details, location_details, org_details, 
                                              incident_timestamp)
        elif doc_type == 'Police Report':
            return self._generate_police_report_narrative(incident_type, people_details, phone_details,
                                                        vehicle_details, location_details, org_details,
                                                        incident_timestamp)
        elif doc_type == 'Intelligence Note':
            return self._generate_intelligence_note_narrative(incident_type, people_details, phone_details,
                                                          vehicle_details, location_details, org_details,
                                                          incident_timestamp)
        else:  # Surveillance Report
            return self._generate_surveillance_report_narrative(incident_type, people_details, phone_details,
                                                              vehicle_details, location_details, org_details,
                                                              incident_timestamp)
    
    def _generate_fir_narrative(self, incident_type, people_details, phone_details, 
                               vehicle_details, location_details, org_details, incident_timestamp):
        """Generate FIR-style narrative"""
        
        narratives = [
            f"On {incident_timestamp.strftime('%d-%m-%Y at %H:%M hours')}, an incident of {incident_type.lower()} was reported at the police station. The complainant stated that ",
            f"At approximately {incident_timestamp.strftime('%H:%M hours on %d-%m-%Y')}, information was received regarding a {incident_type.lower()} incident. Upon investigation, it was found that ",
            f"Based on a complaint received on {incident_timestamp.strftime('%d-%m-%Y')}, a case was registered under relevant sections of IPC for {incident_type.lower()}. The facts of the case are as follows: ",
            f"On the date of {incident_timestamp.strftime('%d-%m-%Y')}, at about {incident_timestamp.strftime('%H:%M hours')}, an occurrence of {incident_type.lower()} came to the notice of police. "
        ]
        
        opening = random.choice(narratives)
        
        # Build the incident description
        if people_details:
            opening += f"involving {', '.join(people_details[:2])}"
            if len(people_details) > 2:
                opening += f" and others"
        else:
            opening += "involving unidentified persons"
        
        if location_details:
            opening += f" at or near {location_details[0]}"
        
        opening += ". "
        
        # Add details based on available information
        details = []
        
        if phone_details:
            details.append(f"Communication records indicate contact via mobile numbers {', '.join(phone_details)}")
        
        if vehicle_details:
            details.append(f"Vehicles involved/sighted include {', '.join(vehicle_details)}")
        
        if org_details:
            details.append(f"Establishments/businesses associated with the incident: {', '.join(org_details)}")
        
        # Add some investigative notes
        investigative_notes = [
            "Preliminary investigation suggests this may be part of a larger pattern of similar incidents.",
            "Forensic evidence is being collected and analyzed.",
            "Witness statements are being recorded.",
            "Surveillance footage from nearby establishments is being reviewed.",
            "Technical analysis of communication devices is underway.",
            "Financial transactions related to the incident are being traced.",
            "Inter-state coordination has been initiated for apprehension of suspects.",
            "The modus operandi appears consistent with known criminal patterns in the region."
        ]
        
        if details:
            opening += " ".join(details) + ". "
        
        opening += random.choice(investigative_notes)
        
        # Add case status and next steps
        status_notes = [
            "Case is under active investigation. Further details will be provided as investigation progresses.",
            "Investigation is ongoing. Suspects are being identified and apprehended.",
            "Case has been forwarded to the concerned department for further action.",
            "Charge sheet is being prepared based on collected evidence.",
            "Court proceedings are expected to commence soon.",
            "Interrogation of detained suspects is in progress.",
            "Property seized during investigation is being documented.",
            "Case is pending for want of certain technical evidences."
        ]
        
        opening += " " + random.choice(status_notes) + "."
        
        return opening
    
    def _generate_police_report_narrative(self, incident_type, people_details, phone_details, 
                                         vehicle_details, location_details, org_details, incident_timestamp):
        """Generate Police Report-style narrative"""
        
        narratives = [
            f"Police Report No: PR/{random.randint(1000,9999)}/{incident_timestamp.year} dated {incident_timestamp.strftime('%d-%m-%Y')}. ",
            f"Subject: Report on {incident_type.lower()} incident occurred on {incident_timestamp.strftime('%d-%m-%Y')}. ",
            f"Reference: Complaint received via PCR/Dial 100 on {incident_timestamp.strftime('%d-%m-%Y')} at {incident_timestamp.strftime('%H:%M')}. "
        ]
        
        opening = random.choice(narratives)
        
        # Incident details
        opening += f"Incident Type: {incident_type}. "
        opening += f"Date & Time: {incident_timestamp.strftime('%d-%m-%Y %H:%M:%S')}. "
        
        if location_details:
            opening += f"Location: {location_details[0]}. "
        
        # Persons involved
        if people_details:
            opening += f"Persons Involved: {', '.join(people_details)}. "
        else:
            opening += "Persons Involved: Unidentified individuals. "
        
        # Communication evidence
        if phone_details:
            opening += f"Communication Evidence: Mobile numbers {', '.join(phone_details)} were found to be active during the incident period. "
        
        # Vehicle evidence
        if vehicle_details:
            opening += f"Vehicle Evidence: {', '.join(vehicle_details)} were noticed in the vicinity of the incident. "
        
        # Establishments
        if org_details:
            opening += f"Associated Establishments: {', '.join(org_details)}. "
        
        # Investigative findings
        findings = [
            "Preliminary investigation indicates planned nature of the incident.",
            "Evidence suggests involvement of organized criminal elements.",
            "Modus operandi appears to be consistent with similar cases reported in the region.",
            "Technical surveillance indicates possible communication between suspects prior to incident.",
            "Financial trails are being examined for any suspicious transactions.",
            "Witness accounts are being corroborated with available evidence.",
            "Forensic team has been deployed to collect physical evidence.",
            "Cyber cell has been alerted for digital forensics analysis."
        ]
        
        opening += "Findings: " + random.choice(findings) + ". "
        
        # Action taken
        actions = [
            "Case has been registered and investigation initiated.",
            "Suspects have been detained for questioning.",
            "Area has been cordoned off for evidence collection.",
            "Surveillance has been increased in the surrounding area.",
            "Check posts have been established at strategic locations.",
            "Special team has been formed for investigation.",
            "Inter-state alert has been issued for suspect apprehension.",
            "Forensic samples have been sent to laboratory for analysis."
        ]
        
        opening += "Action Taken: " + random.choice(actions) + ". "
        
        # Status
        statuses = [
            "Case is under investigation. Further action will be taken based on evidence.",
            "Investigation is ongoing. Report will be submitted upon completion.",
            "Case is pending for want of certain technical inputs.",
            "Charge sheet preparation is in progress.",
            "Case has been sent to court for further proceedings.",
            "Case is sub judice. Further orders awaited.",
            "Case is under trial. Arguments are being heard.",
            "Case has been disposed of. Judgment has been pronounced."
        ]
        
        opening += "Status: " + random.choice(statuses) + "."
        
        return opening
    
    def _generate_intelligence_note_narrative(self, incident_type, people_details, phone_details, 
                                             vehicle_details, location_details, org_details, incident_timestamp):
        """Generate Intelligence Note-style narrative"""
        
        opening = f"INTELLIGENCE NOTE\nDate: {incident_timestamp.strftime('%d-%m-%Y')}\nTime: {incident_timestamp.strftime('%H:%M')}\nSubject: Information regarding {incident_type.lower()} activities\n\n"
        
        opening += "SOURCE: Technical/Human/Mixed\n"
        opening += "RELIABILITY: B-3 (Probably True/Competently Collected)\n\n"
        
        opening += "INFORMATION: "
        
        if people_details:
            opening += f"Information received indicates involvement of {', '.join(people_details[:2])}"
            if len(people_details) > 2:
                opening += f" and associates"
            opening += " in suspicious activities related to "
        else:
            opening += "Information received indicates suspicious activities related to "
        
        opening += f"{incident_type.lower()} in the area of "
        
        if location_details:
            opening += f"{location_details[0]} and surrounding regions. "
        else:
            opening += "certain urban and semi-urban areas. "
        
        opening += "DETAILS: "
        
        details = []
        
        if phone_details:
            details.append(f"Communication analysis shows frequent interaction between numbers {', '.join(phone_details)}")
        
        if vehicle_details:
            details.append(f"Movement patterns suggest use of vehicles {', '.join(vehicle_details)} for operational purposes")
        
        if org_details:
            details.append(f"Certain establishments namely {', '.join(org_details)} appear to be used as cover for illicit activities")
        
        # Intelligence-specific details
        intel_details = [
            "Chatter intercepted indicates planning of similar activities in near future.",
            "Financial transactions show unusual patterns consistent with hawala operations.",
            "Travel patterns indicate reconnaissance activities being conducted.",
            "Association with known criminals has been established through multiple sources.",
            "Modus operandi involves use of multiple SIM cards and frequent changing of vehicles.",
            "Operational security appears to be maintained through use of coded language.",
            "Funds appear to be moving through multiple layers before final destination.",
            "Local informants have reported suspicious gatherings at odd hours."
        ]
        
        if details:
            opening += " ".join(details) + ". "
        
        opening += random.choice(intel_details) + ". "
        
        # Assessment
        assessments = [
            "ASSESSMENT: Information appears credible and warrants further investigation.",
            "ASSESSMENT: Corroborative evidence is being gathered from multiple sources.",
            "ASSESSMENT: Pattern suggests possible organized criminal activity requiring sustained surveillance.",
            "ASSESSMENT: Immediate action may be required to prevent potential incidents.",
            "ASSESSMENT: Long-term monitoring recommended to establish complete network.",
            "ASSESSMENT: Cross-state linkages appear possible and need investigation.",
            "ASSESSMENT: Financial angle needs to be examined thoroughly.",
            "ASSESSMENT: Technical surveillance recommended for concrete evidence."
        ]
        
        opening += "\n\n" + random.choice(assessments) + "."
        
        # Recommendation
        recommendations = [
            "RECOMMENDATION: Keep under surveillance for next 72 hours.",
            "RECOMMENDATION: Conduct discreet inquiry to verify facts.",
            "RECOMMENDATION: Alert concerned police stations for increased vigilance.",
            "RECOMMENDATION: Consider issuing look out circular for suspects.",
            "RECOMMENDATION: Initiate financial investigation to trace money trail.",
            "RECOMMENDATION: Deploy technical team for interception and monitoring.",
            "RECOMMENDATION: Conduct raid based on developed intelligence after proper confirmation.",
            "RECOMMENDATION: Maintain status quo and continue monitoring for more inputs."
        ]
        
        opening += "\n\n" + random.choice(recommendations) + "."
        
        return opening
    
    def _generate_surveillance_report_narrative(self, incident_type, people_details, phone_details, 
                                               vehicle_details, location_details, org_details, incident_timestamp):
        """Generate Surveillance Report-style narrative"""
        
        opening = f"SURVEILLANCE DIRECTORATE REPORT\nReport No: SR/{random.randint(1000,9999)}/{incident_timestamp.year}\nDate: {incident_timestamp.strftime('%d-%m-%Y')}\nPeriod: {incident_timestamp.strftime('%H:%M')} to {(incident_timestamp + timedelta(hours=random.randint(2,8))).strftime('%H:%M')}\nSubject: Surveillance of persons/locations related to {incident_type.lower()}\n\n"
        
        opening += "OBSERVATIONS: "
        
        # Location-based observations
        if location_details:
            opening += f"Surveillance established at {location_details[0]} and surrounding areas. "
        else:
            opening += "Surveillance established at sensitive locations based on inputs. "
        
        # Person observations
        if people_details:
            opening += f"Subjects under observation: {', '.join(people_details[:2])}"
            if len(people_details) > 2:
                opening += f" and others"
            opening += ". "
        else:
            opening += "Subjects under observation: Unidentified persons of interest. "
        
        # Communication monitoring
        if phone_details:
            opening += f"Communication monitoring active on numbers {', '.join(phone_details)}. "
        else:
            opening += "Communication monitoring active on suspected numbers. "
        
        # Vehicle tracking
        if vehicle_details:
            opening += f"Vehicle tracking shows movement of {', '.join(vehicle_details)} between {random.choice(['residential and commercial areas', 'known hotspots', 'border areas', 'industrial zones'])}. "
        else:
            opening += "Vehicle tracking shows suspicious movement patterns. "
        
        # Establishment monitoring
        if org_details:
            opening += f"Monitoring of establishments {', '.join(org_details)} shows unusual activity patterns. "
        else:
            opening += "Monitoring of certain establishments shows unusual activity patterns. "
        
        # Temporal patterns
        patterns = [
            "Increased activity observed during late evening and early morning hours.",
            "Pattern of movement suggests reconnaissance activities.",
            "Regular contact observed between certain numbers at specific intervals.",
            "Movement appears to be coordinated with specific time intervals.",
            "Activity peaks observed during weekends and holidays.",
            "Decreased activity observed during day time hours.",
            "Pattern suggests use of relay points for communication and transfer.",
            "Observations indicate possible preparation for some activity."
        ]
        
        opening += "PATTERN ANALYSIS: " + random.choice(patterns) + ". "
        
        # Technical details
        technical_details = [
            "Technical surveillance equipment deployed includes audio and video recording devices.",
            "Mobile tower dump analysis shows frequent cell tower changes indicating mobility.",
            "Call detail records analysis reveals network of communication.",
            "GPS tracking shows defined routes of movement.",
            "Automatic Number Plate Recognition (ANPR) systems deployed at strategic points.",
            "Facial recognition software being used at entry/exit points.",
            "Communication interception subject to legal procedures and approvals.",
            "Data being analyzed using link analysis software for pattern detection."
        ]
        
        opening += "TECHNICAL: " + random.choice(technical_details) + ". "
        
        # Findings
        findings = [
            "No incriminating evidence found during surveillance period.",
            "Subjects appear to be aware of surveillance and changing patterns.",
            "Communication appears to be using encrypted platforms.",
            "Financial transactions observed appear to be legitimate business dealings.",
            "Movement patterns suggest possible reconnaissance for future activity.",
            "Association with known criminals cannot be ruled out based on observations.",
            "Subjects appear to be maintaining low profile to avoid detection.",
            "Surveillance needs to be continued for concrete evidence gathering."
        ]
        
        opening += "FINDINGS: " + random.choice(findings) + ". "
        
        # Recommendation
        recommendations = [
            "Continue surveillance for another 24-48 hours to gather more evidence.",
            "Consider technical interception subject to legal approvals.",
            "Increase physical surveillance in conjunction with technical monitoring.",
            "Share inputs with concerned police stations for ground verification.",
            "Consider controlled delivery if contraband movement is suspected.",
            "Prepare case for further action based on developed intelligence.",
            "Maintain surveillance and gather more corroborative evidence.",
            "Consider suspension of surveillance and revisit after interval."
        ]
        
        opening += "RECOMMENDATION: " + random.choice(recommendations) + "."
        
        return opening
    
    def generate_fir_document(self, doc_type, sequence, case_id=None):
        """Generate a single FIR/police/intelligence document"""
        
        # Select document subtype
        type_options = [t[0] for t in self.document_types]
        type_weights = [t[2] for t in self.document_types]
        selected_type = random.choices(type_options, weights=type_weights)[0]
        
        # Generate incident timestamp
        case_opening_date = None
        if case_id and case_id in self.cases:
            case_opening_date = self.cases[case_id].get('opening_date')
        
        incident_timestamp = self.generate_incident_timestamp(case_opening_date)
        
        # Select incident type
        incident_type = random.choice(self.incident_types)
        
        # Select related entities
        entities = self.select_related_entities(incident_type, case_id)
        
        # Generate document ID
        doc_id = self.generate_document_id(selected_type, sequence)
        
        # Generate narrative content
        narrative = self.generate_narrative_content(
            selected_type, incident_type, entities, incident_timestamp, case_id
        )
        
        # Create document object
        document = {
            'document_id': doc_id,
            'document_type': selected_type,
            'incident_type': incident_type,
            'timestamp': incident_timestamp.isoformat(),
            'case_id': case_id,
            'narrative_content': narrative,
            'related_entities': entities,
            'metadata': {
                'word_count': len(narrative.split()),
                'character_count': len(narrative),
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        return document
    
    def generate_fir_documents(self, count=2500, output_dir='demo_data/full_dataset/fir_reports'):
        """Generate multiple FIR/police/intelligence documents"""
        
        print(f"Generating {count} FIR/police/intelligence documents...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get case IDs for assigning some documents to cases
        case_ids = list(self.cases.keys()) if self.cases else [None]
        
        documents = []
        case_assigned_count = 0
        
        for i in range(count):
            # Assign to case occasionally (30% chance)
            case_id = random.choice(case_ids) if random.random() < 0.3 else None
            if case_id is not None:
                case_assigned_count += 1
            
            # Generate document
            doc_sequence = i + 1
            document = self.generate_fir_document(
                doc_type='FIR',  # Will be overridden inside
                sequence=doc_sequence,
                case_id=case_id
            )
            
            documents.append(document)
            
            # Progress indicator
            if (i + 1) % 200 == 0:
                print(f"  Generated {i + 1} documents...")
        
        # Save documents as JSON file (structured format)
        output_file = os.path.join(output_dir, 'fir_documents.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(documents)} FIR/police/intelligence documents")
        print(f"  {case_assigned_count} documents assigned to cases")
        print(f"  Saved to: {output_file}")
        
        # Also create individual text files for realism (smaller sample)
        self.create_individual_text_files(documents[:50], output_dir)  # First 50 as individual files
        
        return documents
    
    def create_individual_text_files(self, documents, output_dir):
        """Create individual text files for a sample of documents"""
        
        text_dir = os.path.join(output_dir, 'text_files')
        os.makedirs(text_dir, exist_ok=True)
        
        for i, doc in enumerate(documents):
            filename = f"{doc['document_id'].replace('/', '_')}.txt"
            filepath = os.path.join(text_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Document ID: {doc['document_id']}\n")
                f.write(f"Document Type: {doc['document_type']}\n")
                f.write(f"Incident Type: {doc['incident_type']}\n")
                f.write(f"Timestamp: {doc['timestamp']}\n")
                f.write(f"Case ID: {doc['case_id'] or 'N/A'}\n")
                f.write(f"Word Count: {doc['metadata']['word_count']}\n")
                f.write("-" * 50 + "\n")
                f.write(doc['narrative_content'])
                f.write("\n")
        
        print(f"  Created {len(documents)} individual text files in: {text_dir}")


def main():
    """Main function to generate FIR documents"""
    print("Starting FIR/Police/Intelligence Document Generation")
    print("=" * 60)
    
    # Initialize generator
    generator = FIRDocumentGenerator()
    
    # Generate documents
    documents = generator.generate_fir_documents(count=2500)
    
    print("\nFIR document generation completed!")
    print(f"Total documents generated: {len(documents)}")
    
    # Show sample
    if documents:
        sample = documents[0]
        print(f"\nSample Document:")
        print(f"  ID: {sample['document_id']}")
        print(f"  Type: {sample['document_type']}")
        print(f"  Incident: {sample['incident_type']}")
        print(f"  Timestamp: {sample['timestamp']}")
        print(f"  Word Count: {sample['metadata']['word_count']}")
        print(f"  Preview: {sample['narrative_content'][:100]}...")


if __name__ == "__main__":
    main()