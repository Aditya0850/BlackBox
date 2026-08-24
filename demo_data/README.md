# Demo Dataset for BlackBox Criminal Network Analysis System

This dataset contains synthetic data designed to test and demonstrate the BlackBox system's capabilities for PS 26189 (AI-Powered Criminal Network Analysis System).

## Overview
The dataset simulates a criminal investigation involving a drug trafficking operation with money laundering elements. It includes interconnected data sources that, when analyzed together, reveal a hidden network connecting three primary suspects through phone numbers, locations, financial transactions, and criminal activities.

## Hidden Network to Discover
**Primary Suspects:**
1. **Rajesh Kumar** (aka "Raju") - Drug supplier, uses phone +91 98765 43210
2. **Priya Sharma** (aka "Priya") - Money launderer, uses phone +91 87654 32109  
3. **Vikram Singh** (aka "Vik") - Courier/driver, uses phone +91 76543 21098

**Connections:**
- Rajesh calls Priya to coordinate drug payments
- Priya pays Vikram via bank transfer for deliveries
- Vikram uses specific locations for drop-offs
- All three share connections to common locations (safe houses, meeting points)

## Dataset Structure
```
demo_data/
├── fir_reports/              # FIR-style text documents
│   ├── fir_001.txt           # Initial complaint - missing person/drugs
│   ├── fir_002.txt           # Surveillance report - suspicious activity
│   ├── fir_003.txt           # Financial intelligence - unusual transactions
│   └── fir_004.txt           # Witness statement - courier sighting
├── cdrs/                     # Call Detail Records (CSV format)
│   ├── cdrs_week1.csv        # Call logs for investigation week 1
│   └── cdrs_week2.csv        # Call logs for investigation week 2
├── financial_records/        # Bank transaction records
│   ├── transactions_jan.csv  # January transactions
│   └── transactions_feb.csv  # February transactions
├── surveillance_reports/     # Field observation reports
│   ├── surv_001.txt          # Location surveillance - safe house
│   ├── surv_002.txt          # Vehicle sighting - suspicious car
│   └── surv_003.txt          # Financial surveillance - cash deposits
└── social_media/             # Social media intelligence snippets
    ├── sm_001.txt            # WhatsApp chat excerpt
    ├── sm_002.txt            # Facebook post
    └── sm_003.txt            # Instagram comment
```

## Expected Results from BlackBox Analysis

### Entities to Extract:
**People:**
- Rajesh Kumar (+91 98765 43210)
- Priya Sharma (+91 87654 32109)
- Vikram Singh (+91 76543 21098)
- Suresh Patel (landlord)
- Anita Desai (witness)
- etc.

**Phone Numbers:**
- +91 98765 43210 (Rajesh)
- +91 87654 32109 (Priya)
- +91 76543 21098 (Vikram)
- +91 99887 76655 (Burner phone used by Vikram)
- etc.

**Locations:**
- 123 MG Road, Indore (Rajesh's known address)
- 456 Palace Colony, Bhopal (Priya's registered address)
- 789 VIP Road, Indore (Safe house used for meetings)
- Nehru Nagar Bus Stand, Indore (Common drop-off point)
- etc.

**Vehicles:**
- MH02 AB 1234 (Vikram's motorcycle)
- DL01 CD 5678 (Suspected surveillance vehicle)
- etc.

**Organizations:**
- "Shyam Traders" (Front company used by Priya)
- "QuickLogistics" (Fake courier service)
- etc.

### Relationships to Discover:
- Rajesh → (calls) → Priya
- Priya → (pays via bank transfer) → Vikram
- Vikram → (delivers to) → Nehru Nagar Bus Stand
- Rajesh ↔ (meets at) → 789 VIP Road, Indore ↔ Priya
- Vikram → (uses burner phone) → +91 99887 76655
- etc.

### Key Insights the System Should Surface:
1. **Central Figure**: Priya Sharma shows high connectivity (financial hub)
2. **Communication Pattern**: Rajesh and Priya communicate before financial transfers
3. **Movement Pattern**: Vikram's movements correlate with call timing to Priya
4. **Location Intelligence**: Multiple suspects connected to 789 VIP Road, Indore
5. **Financial Trail**: Unusual cash deposits matching payment timings

## Usage Instructions

1. **For FIR Reports**: Upload `.txt` files through evidence upload - OCR will extract text
2. **For CDRs**: Upload CSV files - system should parse call records
3. **For Financial Records**: Upload CSV files - transaction data extraction
4. **For Surveillance/Social Media**: Upload as documents or text files

## Data Generation Notes
- All data is SYNTHETIC and artificially generated for demonstration purposes
- No real persons, phone numbers, or financial data is used
- Patterns are designed to be detectable by NLP and link analysis
- Timestamps, amounts, and details follow realistic ranges for Indian context