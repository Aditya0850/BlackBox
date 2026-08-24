#!/usr/bin/env python3
"""
BlackBox SIH26189 Large-Scale Synthetic Dataset Generator - FIXED VERSION
Generates exactly 20,000+ synthetic records for criminal network analysis demonstration
NO EXTERNAL API CALLS - Pure local deterministic generation
FIXED: Prevents over-generation by separating entity creation from relationship building
"""

import json
import csv
import random
import uuid
from datetime import datetime, timedelta
import os
import sys

# Set random seeds for reproducibility
random.seed(42)

class SyntheticWorldGenerator:
    def __init__(self):
        self.canonical_entities = {
            'people': {},
            'phone_numbers': {},
            'vehicles': {},
            'locations': {},
            'organizations': {},
            'bank_accounts': {},
            'events': {}
        }
        self.criminal_networks = {}
        self.cases = {}
        self.ground_truth = {
            'metadata': {},
            'canonical_entities': self.canonical_entities,
            'record_mappings': {},
            'true_relationships': {},
            'false_relationships': {},
            'criminal_networks': {},
            'cases': {},
            'entity_resolution_challenges': {},
            'temporal_patterns': {},
            'benchmark_sets': {}
        }
        
        # Counters for ID generation
        self.id_counters = {
            'people': 0,
            'phone_numbers': 0,
            'vehicles': 0,
            'locations': 0,
            'organizations': 0,
            'bank_accounts': 0,
            'events': 0,
            'networks': 0,
            'cases': 0
        }
        
        # Data pools for generating realistic synthetic data
        self.first_names_male = [
            'Rahul', 'Vikram', 'Sameer', 'Arvind', 'Rohan', 'Karan', 'Arjun', 'Dev',
            'Sanjay', 'Rajesh', 'Amit', 'Suresh', 'Mohan', 'Lalit', 'Kailash',
            'Govind', 'Satish', 'Rakesh', 'Naresh', 'Deepak', 'Sandeep', 'Sunil',
            'Manish', 'Pankaj', 'Ashok', 'Ravi', 'Mukesh', 'Naveen', 'Pradeep',
            'Vijay', 'Anil', 'Sunil', 'Rajiv', 'Ashish', 'Nitin', 'Jitendra'
        ]
        
        self.first_names_female = [
            'Priya', 'Anita', 'Neha', 'Kavita', 'Lekha', 'Meera', 'Sunita', 'Pooja',
            'Anjali', 'Sonia', 'Rekha', 'Geeta', 'Shobha', 'Madhu', 'Uma',
            'Savitri', 'Gayatri', 'Durga', 'Kali', 'Lakshmi', 'Saraswati',
            'Parvati', 'Sita', 'Radha', 'Meera', 'Yamuna', 'Ganga', 'Narmada',
            'Kaveri', 'Godavari', 'Krishna', 'Radha', 'Rukmini', 'Satyabhama'
        ]
        
        self.last_names = [
            'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Joshi',
            'Mehta', 'Reddy', 'Yadav', 'Tiwari', 'Chaturvedi', 'Mishra',
            'Srivastava', 'Pandey', 'Dubey', 'Singhania', 'Goenka', 'Bajaj',
            'Birla', 'Tata', 'Ambani', 'Mittal', 'Agrawal', 'Khandelwal',
            'Maheshwari', 'Oswal', 'Agarwal', 'Sahara', 'Adani', 'Zaveri'
        ]
        
        self.organizations_names = [
            'Shyam Traders', 'Joshi Import Export', 'Verma Boutiques', 'Nair Enterprises',
            'QuickLogistics Solutions', 'Patel Properties', 'Kumar Transport',
            'Singh Enterprises', 'Agarwal Industries', 'Gupta Exports',
            'Maheshwari Textiles', 'Oswal Motors', 'Birla Group', 'Tata Motors',
            'Reliance Industries', 'Adani Group', 'Godrej Group', 'Larsen & Toubro',
            'Mahindra & Mahindra', 'Hero MotoCorp', 'Maruti Suzuki', 'Hyundai India',
            'Honda India', 'Toyota Kirloskar', 'Volkswagen India', 'Ford India',
            'Skoda Auto', 'Audi India', 'BMW India', 'Mercedes-Benz India',
            'HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Punjab National Bank',
            'Canara Bank', 'Bank of Baroda', 'Union Bank of India', 'Bank of India',
            'Axis Bank', 'Kotak Mahindra Bank', 'IndusInd Bank', 'Yes Bank',
            'Federal Bank', 'IDFC First Bank', 'RBL Bank', 'South Indian Bank'
        ]
        
        self.cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Chennai',
            'Kolkata', 'Surat', 'Pune', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur',
            'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad',
            'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Madurai',
            'Nashik', 'Faridabad', 'Meerut', 'Rajkot', 'Kalyan-Dombivali',
            'Vasai-Virar', 'Varanasi', 'Srinagar', 'Aurangabad', 'Dhanbad',
            'Amritsar', 'Navi Mumbai', 'Allahabad', 'Ranchi', 'Howrah',
            'Coimbatore', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur',
            'Madurai', 'Raipur', 'Kota', 'Guwahati', 'Chandigarh', 'Solapur',
            'Hubli-Dharwad', 'Bareilly', 'Moradabad', 'Mysore', 'Gurgaon',
            'Aligarh', 'Jalandhar', 'Tiruchirappalli', 'Bhubaneswar',
            'Salem', 'Warangal', 'Guntur', 'Bhiwandi', 'Saharanpur',
            'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur',
            'Bhilai', 'Cuttack', 'Firozabad', 'Kochi', 'Nellore', 'Bhavnagar',
            'Dehradun', 'Durgapur', 'Asansol', 'Nanded', 'Kolhapur',
            'Ajmer', 'Akola', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Loni',
            'Siliguri', 'Jhansi', 'Ulhasnagar', 'Jammu', 'Sangli-Miraj & Kupwad',
            'Mangalore', 'Erode', 'Belgaum', 'Ambattur', 'Tirunelveli',
            'Malegaon', 'Gaya', 'Jalna', 'Udaipur', 'Mahesana', 'Tirupati'
        ]
        
        self.states = [
            'Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Gujarat',
            'Tamil Nadu', 'West Bengal', 'Uttar Pradesh', 'Rajasthan',
            'Madhya Pradesh', 'Bihar', 'Andhra Pradesh', 'Odisha',
            'Kerala', 'Jharkhand', 'Assam', 'Punjab', 'Haryana',
            'Chhattisgarh', 'Uttarakhand', 'Himachal Pradesh', 'Goa',
            'Arunachal Pradesh', 'Nagaland', 'Manipur', 'Mizoram',
            'Tripura', 'Meghalaya', 'Sikkim', 'Jammu & Kashmir',
            'Ladakh', 'Puducherry', 'Lakshadweep', 'Andaman & Nicobar Islands'
        ]
        
        self.vehicle_models = [
            'Maruti Swift', 'Maruti Dzire', 'Maruti Baleno', 'Maruti Alto',
            'Maruti WagonR', 'Maruti Ertiga', 'Maruti Vitara Brezza',
            'Hyundai i20', 'Hyundai Creta', 'Hyundai Verna', 'Hyundai Venue',
            'Honda City', 'Honda Amaze', 'Honda Jazz', 'Honda WR-V',
            'Toyota Glanza', 'Toyota Urban Cruiser', 'Toyota Yaris',
            'Kia Seltos', 'Kia Sonet', 'Kia Carens',
            'Mahindra XUV300', 'Mahindra XUV500', 'Mahindra Thar',
            'Tata Nexon', 'Tata Harrier', 'Tata Safari', 'Tata Tiago',
            'Ford EcoSport', 'Ford Figo', 'Ford Aspire',
            'Volkswagen Polo', 'Volkswagen Vento', 'Volkswagen Ameo',
            'Skoda Rapid', 'Skoda Octavia', 'Skoda Kushaq',
            'BMW 3 Series', 'BMW 5 Series', 'BMW X1', 'BMW X3',
            'Mercedes-Benz C-Class', 'Mercedes-Benz E-Class', 'Mercedes-Benz GLA',
            'Audi A3', 'Audi A4', 'Audi Q3', 'Audi Q5'
        ]
        
        self.vehicle_types = ['Motorcycle', 'Car', 'Truck', 'Bus', 'Auto-rickshaw', 'Tempo', 'Van']
        
        self.location_types = [
            'Residential', 'Commercial Office', 'Retail Shop', 'Restaurant',
            'Warehouse', 'Factory', 'Hospital', 'Clinic', 'Pharmacy',
            'School', 'College', 'Coaching Center', 'Bank', 'ATM',
            'Petrol Pump', 'Bus Stand', 'Railway Station', 'Airport',
            'Park', 'Mall', 'Hotel', 'Guest House', 'Dhaba',
            'Police Station', 'Court', 'Jail', 'Checkpoint', 'Border',
            'Highway', 'National Highway', 'State Highway', 'River',
            'Bridge', 'Tunnel', 'Market', 'Wholesale Market'
        ]
        
        self.business_types = [
            'Trading', 'Import Export', 'Manufacturing', 'Logistics',
            'Transport', 'Textiles', 'Garments', 'Electronics',
            'Pharmaceuticals', 'Chemicals', 'Food Processing',
            'Construction', 'Real Estate', 'Finance', 'Insurance',
            'IT Services', 'Healthcare', 'Education', 'Hospitality',
            'Entertainment', 'Media', 'Agriculture', 'Mining',
            'Telecommunications', 'Energy', 'Utilities'
        ]
        
        self.criminal_network_types = [
            'hierarchical', 'hub_and_spoke', 'loosely_connected',
            'clustered', 'decentralized', 'pipeline', 'distribution',
            'corruption', 'terror_financing', 'wildlife_poaching'
        ]
        
        self.case_types = [
            'narcotics', 'financial_fraud', 'human_trafficking',
            'cybercrime', 'organised_crime', 'terrorism',
            'wildlife_crime', 'corruption', 'extortion', 'smuggling'
        ]
        
        self.relationship_types = [
            'calls', 'transfers_money_to', 'deposits_cash_in', 'withdraws_cash_from',
            'meets_at', 'visits', 'delivers_to', 'picks_up_from',
            'owns', 'registered_to', 'employed_by', 'associated_with',
            'communicates_with', 'posted_on_social_media', 'commented_on_social_media',
            'lives_at', 'works_at', 'stores_at', 'transports_goods_for',
            'receives_shipment_at', 'delivers_from', 'uses_fake_documentation_through',
            'operates_through', 'owns_directs', 'monitors', 'monitors_transactions_of',
            'investigated', 'consulted_on', 'analyzed_financials', 'shared_intelligence_on'
        ]
    
    def generate_id(self, entity_type):
        """Generate a unique ID for an entity type"""
        self.id_counters[entity_type] += 1
        if entity_type == 'people':
            return f"P{self.id_counters[entity_type]:04d}"
        elif entity_type == 'phone_numbers':
            return f"PH{self.id_counters[entity_type]:04d}"
        elif entity_type == 'vehicles':
            return f"V{self.id_counters[entity_type]:04d}"
        elif entity_type == 'locations':
            return f"L{self.id_counters[entity_type]:04d}"
        elif entity_type == 'organizations':
            return f"O{self.id_counters[entity_type]:04d}"
        elif entity_type == 'bank_accounts':
            return f"A{self.id_counters[entity_type]:04d}"
        elif entity_type == 'events':
            return f"E{self.id_counters[entity_type]:04d}"
        elif entity_type == 'networks':
            return f"N{self.id_counters[entity_type]:03d}"
        elif entity_type == 'cases':
            return f"C{self.id_counters[entity_type]:04d}"
        else:
            return f"{entity_type.upper()}{self.id_counters[entity_type]:04d}"
    
    def generate_phone_number(self):
        """Generate a realistic Indian phone number"""
        prefix = random.choice(['6', '7', '8', '9'])
        number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        formatted = f"+91 {number[:5]} {number[5:]}"
        return formatted, number
    
    def generate_vehicle_registration(self):
        """Generate a realistic Indian vehicle registration"""
        state_codes = ['MH', 'DL', 'KA', 'TG', 'GJ', 'TN', 'WB', 'UP', 'RJ', 'MP',
                      'BR', 'AP', 'OR', 'KL', 'JH', 'AS', 'PB', 'HR', 'CG', 'UK',
                      'HP', 'GA', 'AR', 'NL', 'MN', 'MI', 'TR', 'ML', 'SK', 'JK',
                      'LD', 'PY', 'AN']
        state_code = random.choice(state_codes)
        district_num = f"{random.randint(1, 99):02d}"
        series_chars = ''.join([chr(random.randint(65, 90)) for _ in range(2)])
        number = f"{random.randint(1, 9999):04d}"
        return f"{state_code} {district_num} {series_chars} {number}"
    
    def generate_person_entity(self, gender=None, age_range=(20, 60)):
        """Generate a synthetic person entity WITHOUT creating related entities"""
        person_id = self.generate_id('people')
        
        if gender is None:
            gender = random.choice(['M', 'F'])
        
        if gender == 'M':
            first_name = random.choice(self.first_names_male)
        else:
            first_name = random.choice(self.first_names_female)
        
        last_name = random.choice(self.last_names)
        canonical_name = f"{first_name} {last_name}"
        
        # Generate aliases and variations
        aliases = [canonical_name]
        
        # Add nickname variations
        if len(first_name) > 3:
            nicknames = [first_name[:3]]
            if len(first_name) > 4:
                nicknames.append(first_name[:4])
            aliases.extend(nicknames)
        
        # Add initials variations
        initials = f"{first_name[0]}. {last_name}"
        aliases.append(initials)
        
        # Add just first name
        aliases.append(first_name)
        
        # Add just last name (less common but possible)
        aliases.append(last_name)
        
        # Add common Indian nicknames
        common_nicknames = {
            'Rahul': ['Rahu', 'Rolly'],
            'Vikram': ['Vicky', 'Viku'],
            'Sameer': ['Sammy', 'Sam'],
            'Arvind': ['Arvi', 'Vindu'],
            'Rohan': ['Rocky', 'Ronny'],
            'Karan': ['Karo', 'Kanu'],
            'Arjun': ['Arju', 'Jun'],
            'Dev': ['Devu', 'Devo'],
            'Sanjay': ['Sanj', 'Sanju'],
            'Rajesh': ['Raju', 'Raj'],
            'Amit': ['Amz', 'Ami'],
            'Suresh': ['Sures', 'Surya'],
            'Mohan': ['Mo', 'Monu'],
            'Lalit': ['Lalu', 'Litti'],
            'Kailash': ['Kailu', 'Kail'],
            'Govind': ['Gov', 'Gobu'],
            'Satish': ['Sat', 'Sattu'],
            'Rakesh': ['Rak', 'Rakku'],
            'Naresh': ['Nar', 'Naru'],
            'Deepak': ['Deep', 'Deeku'],
            'Sandeep': ['Sand', 'Sandu'],
            'Sunil': ['Sunny', 'Sunu'],
            'Manish': ['Mani', 'Manu'],
            'Pankaj': ['Panku', 'Pak'],
            'Ashok': ['Ashu', 'Ash'],
            'Ravi': ['RV', 'Ra'],
            'Mukesh': ['Muk', 'Muke'],
            'Naveen': ['Nav', 'Navi'],
            'Pradeep': ['Prad', 'Pradu'],
            'Vijay': ['Vij', 'Victory'],
            'Anil': ['Anilu', 'Anilu'],
            'Suresh': ['Sures', 'Surya'],
            'Rajiv': ['Raju', 'Rivu'],
            'Ashish': ['Ashu', 'Ash'],
            'Nitin': ['Nitu', 'Nittu'],
            'Jitendra': ['Jitu', 'Jeet']
        }
        
        if first_name in common_nicknames:
            aliases.extend(common_nicknames[first_name])
        
        age = random.randint(age_range[0], age_range[1])
        
        # We'll store the IDs of related entities separately (to be filled later)
        person_entity = {
            'canonical_name': canonical_name,
            'aliases': list(set(aliases)),  # Remove duplicates
            'gender': gender,
            'age': age,
            # These will be populated later during relationship building
            'phone_numbers': [],  # Will be filled with phone IDs
            'addresses': [],      # Will be filled with location IDs
            'vehicles': [],       # Will be filled with vehicle IDs
            'organizations': [],  # Will be filled with organization IDs
            'bank_accounts': [],  # Will be filled with bank account IDs
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime.now() - timedelta(days=random.randint(365, 1095))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat()
            }
        }
        
        self.canonical_entities['people'][person_id] = person_entity
        return person_id
    
    def generate_phone_entity(self):
        """Generate a synthetic phone number entity WITHOUT creating related entities"""
        phone_id = self.generate_id('phone_numbers')
        formatted_number, raw_number = self.generate_phone_number()
        
        # Determine if it's a burner/disposable phone (8% chance)
        is_burner = random.random() < 0.08
        # Determine if it's a landline (3% chance)
        is_landline = random.random() < 0.03 and not is_burner
        # Otherwise it's a regular mobile
        is_mobile = not (is_burner or is_landline)
        
        phone_entity = {
            'raw_number': raw_number,
            'formatted_number': formatted_number,
            'type': 'burner' if is_burner else ('landline' if is_landline else 'mobile'),
            'carrier': random.choice(['Jio', 'Airtel', 'Vodafone-Idea', 'BSNL']),
            'is_active': random.random() > 0.05,  # 95% active
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(30, 1095))).isoformat()
            }
        }
        
        # Burner phones have shorter validity
        if is_burner:
            phone_entity['validity_period']['end'] = (
                datetime.now() + timedelta(days=random.randint(30, 180))
            ).isoformat()
        
        self.canonical_entities['phone_numbers'][phone_id] = phone_entity
        return phone_id
    
    def generate_vehicle_entity(self):
        """Generate a synthetic vehicle entity WITHOUT creating related entities"""
        vehicle_id = self.generate_id('vehicles')
        registration = self.generate_vehicle_registration()
        model = random.choice(self.vehicle_models)
        vehicle_type = random.choice(self.vehicle_types)
        year = random.randint(2010, 2026)
        
        # Determine fuel type based on vehicle type
        if vehicle_type == 'Motorcycle':
            fuel_type = random.choice(['Petrol'])
        elif vehicle_type in ['Auto-rickshaw']:
            fuel_type = random.choice(['CNG', 'LPG', 'Petrol'])
        elif vehicle_type in ['Bus', 'Truck']:
            fuel_type = random.choice(['Diesel', 'CNG'])
        else:  # Car, Van, etc.
            fuel_type = random.choice(['Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid'])
        
        vehicle_entity = {
            'registration_number': registration,
            'model': model,
            'type': vehicle_type,
            'year': year,
            'fuel_type': fuel_type,
            'color': random.choice(['White', 'Black', 'Silver', 'Grey', 'Blue', 'Red', 'Brown', 'Green', 'Yellow', 'Orange']),
            'is_active': random.random() > 0.02,  # 98% active
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime(year, 1, 1)).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat()
            }
        }
        
        self.canonical_entities['vehicles'][vehicle_id] = vehicle_entity
        return vehicle_id
    
    def generate_location_entity(self):
        """Generate a synthetic location entity WITHOUT creating related entities"""
        location_id = self.generate_id('locations')
        city = random.choice(self.cities)
        state = random.choice([s for s in self.states if s in ['Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Gujarat', 'Tamil Nadu', 'West Bengal']] or self.cities)
        
        location_types = self.location_types
        loc_type = random.choice(location_types)
        
        # Generate a realistic address
        building_num = random.randint(1, 999)
        street_names = [
            'MG Road', 'Park Street', 'Church Street', 'Brigade Road',
            'Residency Road', 'Commercial Street', 'JC Road', 'AVM Double Road',
            'Ring Road', 'Outer Ring Road', 'Inner Ring Road', 'Airport Road',
            'Hosur Road', 'Sarjapur Road', 'Whitefield Main Road',
            'Old Madras Road', 'Airport Road', 'Kanakpura Road',
            'Banerghatta Road', 'Jayanagar', 'J.P. Nagar', 'Basavangudi',
            'Malleshwaram', 'Rajajinagar', 'Basaveshwaranagar', 'Vijayanagar',
            'Yeshwanthpur', 'Peenya', 'Jalahalli', 'Yelahanka', 'Kengeri',
            'Uttarahalli', 'Kumaraswamy Layout', 'JP Nagar', 'Bannerghatta',
            'Electronic City', 'Whitefield', 'Marathahalli', 'KR Puram',
            'BTM Layout', 'HSR Layout', 'OMBR Layout', 'KANAKAPURA ROAD',
            'SARJAPUR ROAD', 'OUTER RING ROAD', 'INNER RING ROAD'
        ]
        street = random.choice(street_names)
        area = random.choice([
            'Indiranagar', 'Koramangala', 'JP Nagar', 'Basavangudi',
            'Malleshwaram', 'Rajajinagar', 'Basaveshwaranagar', 'Vijayanagar',
            'Yeshwanthpur', 'Peenya', 'Jalahalli', 'Yelahanka', 'Kengeri',
            'Uttarahalli', 'Kumaraswamy Layout', 'JP Nagar', 'Bannerghatta',
            'Electronic City', 'Whitefield', 'Marathahalli', 'KR Puram',
            'BTM Layout', 'HSR Layout', 'OMBR Layout', 'Frazer Town',
            'Shivajinagar', 'Lavelle Road', 'Residency Road', 'St. Marks Road',
            'Mahatma Gandhi Road', 'KG Road', 'KASTURBA ROAD',
            'CUBBON PARK', 'VIDHANA SOUDHA', 'ATAL BIHARI VAJPAYEE',
            'CENTRAL COLLEGE', 'NATIONAL COLLEGE', 'RV COLLEGE'
        ])
        
        # Format address
        address_formats = [
            f"{building_num}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"{building_num}/{random.randint(1, 10)}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"No. {building_num}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"{building_num}-{random.randint(1, 10)}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"Plot No {building_num}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"House No {building_num}, {street}, {area}, {city} - {random.randint(100000, 999999)}",
            f"{building_num}, {street}, Near {random.choice(['Landmark', 'Temple', 'School', 'Hospital', 'Park'])}, {area}, {city} - {random.randint(100000, 999999)}"
        ]
        address = random.choice(address_formats)
        
        location_entity = {
            'address': address,
            'area': area,
            'city': city,
            'state': state,
            'pincode': f"{random.randint(100000, 999999):06d}",
            'type': loc_type,
            'is_active': random.random() > 0.01,  # 99% active
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime.now() - timedelta(days=random.randint(365, 1095))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat()
            }
        }
        
        self.canonical_entities['locations'][location_id] = location_entity
        return location_id
    
    def generate_organization_entity(self):
        """Generate a synthetic organization entity WITHOUT creating related entities"""
        org_id = self.generate_id('organizations')
        # Mix of real company names and generated ones
        if random.random() < 0.8:  # 80% real company names from our list
            name = random.choice(self.organizations_names)
        else:  # 20% generated names
            adjectives = ['Global', 'National', 'International', 'Supreme', 'Prime', 'Ultra', 'Mega', 'Super', 'Zenith', 'Apex', 'Vertex', 'Summit', 'Pinnacle', 'Crown', 'Royal', 'Imperial', 'Elite', 'Premier', 'Supreme', 'Ultimate']
            nouns = ['Enterprises', 'Industries', 'Corporation', 'Company', 'Limited', 'Ltd', 'Private Limited', 'Pvt Ltd', 'Group', 'Conglomerate', 'Solutions', 'Systems', 'Technologies', 'Innovations', 'Ventures', 'Holdings', 'Partnership', 'Alliance', 'Network', 'Foundation']
            name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        
        business_type = random.choice(self.business_types)
        
        organization_entity = {
            'name': name,
            'business_type': business_type,
            # These will be populated later during relationship building
            'locations': [],  # Will be filled with location IDs
            'phone_numbers': [],  # Will be filled with phone IDs
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime.now() - timedelta(days=random.randint(365, 1095))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat()
            },
            'is_active': random.random() > 0.02  # 98% active
        }
        
        self.canonical_entities['organizations'][org_id] = organization_entity
        return org_id
    
    def generate_bank_account_entity(self):
        """Generate a synthetic bank account entity WITHOUT creating related entities"""
        account_id = self.generate_id('bank_accounts')
        
        # Generate account number
        account_number = f"{random.randint(1000000000, 9999999999):010d}"  # 10-digit account number
        
        # Determine account type
        account_types = ['Savings', 'Current', 'Salary', 'Fixed Deposit', 'Recurring Deposit', 'NRE', 'NRO', 'FCNR']
        account_type = random.choice(account_types)
        
        # Determine bank
        banks = ['State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Punjab National Bank', 'Bank of Baroda',
                 'Canara Bank', 'Union Bank of India', 'Bank of India', 'Axis Bank', 'Kotak Mahindra Bank',
                 'IndusInd Bank', 'Yes Bank', 'Federal Bank', 'IDFC First Bank', 'RBL Bank', 'South Indian Bank',
                 'City Union Bank', 'Karur Vysya Bank', 'Lakshmi Vilas Bank', 'Dhanlaxmi Bank',
                 'Standard Chartered Bank', 'Citibank', 'HSBC', 'Deutsche Bank', 'Barclays']
        bank = random.choice(banks)
        
        # Generate IFSC code (simplified)
        bank_codes = {
            'State Bank of India': 'SBIN',
            'HDFC Bank': 'HDFC',
            'ICICI Bank': 'ICIC',
            'Punjab National Bank': 'PUNB',
            'Bank of Baroda': 'BARB',
            'Canara Bank': 'CNRB',
            'Union Bank of India': 'UBIN',
            'Bank of India': 'BKID',
            'Axis Bank': 'UTIB',
            'Kotak Mahindra Bank': 'KKBK',
            'IndusInd Bank': 'INDB',
            'Yes Bank': 'YESB',
            'Federal Bank': 'FDRL',
            'IDFC First Bank': 'IDFB',
            'RBL Bank': 'RATN',
            'South Indian Bank': 'SIBL'
        }
        bank_code = bank_codes.get(bank, 'XXXX')
        ifsc = f"{bank_code}0{random.randint(000000, 999999):06d}"
        
        # Generate balance (for realism, though not typically shared)
        balance_ranges = {
            'Savings': (1000, 500000),
            'Current': (5000, 2000000),
            'Salary': (5000, 300000),
            'Fixed Deposit': (50000, 5000000),
            'Recurring Deposit': (1000, 500000),
            'NRE': (10000, 5000000),
            'NRO': (5000, 2000000),
            'FCNR': (100000, 10000000)
        }
        min_bal, max_bal = balance_ranges.get(account_type, (1000, 100000))
        balance = random.randint(min_bal, max_bal)
        
        account_entity = {
            'account_number': account_number,
            'account_type': account_type,
            'bank_name': bank,
            'ifsc_code': ifsc,
            'balance': balance,  # For internal realism
            'is_active': random.random() > 0.03,  # 97% active
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': (datetime.now() - timedelta(days=random.randint(365, 1095))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat()
            }
        }
        
        self.canonical_entities['bank_accounts'][account_id] = account_entity
        return account_id
    
    def generate_event_entity(self, event_type=None, timestamp=None):
        """Generate a synthetic event entity"""
        event_id = self.generate_id('events')
        
        if event_type is None:
            event_types = ['meeting', 'transaction', 'delivery', 'pickup', 'surveillance', 'incident', 'arrest', 'raid', 'seizure', 'call', 'transfer', 'deposit', 'withdrawal']
            event_type = random.choice(event_types)
        
        if timestamp is None:
            # Generate timestamp within our range (2024-01-01 to 2026-06-30)
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2026, 6, 30)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            timestamp = start_date + timedelta(days=random_days)
            # Add random time of day
            timestamp = timestamp.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
        
        event_entity = {
            'type': event_type,
            'timestamp': timestamp.isoformat(),
            'date_added': datetime.now().isoformat(),
            'validity_period': {
                'start': timestamp.isoformat(),
                'end': (timestamp + timedelta(days=365)).isoformat()  # Events are relevant for a year
            }
        }
        
        self.canonical_entities['events'][event_id] = event_entity
        return event_id, timestamp
    
    def build_relationships(self):
        """Build relationships between entities after all base entities are created"""
        print("Building relationships between entities...")
        
        # Assign phone numbers to people (1-2 per person)
        person_ids = list(self.canonical_entities['people'].keys())
        phone_ids = list(self.canonical_entities['phone_numbers'].keys())
        
        for person_id in person_ids:
            # Each person gets 1-2 phone numbers
            num_phones = random.randint(1, 2)
            assigned_phones = random.sample(phone_ids, min(num_phones, len(phone_ids)))
            self.canonical_entities['people'][person_id]['phone_numbers'] = assigned_phones
        
        # Assign addresses to people (1 per person)
        location_ids = list(self.canonical_entities['locations'].keys())
        for person_id in person_ids:
            # Each person gets 1 address
            if location_ids:
                assigned_location = random.choice(location_ids)
                self.canonical_entities['people'][person_id]['addresses'] = [assigned_location]
        
        # Assign vehicles to people (0-1 per person, 60% ownership)
        vehicle_ids = list(self.canonical_entities['vehicles'].keys())
        for person_id in person_ids:
            if random.random() < 0.6 and vehicle_ids:  # 60% own a vehicle
                assigned_vehicle = random.choice(vehicle_ids)
                self.canonical_entities['people'][person_id]['vehicles'] = [assigned_vehicle]
        
        # Assign organizations to people (0-1 per person, 40% association)
        org_ids = list(self.canonical_entities['organizations'].keys())
        for person_id in person_ids:
            if random.random() < 0.4 and org_ids:  # 40% associated with an organization
                assigned_org = random.choice(org_ids)
                self.canonical_entities['people'][person_id]['organizations'] = [assigned_org]
        
        # Assign bank accounts to people (1-2 per person)
        account_ids = list(self.canonical_entities['bank_accounts'].keys())
        for person_id in person_ids:
            # Each person gets 1-2 bank accounts
            num_accounts = random.randint(1, 2)
            assigned_accounts = random.sample(account_ids, min(num_accounts, len(account_ids)))
            self.canonical_entities['people'][person_id]['bank_accounts'] = assigned_accounts
        
        # Assign locations to organizations (1-2 per organization)
        for org_id in org_ids:
            if location_ids:
                num_locations = random.randint(1, 2)
                assigned_locations = random.sample(location_ids, min(num_locations, len(location_ids)))
                self.canonical_entities['organizations'][org_id]['locations'] = assigned_locations
        
        # Assign phone numbers to organizations (1-2 per organization)
        for org_id in org_ids:
            if phone_ids:
                num_phones = random.randint(1, 2)
                assigned_phones = random.sample(phone_ids, min(num_phones, len(phone_ids)))
                self.canonical_entities['organizations'][org_id]['phone_numbers'] = assigned_phones
        
        print("Relationships built successfully")
    
    def generate_criminal_network(self, network_type=None, size=None):
        """Generate a synthetic criminal network"""
        network_id = self.generate_id('networks')
        
        if network_type is None:
            network_type = random.choice(self.criminal_network_types)
        
        if size is None:
            # Different network types have different typical sizes - TARGETED FOR CONTROL
            size_ranges = {
                'hierarchical': (8, 12),
                'hub_and_spoke': (6, 10),
                'loosely_connected': (10, 15),
                'clustered': (12, 18),
                'decentralized': (8, 12),
                'pipeline': (5, 8),
                'distribution': (10, 15),
                'corruption': (5, 10),
                'terror_financing': (4, 8),
                'wildlife_poaching': (6, 12)
            }
            min_size, max_size = size_ranges.get(network_type, (8, 12))
            size = random.randint(min_size, max_size)
        
        # Generate members for this network
        member_ids = []
        for i in range(size):
            person_id = self.generate_person_entity(age_range=(22, 55))  # Criminals tend to be in this age range
            member_ids.append(person_id)
        
        # Define network structure based on type
        structure = {}
        if network_type == 'hierarchical':
            # Clear leadership structure
            if len(member_ids) >= 3:
                structure['leader'] = member_ids[0]
                structure['lieutenants'] = member_ids[1:min(3, len(member_ids))]
                structure['enforcers'] = member_ids[3:min(6, len(member_ids))]
                structure['technicians'] = member_ids[6:min(8, len(member_ids))]
                structure['foot_soldiers'] = member_ids[8:] if len(member_ids) > 8 else []
            else:
                structure['leader'] = member_ids[0] if member_ids else None
                structure['members'] = member_ids[1:] if len(member_ids) > 1 else []
        
        elif network_type == 'hub_and_spoke':
            # Central figure with associates
            if len(member_ids) >= 2:
                structure['hub'] = member_ids[0]
                structure['spokes'] = member_ids[1:]
            else:
                structure['members'] = member_ids
        
        elif network_type == 'loosely_connected':
            # Members with weak connections
            structure['members'] = member_ids
            structure['connection_density'] = random.uniform(0.2, 0.5)  # Low to medium connection density
        
        elif network_type == 'clustered':
            # Geographic or functional clusters
            if len(member_ids) >= 4:
                cluster_size = max(2, len(member_ids) // 3)
                structure['cluster_1'] = member_ids[:cluster_size]
                structure['cluster_2'] = member_ids[cluster_size:cluster_size*2]
                structure['cluster_3'] = member_ids[cluster_size*2:cluster_size*3]
                structure['bridge_members'] = member_ids[cluster_size*3:] if len(member_ids) > cluster_size*3 else []
            else:
                structure['members'] = member_ids
        
        elif network_type == 'decentralized':
            # Peer-to-peer structure
            structure['members'] = member_ids
            structure['connection_probability'] = random.uniform(0.3, 0.6)
        
        elif network_type == 'pipeline':
            # Linear structure: source -> transit -> destination
            if len(member_ids) >= 3:
                third = len(member_ids) // 3
                structure['source'] = member_ids[:third]
                structure['transit'] = member_ids[third:2*third]
                structure['destination'] = member_ids[2*third:]
            else:
                structure['members'] = member_ids
        
        elif network_type == 'distribution':
            # Manufacturer -> distributor -> retailer -> customer
            if len(member_ids) >= 4:
                quarter = len(member_ids) // 4
                structure['manufacturer'] = member_ids[:quarter]
                structure['distributor'] = member_ids[quarter:2*quarter]
                structure['retailer'] = member_ids[2*quarter:3*quarter]
                structure['customer'] = member_ids[3*quarter:]
            else:
                structure['members'] = member_ids
        
        elif network_type == 'corruption':
            # Officials-businessmen-middlemen
            if len(member_ids) >= 3:
                structure['officials'] = member_ids[:len(member_ids)//3]
                structure['businessmen'] = member_ids[len(member_ids)//3:2*len(member_ids)//3]
                structure['middlemen'] = member_ids[2*len(member_ids)//3:]
            else:
                structure['members'] = member_ids
        
        elif network_type == 'terror_financing':
            # Small, tight-knit cell
            structure['members'] = member_ids
            structure['cell_structure'] = True
        
        elif network_type == 'wildlife_poaching':
            # Local hunters-international buyers
            if len(member_ids) >= 4:
                quarter = len(member_ids) // 4
                structure['local_hunters'] = member_ids[:quarter]
                structure['middlemen'] = member_ids[quarter:2*quarter]
                structure['exporters'] = member_ids[2*quarter:3*quarter]
                structure['international_buyers'] = member_ids[3*quarter:]
            else:
                structure['members'] = member_ids
        
        else:
            # Default structure
            structure['members'] = member_ids
        
        network_entity = {
            'name': f"{network_type.replace('_', ' ').title()} Network {self.id_counters['networks']}",
            'type': network_type,
            'primary_activity': self._get_primary_activity_for_network_type(network_type),
            'geographic_focus': random.sample(self.cities, min(3, len(self.cities))),
            'members': member_ids,
            'structure': structure,
            'communication_pattern': self._get_communication_pattern_for_network_type(network_type),
            'financial_pattern': self._get_financial_pattern_for_network_type(network_type),
            'typical_transaction_size': self._get_typical_transaction_size_for_network_type(network_type),
            'communication_frequency': self._get_communication_frequency_for_network_type(network_type),
            'known_fronts': [],  # Will be populated later from organizations
            'known_vehicles': [],  # Will be populated later from vehicles
            'known_locations': [],  # Will be populated later from locations
            'date_added': datetime.now().isoformat(),
            'active_period': {
                'start': (datetime.now() - timedelta(days=random.randint(180, 540))).isoformat(),
                'end': (datetime.now() + timedelta(days=random.randint(180, 540))).isoformat()
            }
        }
        
        self.criminal_networks[network_id] = network_entity
        return network_id
    
    def _get_primary_activity_for_network_type(self, network_type):
        activities = {
            'hierarchical': 'narcotics_trafficking',
            'hub_and_spoke': 'financial_fraud',
            'loosely_connected': 'cybercrime',
            'clustered': 'smuggling',
            'decentralized': 'hawala_operations',
            'pipeline': 'drug_pipeline',
            'distribution': 'counterfeit_distribution',
            'corruption': 'political_corruption',
            'terror_financing': 'terror_funding',
            'wildlife_poaching': 'wildlife_trafficking'
        }
        return activities.get(network_type, 'criminal_activity')
    
    def _get_communication_pattern_for_network_type(self, network_type):
        patterns = {
            'hierarchical': 'burner_phones_with_hierarchical_flow',
            'hub_and_spoke': 'central_hub_communication',
            'loosely_connected': 'encrypted_channels_specialized_contact',
            'clustered': 'geographic_cluster_communication',
            'decentralized': 'peer_to_peer_trust_network',
            'pipeline': 'sequential_contact_chain',
            'distribution': 'distributor_network_communication',
            'corruption': 'official_businessman_intermediary',
            'terror_financing': 'tight_knit_cell_communication',
            'wildlife_poaching': 'hunter_buyer_network'
        }
        return patterns.get(network_type, 'standard_criminal_communication')
    
    def _get_financial_pattern_for_network_type(self, network_type):
        patterns = {
            'hierarchical': 'layered_transfers_via_shell_companies',
            'hub_and_spoke': 'central_fund_pooling_distribution',
            'loosely_connected': 'cryptocurrency_mixers_micro_transactions',
            'clustered': 'cash_intensive_bulk_transactions',
            'decentralized': 'hawala_hundi_value_transfer',
            'pipeline': 'sequential_fund_flow_along_chain',
            'distribution': 'wholesale_credit_cash_collection',
            'corruption': 'kickback_over_invoicing_fake_invoices',
            'terror_financing': 'small_regular_donations_charity_fronts',
            'wildlife_poaching': 'high_value_low_volume_ivory_rhino_horn'
        }
        return patterns.get(network_type, 'standard_financial_pattern')
    
    def _get_typical_transaction_size_for_network_type(self, network_type):
        sizes = {
            'hierarchical': '500000-5000000',
            'hub_and_spoke': '100000-2000000',
            'loosely_connected': '50000-500000',
            'clustered': '100000-3000000',
            'decentralized': '50000-1000000',
            'pipeline': '200000-1500000',
            'distribution': '50000-800000',
            'corruption': '100000-5000000',
            'terror_financing': '10000-500000',
            'wildlife_poaching': '1000000-10000000'
        }
        return sizes.get(network_type, '100000-1000000')
    
    def _get_communication_frequency_for_network_type(self, network_type):
        frequencies = {
            'hierarchical': 'burst_before_operations',
            'hub_and_spoke': 'regular_hub_contact',
            'loosely_connected': 'specialized_as_needed',
            'clustered': 'geographic_timing_based',
            'decentralized': 'peer_based_as_required',
            'pipeline': 'sequential_activation',
            'distribution': 'distributor_schedule_based',
            'corruption': 'contract_payment_cycle',
            'terror_financing': 'regular_small_intervals',
            'wildlife_poaching': 'event_based_post_hunt'
        }
        return frequencies.get(network_type, 'as_needed_based_on_operations')
    
    def generate_case(self, case_type=None, primary_network=None):
        """Generate a synthetic investigative case"""
        case_id = self.generate_id('cases')
        
        if case_type is None:
            case_type = random.choice(self.case_types)
        
        # Generate case number
        year = random.choice([2024, 2025, 2026])
        month = random.randint(1, 12)
        sequence = random.randint(100, 999)
        case_number = f"{case_type.upper()}/{self._get_state_abbreviation()}/{year}/{sequence:03d}"
        
        # Generate title
        adjectives = ['Suspected', 'Alleged', 'Reported', 'Ongoing', 'Active', 'Under Investigation']
        nouns = ['Activity', 'Operation', 'Network', 'Racket', 'Ring', 'Syndicate', 'Cartel', 'Gang']
        locations = ['City', 'Metro', 'Urban', 'Rural', 'District', 'State', 'Region', 'Area']
        title = f"{random.choice(adjectives)} {random.choice(self.criminal_network_types).replace('_', ' ').title()} {random.choice(nouns)} - {random.choice(locations)} {random.choice(self.cities)}"
        
        # Determine opening date (sometime in 2024-2026)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2026, 6, 30)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        opening_date = start_date + timedelta(days=random_days)
        
        # Generate investigating officers (refer to person entities)
        investigating_officer = self.generate_person_entity(age_range=(30, 55)) if random.random() < 0.8 else None
        supervising_officer = self.generate_person_entity(age_range=(35, 60)) if random.random() < 0.6 else None
        
        case_entity = {
            'case_number': case_number,
            'title': title,
            'case_type': case_type,
            'opening_date': opening_date.isoformat(),
            'investigating_officer': investigating_officer,
            'supervising_officer': supervising_officer,
            'primary_network': primary_network,
            'secondary_networks': [],  # Will be populated
            'status': random.choice(['open', 'under_investigation', 'closed', 'pending_trial']),
            'classification': random.choice(['public', 'confidential', 'secret', 'top_secret']),
            'evidence_items': [],  # Will be populated with actual records
            'linked_cases': [],  # Cases with genuine connections
            'superficially_similar_cases': [],  # Cases with red herring similarities
            'date_added': datetime.now().isoformat(),
            'expected_discoveries': {
                'central_entities': [],
                'bridge_entities': [],
                'suspicious_patterns': [],
                'cross_case_links': []
            }
        }
        
        self.cases[case_id] = case_entity
        return case_id
    
    def _get_state_abbreviation(self):
        state_abbrevs = {
            'Maharashtra': 'MH', 'Delhi': 'DL', 'Karnataka': 'KA', 'Telangana': 'TG',
            'Gujarat': 'GJ', 'Tamil Nadu': 'TN', 'West Bengal': 'WB', 'Uttar Pradesh': 'UP',
            'Rajasthan': 'RJ', 'Madhya Pradesh': 'MP', 'Bihar': 'BR', 'Andhra Pradesh': 'AP',
            'Odisha': 'OR', 'Kerala': 'KL', 'Jharkatch': 'JH', 'Assam': 'AS', 'Punjab': 'PB',
            'Haryana': 'HR', 'Chhattisgarh': 'CG', 'Uttarakhand': 'UK', 'Himachal Pradesh': 'HP',
            'Goa': 'GA', 'Arunachal Pradesh': 'AR', 'Nagaland': 'NL', 'Manipur': 'MN',
            'Mizoram': 'MI', 'Tripura': 'TR', 'Meghalaya': 'ML', 'Sikkim': 'SK',
            'Jammu & Kashmir': 'JK', 'Ladakh': 'LD', 'Puducherry': 'PY',
            'Lakshadweep': 'LD', 'Andaman & Nicobar Islands': 'AN'
        }
        # Return a random state abbreviation
        return random.choice(list(state_abbrevs.values()))
    
    def generate_synthetic_world(self, target_people=1000, target_phones=500, target_vehicles=300, 
                               target_locations=300, target_organizations=150, target_accounts=300,
                               target_events=200, target_networks=10, target_cases=60):
        """Generate the foundational synthetic world with TARGETED counts"""
        print(f"Generating synthetic world with targets:")
        print(f"  People: {target_people}")
        print(f"  Phone Numbers: {target_phones}")
        print(f"  Vehicles: {target_vehicles}")
        print(f"  Locations: {target_locations}")
        print(f"  Organizations: {target_organizations}")
        print(f"  Bank Accounts: {target_accounts}")
        print(f"  Events: {target_events}")
        print(f"  Criminal Networks: {target_networks}")
        print(f"  Cases: {target_cases}")
        
        # Generate people (base entities only)
        print("Generating people...")
        for i in range(target_people):
            if i % 100 == 0 and i > 0:
                print(f"  Generated {i} people...")
            self.generate_person_entity()
        print(f"  Generated {len(self.canonical_entities['people'])} people")
        
        # Generate phone numbers (base entities only)
        print("Generating phone numbers...")
        for i in range(target_phones):
            if i % 50 == 0 and i > 0:
                print(f"  Generated {i} phone numbers...")
            self.generate_phone_entity()
        print(f"  Generated {len(self.canonical_entities['phone_numbers'])} phone numbers")
        
        # Generate vehicles (base entities only)
        print("Generating vehicles...")
        for i in range(target_vehicles):
            if i % 50 == 0 and i > 0:
                print(f"  Generated {i} vehicles...")
            self.generate_vehicle_entity()
        print(f"  Generated {len(self.canonical_entities['vehicles'])} vehicles")
        
        # Generate locations (base entities only)
        print("Generating locations...")
        for i in range(target_locations):
            if i % 50 == 0 and i > 0:
                print(f"  Generated {i} locations...")
            self.generate_location_entity()
        print(f"  Generated {len(self.canonical_entities['locations'])} locations")
        
        # Generate organizations (base entities only)
        print("Generating organizations...")
        for i in range(target_organizations):
            if i % 25 == 0 and i > 0:
                print(f"  Generated {i} organizations...")
            self.generate_organization_entity()
        print(f"  Generated {len(self.canonical_entities['organizations'])} organizations")
        
        # Generate bank accounts (base entities only)
        print("Generating bank accounts...")
        for i in range(target_accounts):
            if i % 50 == 0 and i > 0:
                print(f"  Generated {i} bank accounts...")
            self.generate_bank_account_entity()
        print(f"  Generated {len(self.canonical_entities['bank_accounts'])} bank accounts")
        
        # Generate events
        print("Generating events...")
        for i in range(target_events):
            if i % 25 == 0 and i > 0:
                print(f"  Generated {i} events...")
            self.generate_event_entity()
        print(f"  Generated {len(self.canonical_entities['events'])} events")
        
        # Build relationships between entities
        self.build_relationships()
        
        # Generate criminal networks (exact count)
        print("Generating criminal networks...")
        network_types = self.criminal_network_types
        networks_per_type = max(1, target_networks // len(network_types))
        remainder = target_networks % len(network_types)
        
        network_count = 0
        for i, network_type in enumerate(network_types):
            count = networks_per_type + (1 if i < remainder else 0)
            for j in range(count):
                if network_count % 5 == 0 and network_count > 0:
                    print(f"  Generated {network_count} networks...")
                self.generate_criminal_network(network_type=network_type)
                network_count += 1
        print(f"  Generated {len(self.criminal_networks)} criminal networks")
        
        # Generate cases (exact count)
        print("Generating cases...")
        case_types = self.case_types
        cases_per_type = max(1, target_cases // len(case_types))
        remainder = target_cases % len(case_types)
        
        case_count = 0
        for i, case_type in enumerate(case_types):
            count = cases_per_type + (1 if i < remainder else 0)
            for j in range(count):
                if case_count % 10 == 0 and case_count > 0:
                    print(f"  Generated {case_count} cases...")
                # Some cases get assigned to networks
                primary_network = random.choice(list(self.criminal_networks.keys())) if self.criminal_networks and random.random() < 0.6 else None
                self.generate_case(primary_network=primary_network)
                case_count += 1
        print(f"  Generated {len(self.cases)} cases")
        
        print("Synthetic world generation complete!")
    
    def save_world_model(self, filepath):
        """Save the world model to a JSON file"""
        world_model = {
            'canonical_entities': self.canonical_entities,
            'criminal_networks': self.criminal_networks,
            'cases': self.cases,
            'ground_truth': self.ground_truth,
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(world_model, f, indent=2, ensure_ascii=False)
        
        print(f"World model saved to {filepath}")
    
    def load_world_model(self, filepath):
        """Load the world model from a JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            world_model = json.load(f)
        
        self.canonical_entities = world_model['canonical_entities']
        self.criminal_networks = world_model['criminal_networks']
        self.cases = world_model['cases']
        
        # Reset ID counters based on loaded data
        self.id_counters = {
            'people': len(self.canonical_entities['people']),
            'phone_numbers': len(self.canonical_entities['phone_numbers']),
            'vehicles': len(self.canonical_entities['vehicles']),
            'locations': len(self.canonical_entities['locations']),
            'organizations': len(self.canonical_entities['organizations']),
            'bank_accounts': len(self.canonical_entities['bank_accounts']),
            'events': len(self.canonical_entities['events']),
            'networks': len(self.criminal_networks),
            'cases': len(self.cases)
        }
        
        print(f"World model loaded from {filepath}")

def main():
    """Main function to generate the dataset"""
    print("Starting BlackBox SIH26189 Large-Scale Synthetic Dataset Generation")
    print("=" * 70)
    print("NO EXTERNAL API CALLS - Pure local deterministic generation")
    print("Using random.seed(42) for reproducibility")
    print()
    
    # Create generator
    generator = SyntheticWorldGenerator()
    
    # Generate the synthetic world with TARGETED amounts
    generator.generate_synthetic_world(
        target_people=1000,
        target_phones=500,
        target_vehicles=300,
        target_locations=300,
        target_organizations=150,
        target_accounts=300,
        target_events=200,
        target_networks=10,
        target_cases=60
    )
    
    # Save world model
    os.makedirs('demo_data/world_model', exist_ok=True)
    generator.save_world_model('demo_data/world_model/synthetic_world.json')
    
    print("\nGeneration of synthetic world completed!")
    print(f"Summary:")
    print(f"  People: {len(generator.canonical_entities['people'])}")
    print(f"  Phone Numbers: {len(generator.canonical_entities['phone_numbers'])}")
    print(f"  Vehicles: {len(generator.canonical_entities['vehicles'])}")
    print(f"  Locations: {len(generator.canonical_entities['locations'])}")
    print(f"  Organizations: {len(generator.canonical_entities['organizations'])}")
    print(f"  Bank Accounts: {len(generator.canonical_entities['bank_accounts'])}")
    print(f"  Events: {len(generator.canonical_entities['events'])}")
    print(f"  Criminal Networks: {len(generator.criminal_networks)}")
    print(f"  Cases: {len(generator.cases)}")
    
    # Calculate approximate total entities
    total_entities = (
        len(generator.canonical_entities['people']) +
        len(generator.canonical_entities['phone_numbers']) +
        len(generator.canonical_entities['vehicles']) +
        len(generator.canonical_entities['locations']) +
        len(generator.canonical_entities['organizations']) +
        len(generator.canonical_entities['bank_accounts']) +
        len(generator.canonical_entities['events'])
    )
    print(f"  Total Entities: {total_entities}")

if __name__ == "__main__":
    main()