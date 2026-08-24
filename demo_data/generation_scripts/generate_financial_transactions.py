#!/usr/bin/env python3
"""
BlackBox SIH26189 Financial Transaction Generator
Generates 4,000+ synthetic financial transaction records
"""

import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add the generation_scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_fixed_world import SyntheticWorldGenerator

class FinancialTransactionGenerator:
    def __init__(self, world_model_path='demo_data/world_model/synthetic_world.json'):
        self.world_model_path = world_model_path
        self.load_world_model()
        
        # Transaction types and their characteristics
        self.transaction_types = [
            ('NEFT', 0.25, 50000, 5000000),      # (type, probability, min_amount, max_amount)
            ('RTGS', 0.15, 200000, 10000000),
            ('IMPS', 0.20, 500, 50000),
            ('UPI', 0.25, 50, 20000),
            ('CASH_DEPOSIT', 0.10, 1000, 500000),
            ('CASH_WITHDRAWAL', 0.05, 500, 200000)
        ]
        
        # Transaction purposes/categories
        self.transaction_purposes = [
            'Salary Payment', 'Business Invoice', 'Personal Transfer', 
            'Bill Payment', 'Investment', 'Loan Repayment', 
            'Gift/Donation', 'Purchase', 'Expense Reimbursement',
            'Trade Settlement', 'Supplier Payment', 'Customer Payment',
            'Rent Payment', 'Utility Bill', 'Insurance Premium',
            'Tax Payment', 'ATM Withdrawal', 'Cash Deposit',
            'Fixed Deposit', 'Recurring Deposit', 'Mutual Fund',
            'Stock Purchase', 'Property Purchase', 'Loan Disbursement'
        ]
        
        # Suspicious patterns (for red herrings and actual suspicious activity)
        self.suspicious_patterns = [
            'Structuring', 'Round-tripping', 'Hawala-like', 
            'Smurfing', 'Layering', 'Integration', 
            'Unusual Timing', 'High Frequency Low Value',
            'Rapid Movement', 'Circular Transactions'
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
        print(f"  {len(self.canonical_entities['bank_accounts'])} bank accounts")
        print(f"  {len(self.criminal_networks)} criminal networks")
        print(f"  {len(self.cases)} cases")
    
    def generate_transaction_id(self, sequence):
        """Generate a unique transaction ID"""
        return f"TXN/{sequence:010d}"
    
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
        
        # Add time of day (business hours more likely for financial transactions)
        if random.random() < 0.7:  # 70% during business hours
            hour = random.randint(9, 18)  # 9 AM to 6 PM
        else:
            hour = random.randint(0, 23)  # Any time
            
        timestamp = timestamp.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return timestamp
    
    def select_accounts(self, is_suspicious=False, network_id=None, person_id=None):
        """Select sender and receiver bank accounts"""
        account_ids = list(self.canonical_entities['bank_accounts'].keys())
        
        if not account_ids:
            return None, None
        
        if is_suspicious:
            # For suspicious transactions, try to use network connections
            if network_id and network_id in self.criminal_networks:
                network = self.criminal_networks[network_id]
                network_members = network.get('members', [])
                
                if network_members and person_id is None:
                    # Pick a random person from network
                    person_id = random.choice(network_members)
                
                if person_id is not None:
                    person = self.canonical_entities['people'].get(person_id, {})
                    person_accounts = person.get('bank_accounts', [])
                    
                    if person_accounts:
                        # Use person's accounts as one side
                        sender_account = random.choice(person_accounts)
                        # Receiver could be another network member or external
                        if random.random() < 0.6 and len(network_members) > 1:
                            # Transfer to another network member
                            other_person_id = random.choice([m for m in network_members if m != person_id])
                            other_person = self.canonical_entities['people'].get(other_person_id, {})
                            other_accounts = other_person.get('bank_accounts', [])
                            if other_accounts:
                                receiver_account = random.choice(other_accounts)
                            else:
                                receiver_account = random.choice(account_ids)
                        else:
                            # Transfer to external account
                            receiver_account = random.choice(account_ids)
                        return sender_account, receiver_account
            
            # Fallback: select random accounts with some suspicious characteristics
            if len(account_ids) >= 2:
                sender_account, receiver_account = random.sample(account_ids, 2)
                # Mark as suspicious in metadata
                return sender_account, receiver_account
        
        # Normal transaction: select random accounts
        if len(account_ids) >= 2:
            sender_account, receiver_account = random.sample(account_ids, 2)
        else:
            sender_account = receiver_account = random.choice(account_ids)
        
        return sender_account, receiver_account
    
    def generate_transaction_record(self, sequence, is_suspicious=False, network_id=None, person_id=None):
        """Generate a single financial transaction record"""
        
        # Generate timestamp
        timestamp = self.generate_timestamp()
        
        # Select transaction type based on weights and amounts
        txn_types = [t[0] for t in self.transaction_types]
        txn_weights = [t[1] for t in self.transaction_types]
        txn_type = random.choices(txn_types, weights=txn_weights)[0]
        
        # Get amount range for selected type
        txn_info = [t for t in self.transaction_types if t[0] == txn_type][0]
        _, _, min_amount, max_amount = txn_info
        
        # Generate amount
        if txn_type in ['CASH_DEPOSIT', 'CASH_WITHDRAWAL']:
            # Cash transactions often round numbers
            amount = round(random.randint(min_amount, max_amount) / 100) * 100
        else:
            amount = random.randint(min_amount, max_amount)
        
        # Select purpose
        purpose = random.choice(self.transaction_purposes)
        
        # Select accounts
        sender_id, receiver_id = self.select_accounts(is_suspicious, network_id, person_id)
        
        if sender_id is None or receiver_id is None:
            return None
        
        # Get account details
        sender_account = self.canonical_entities['bank_accounts'].get(sender_id, {})
        receiver_account = self.canonical_entities['bank_accounts'].get(receiver_id, {})
        
        # Determine if it's suspicious based on patterns
        is_suspicious_txn = is_suspicious
        suspicious_pattern = None
        
        if is_suspicious and random.random() < 0.7:  # 70% of suspicious transactions have identifiable pattern
            suspicious_pattern = random.choice(self.suspicious_patterns)
        
        # Add some randomness to suspicious flag (some normal transactions look suspicious)
        if not is_suspicious and random.random() < 0.05:  # 5% false positive rate
            is_suspicious_txn = True
            suspicious_pattern = random.choice(self.suspicious_patterns) if random.random() < 0.5 else None
        
        # Generate transaction record
        transaction_record = {
            'transaction_id': self.generate_transaction_id(sequence),
            'timestamp': timestamp.isoformat(),
            'transaction_type': txn_type,
            'amount': amount,
            'currency': 'INR',
            'purpose': purpose,
            'sender_account_id': sender_id,
            'receiver_account_id': receiver_id,
            'sender_account_number': sender_account.get('account_number', 'UNKNOWN'),
            'receiver_account_number': receiver_account.get('account_number', 'UNKNOWN'),
            'sender_bank': sender_account.get('bank_name', 'UNKNOWN'),
            'receiver_bank': receiver_account.get('bank_name', 'UNKNOWN'),
            'sender_ifsc': sender_account.get('ifsc_code', 'UNKNOWN'),
            'receiver_ifsc': receiver_account.get('ifsc_code', 'UNKNOWN'),
            'is_suspicious': is_suspicious_txn,
            'suspicious_pattern': suspicious_pattern,
            'network_id': network_id if is_suspicious_txn else None,
            'related_person_id': person_id,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        return transaction_record
    
    def generate_transaction_records(self, count=5000, output_dir='demo_data/full_dataset/financial_transactions'):
        """Generate multiple financial transaction records"""
        
        print(f"Generating {count} financial transaction records...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get network and person IDs for assigning some transactions
        network_ids = list(self.criminal_networks.keys()) if self.criminal_networks else [None]
        person_ids = list(self.canonical_entities['people'].keys()) if self.canonical_entities['people'] else [None]
        
        records = []
        suspicious_count = 0
        
        for i in range(count):
            # Determine if this transaction should be suspicious (8% base rate)
            is_suspicious = random.random() < 0.08
            network_id = None
            person_id = None
            
            if is_suspicious:
                # Try to associate with network or person
                if random.random() < 0.6 and network_ids[0] is not None:  # 60% network-related
                    network_id = random.choice(network_ids)
                elif random.random() < 0.3 and person_ids[0] is not None:  # 30% person-related
                    person_id = random.choice(person_ids)
                # 10% remain unassociated (generic suspicious)
                
                if network_id is not None or person_id is not None:
                    suspicious_count += 1
            
            # Generate transaction
            record_sequence = i + 1
            record = self.generate_transaction_record(
                sequence=record_sequence,
                is_suspicious=is_suspicious,
                network_id=network_id,
                person_id=person_id
            )
            
            if record is not None:
                records.append(record)
            
            # Progress indicator
            if (i + 1) % 400 == 0:
                print(f"  Generated {i + 1} records...")
        
        # Save records as JSON file (structured format)
        output_file = os.path.join(output_dir, 'financial_transactions.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"  Generated {len(records)} financial transaction records")
        print(f"  {suspicious_count} records marked as suspicious")
        print(f"  Saved to: {output_file}")
        
        # Also create CSV file for easier analysis
        self.create_csv_file(records, output_dir)
        
        return records
    
    def create_csv_file(self, records, output_dir):
        """Create CSV file for financial transaction records"""
        
        csv_file = os.path.join(output_dir, 'financial_transactions.csv')
        
        if not records:
            print("  No records to write to CSV")
            return
        
        # Define CSV headers
        headers = [
            'transaction_id', 'timestamp', 'transaction_type', 'amount', 'currency',
            'purpose', 'sender_account_id', 'receiver_account_id', 
            'sender_account_number', 'receiver_account_number',
            'sender_bank', 'receiver_bank', 'sender_ifsc', 'receiver_ifsc',
            'is_suspicious', 'suspicious_pattern', 'network_id', 'related_person_id'
        ]
        
        # Write CSV
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for record in records:
                # Flatten the record for CSV
                csv_record = {
                    'transaction_id': record['transaction_id'],
                    'timestamp': record['timestamp'],
                    'transaction_type': record['transaction_type'],
                    'amount': record['amount'],
                    'currency': record['currency'],
                    'purpose': record['purpose'],
                    'sender_account_id': record['sender_account_id'],
                    'receiver_account_id': record['receiver_account_id'],
                    'sender_account_number': record['sender_account_number'],
                    'receiver_account_number': record['receiver_account_number'],
                    'sender_bank': record['sender_bank'],
                    'receiver_bank': record['receiver_bank'],
                    'sender_ifsc': record['sender_ifsc'],
                    'receiver_ifsc': record['receiver_ifsc'],
                    'is_suspicious': record['is_suspicious'],
                    'suspicious_pattern': record['suspicious_pattern'] or '',
                    'network_id': record['network_id'] or '',
                    'related_person_id': record['related_person_id'] or ''
                }
                writer.writerow(csv_record)
        
        print(f"  Created CSV file: {csv_file}")


def main():
    """Main function to generate financial transaction records"""
    print("Starting Financial Transaction Generation")
    print("=" * 50)
    
    # Initialize generator
    generator = FinancialTransactionGenerator()
    
    # Generate records
    records = generator.generate_transaction_records(count=5000)
    
    print("\nFinancial transaction generation completed!")
    print(f"Total records generated: {len(records)}")
    
    # Show sample
    if records:
        sample = records[0]
        print(f"\nSample Financial Transaction:")
        print(f"  ID: {sample['transaction_id']}")
        print(f"  Timestamp: {sample['timestamp']}")
        print(f"  Type: {sample['transaction_type']}")
        print(f"  Amount: ₹{sample['amount']:,}")
        print(f"  From: {sample['sender_account_number']} ({sample['sender_bank']})")
        print(f"  To: {sample['receiver_account_number']} ({sample['receiver_bank']})")
        print(f"  Suspicious: {sample['is_suspicious']}")
        if sample['suspicious_pattern']:
            print(f"  Pattern: {sample['suspicious_pattern']}")


if __name__ == "__main__":
    main()