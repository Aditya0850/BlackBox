# BlackBox SIH26189 Large-Scale Synthetic Dataset Generation Plan

## Overview
This document outlines the strategy for generating a large-scale synthetic dataset (20,000+ records) for demonstrating and benchmarking the BlackBox Criminal Network Analysis System (SIH 2026 Problem Statement 26189).

## Current State Analysis
The existing dataset in `demo_data/` contains:
- FIR/police reports: 2 files
- CDR records: 2 CSV files (~25 records each)
- Financial transactions: 2 CSV files (~7 records each)
- Surveillance reports: 3 files
- Social media/intelligence: 3 files
- Witness statements: 0 files (in current demo_data)
- Total: ~12 documents with minimal records

This is insufficient for demonstrating large-scale network analysis capabilities.

## Proposed Dataset Architecture

### 1. Synthetic World Model Foundation
Before generating observations, we will define a coherent synthetic world:

**Entities to Define:**
- **People**: 1,200+ canonical entities (600 criminal network participants, 600 legitimate individuals)
- **Phone Numbers**: 600+ canonical numbers (including burner/disposable phones)
- **Vehicles**: 350+ canonical vehicles (with registration details)
- **Locations**: 350+ canonical locations (addresses, types, significance)
- **Organizations**: 180+ canonical organizations (mix of legitimate fronts, legitimate businesses, shell companies)
- **Bank Accounts**: 350+ canonical accounts (linked to people/organizations)
- **Events**: 500+ canonical events (meetings, transactions, incidents with timestamps)

Each entity will have:
- Stable canonical ID (e.g., P0001, PH0001, V0001, L0001, O0001, A0001, E0001)
- Core attributes (name, type, details)
- Aliases/variations
- Validity periods (for temporal aspects)
- Network affiliations

### 2. Multiple Criminal Networks (8-15 distinct networks)
We will create varied network structures:

**Network Types:**
1. **Hierarchical Drug Cartel** (clear leadership, tiers)
2. **Hub-and-Spoke Financial Fraud** (central figure with multiple associates)
3. **Loosely Connected Cybercrime Ring** (specialized members, infrequent direct contact)
4. **Clustered Smuggling Operation** (geographic clusters connected by bridges)
5. **Decentralized Hawala Network** (peer-to-peer trust-based)
6. **Human Trafficking Pipeline** (source-transit-destination structure)
7. **Counterfeit Goods Distribution** (manufacturing-logistics-sales)
8. **Political Corruption Network** (officials-businessmen-middlemen)
9. **Terror Financing Cell** (small, tight-knit, alternate funding)
10. **Wildlife Poaching Syndicate** (local hunters-international buyers)

Each network will have:
- 8-25 participants
- Defined roles (leader, financier, enforcer, technician, etc.)
- Internal communication patterns
- Financial flow patterns
- Geographic spread
- Legitimate-looking associates

### 3. Cross-Case Connections (50-100 synthetic cases)
Cases will represent investigative groupings:

**Case Types:**
- FIR-based cases (crime-specific)
- Intelligence-led cases (surveillance/informant driven)
- Financial investigation cases (money laundering focus)
- Cybercrime cases (digital evidence focus)
- Narcotics cases
- Human trafficking cases
- Financial fraud cases
- Organized crime cases

**Connection Mechanisms:**
- **Direct Entity Sharing**: Same person appears in multiple cases
- **Attribute Sharing**: Same phone/vehicle/location/account but different person aliases
- **Temporal Proximity**: Events in different cases close in time
- **Pattern Similarity**: Similar M.O. across cases
- **Institutional Links**: Same investigator/analyst involved
- **Geographic Proximity**: Cases in same area suggesting related activity

**Connection Statistics:**
- ~15-20% of cases will have genuine cross-case connections
- ~30-40% will have misleading similarities (red herrings)
- ~40-50% will be largely independent

### 4. Red Herring Strategy (30-40% of interesting-looking relationships)
Red herrings will be carefully crafted to test contextual reasoning:

**Types of Red Herrings:**
- **Name Collisions**: Common names (Rahul Sharma, Priya Patel) appearing in unrelated contexts
- **Legitimate Business Activity**: Normal transactions that resemble suspicious patterns
- **Family/Social Connections**: Legitimate frequent communication mistaken for criminal coordination
- **Wrong Numbers/Misdials**: Accidental calls creating false associations
- **Shared Public Locations**: Bus stations, markets, airports used by many unrelated people
- **Common Vehicle Models**: Popular makes/models appearing in multiple contexts
- **Routine Financial Activity**: Salary payments, utility bills, legitimate business transfers
- **Occupational Patterns**: Doctors calling patients, teachers contacting parents, delivery services
- **Seasonal/Event-Based Spikes**: Festival shopping, holiday travel, event attendance
- **Expired/Reassigned Attributes**: Old phone numbers reassigned, sold vehicles, moved residents
- **OCR/Transcription Errors**: Creating false similarities or differences
- **Deliberate Misinformation**: False intelligence reports, misleading witness statements

### 5. Entity Resolution Challenges
Realistic identity ambiguity will be built in:

**Ambiguity Types:**
- **Variations in Naming**: "Rahul Kumar", "R. Kumar", "Rahul K. Kumar", "Rahul Kr."
- **Aliases/Nicknames**: "Raju", "RK", "The Boss" for same person
- **Transliteration Variants**: Hindi/English mix ("Rahul Kumar" vs "राहुल कुमार")
- **Initials vs Full Names**: Using initials in some documents, full names in others
- **OCR Errors**: "O" vs "0", "l" vs "I", "rn" vs "m" creating name variations
- **Missing Information**: Partial names, incomplete phone numbers, vague locations
- **Outdated Information**: Old addresses, disconnected phones, sold vehicles
- **Shared Attributes**: Family members sharing addresses, phone plans, vehicles
- **Professional Titles**: Dr., Mr., Ms., Insp., SI, HC affecting name presentation
- **Contextual Names**: Maiden names vs married names, business names vs personal names

Ground truth will explicitly map each record mention to canonical entity IDs, specifying:
- Confidence level of the mention
- Which attributes matched
- What ambiguity was present
- Whether it's a true match or should be resolved as different entity

### 6. Temporal Patterns (2024-2026 timeframe)
Timestamps will be distributed realistically:

**Temporal Features:**
- **Overall Distribution**: Activity spread over 30 months (2024-01 to 2026-06)
- **Network-Specific Patterns**:
  - Buildup phases before major operations
  - Cool-down periods after incidents
  - Regular meeting schedules (weekly, monthly)
  - Payment cycles (salary, supply payments)
  - Communication bursts before events
  - Dormant periods followed by reactivation
- **Legitimate Patterns**:
  - Business hours activity (9 AM-7 PM)
  - Weekend vs weekday variations
  - Holiday effects (increased shopping, reduced business)
  - Seasonal business cycles (agricultural, tourism, retail)
  - Commute patterns (morning/evening peaks)
- **Anomalous Patterns to Detect**:
  - Unusual late-night activity (2 AM-5 AM)
  - Sudden increases in communication frequency
  - Regular small transfers followed by large withdrawal
  - Activity shifting geographic locations
  - Coordinated silence (avoiding detection)
  - Artificial timing to avoid pattern detection

### 7. Financial Network Generation
Synthetic financial activity will mimic real-world patterns:

**Transaction Types:**
- **NEFT/RTGS**: Large value transfers (₹50,000-₹5,000,000)
- **IMPS/UPI**: Smaller instant transfers (₹500-₹50,000)
- **Cash Deposits/Withdrawals**: ATM and branch transactions
- **Cheque Transactions**: Paper-based (less common but present)
- **International Transfers**: SWIFT-like for cross-border cases
- **Hawala/Hundi**: Informal value transfer (not directly in bank records but inferable)

**Patterns to Generate:**
- **Normal Business**: Regular supplier payments, salary disbursements
- **Suspicious Chain**: A→B→C→D within 24-72 hours with specific characteristics
- **Structuring**: Multiple small transactions to avoid reporting thresholds
- **Round-amount Transactions**: Unusually exact amounts (₹50,000, ₹1,00,000)
- **Rapid Movement**: Funds moving quickly between accounts
- **Circular Transactions**: A→B→C→A (money laundering indicator)
- **Structured Salaries**: Regular payments to multiple similar accounts
- **Business-to-Business**: Legitimate trade patterns
- **Personal Transfers**: Family support, gifts, loan repayments
- **Cash Intensive Business**: Legitimate cash-heavy operations (street vendors, transport)

**Account Types:**
- Savings accounts (individuals)
- Current accounts (businesses)
- Corporate accounts
- Trust accounts
- Joint accounts
- Dormant accounts (suddenly reactivated)

### 8. Communication Network (CDRs)
Call detail records will include:

**CDR Fields:**
- caller_number
- receiver_number
- call_timestamp
- duration_seconds
- call_type (voice, SMS, data)
- cell_tower_id
- location_area_code
- subscriber_location (approximate)
- imei (for burner phone tracking)
- call_status (completed, failed, busy)
- forwarding_info (if applicable)

**Communication Patterns:**
- **Normal Communication**: Family calls, business calls, service inquiries
- **Suspicious Patterns**:
  - Pre-event bursts (increased calls 2-6 hours before meeting)
  - Post-event follow-up (calls after delivery/transaction)
  - burner phone usage (short-lived, frequently changing)
  - cliff-effect communication (sudden start/stop)
  - timed communication (same time daily/weekly)
  - location-based calling (calls only from specific areas)
  - callback patterns (specific number always calls back)
  - hub communication (one number calls many others briefly)
  - silent calls (very short duration, likely signaling)
- **Legitimate High-Volume**: Customer service, telemarketing, delivery services
- **Wrong Numbers**: Random misdials
- **Network Issues**: Failed calls, busy signals (provide context)
- **International Calls**: For cross-border cases
- **Roaming Indicators**: When subjects travel

### 9. Location Intelligence
Locations will be richly defined:

**Location Types:**
- **Residential**: Apartments, houses, hostels, PGs
- **Commercial**: Offices, shops, factories, warehouses
- **Public**: Parks, stations, airports, malls, hospitals
- **Transport**: Bus stands, railway stations, taxi stands, petrol pumps
- **Hospitality**: Hotels, restaurants, dhabas, guest houses
- **Educational**: Schools, colleges, coaching centers
- **Healthcare**: Clinics, hospitals, pharmacies
- **Financial**: Banks, ATMs, exchange offices, hawala centers
- **Criminal-Associated**: Known safe houses, meeting points, drop zones (unknown to public)
- **Geographic Features**: Rivers, borders, checkpoints, highways

**Location Attributes:**
- Precise address (with potential variations/errors)
- Area/locality
- City/Town
- State
- Pincode
- Location type/significance
- Ownership/occupancy information (may be incomplete/wrong)
- Historical usage
- Surveillance coverage (known/unknown)
- Accessibility (entry/exit points, CCTV coverage)
- Typical foot traffic/vehicle flow

**Location Records to Generate:**
- Property ownership/rental records
- Utility connections (electricity, water, gas)
- Business licenses/registrations
- Surveillance camera registrations
- Vehicle parking records
- Entry/exit logs (from secure locations)
- Cell tower coverage maps
- Public transport schedules
- Event venue bookings
- Hotel/guest house registrations

### 10. Document Realism
Text-based sources will mimic real investigative documents:

**Document Types and Styles:**
- **FIRs**: Formal police reports with structured format, varying detail levels
- **Police Reports**: Internal memos, technical reports, progress updates
- **Witness Statements**: Varied literacy levels, emotional tone, memory inconsistencies
- **Surveillance Reports**: Objective observations, timed entries, officer notes
- **Intelligence Notes**: Informant reports, intercepted comms summaries, analysis
- **Social Media**: Platform-specific styles (Twitter brevity, Facebook longer, Instagram visual-focused)
- **Financial Records**: Bank statements, transaction alerts, SMS notifications
- **Vehicle Records**: RC book extracts, insurance documents, PUC certificates
- **Medical Reports**: Hospital summaries, test results, medico-legal reports
- **Educational Records**: Bonafide certificates, mark sheets, transfer certificates
- **Communication Logs**: Call logs, SMS logs, email headers (redacted)
- **Legal Documents**: Court notices, bail orders, charge sheets (partial)
- **Travel Records**: Ticket copies, passport entries, visa stamps
- **Shipping Documents**: Bills of lading, packing lists, customs declarations

**Realism Features:**
- **Writing Styles**: Formal bureaucratic, casual personal, technical, emotional
- **Abbreviations**: Police codes, banking terms, medical shorthand, local slang
- **Inconsistent Date Formats**: DD-MM-YYYY, MM/DD/YY, D-M-YYYY, written dates
- **Spelling Mistakes**: Common typos, phonetic spelling, language interference errors
- **Partial Information**: Incomplete phone numbers, vague descriptions, missing fields
- **Aliases and Nicknames**: How people are actually referred to in different contexts
- **References to Previous Reports**: "As mentioned in FIR No....", "Continuing from previous report..."
- **OCR-like Corruption**: Character substitution, word splitting/merging, line noise (for scanned docs)
- **Handwritten Elements**: Simulated notes, corrections, marginalia
- **Multilingual Content**: Hindi-English mix, regional language terms, code-switching
- **Form Variations**: Different form versions, missing fields, extra fields
- **Time Stamps**: Varying precision (exact time, approximate time, time ranges)
- **Location Descriptions**: Varying specificity (exact address, landmark-based, area-based)
- **Redaction Styles**: Different agencies' redaction patterns, partial masking
- **Quality Variations**: Clear prints, faded copies, water damage, creases, stains

### 11. Ground Truth Requirements
Machine-readable ground truth will be comprehensive:

**Ground Truth Structure:**
```
{
  "metadata": {
    "generation_timestamp": "...",
    "version": "1.0",
    "total_records": 20000+,
    "date_range": {"start": "2024-01-01", "end": "2026-06-30"},
    "scenario": "SIH26189_Criminal_Network_Analysis"
  },
  "canonical_entities": {
    "people": {
      "P0001": {
        "canonical_name": "Rahul Kumar Sharma",
        "aliases": ["Rahul Sharma", "R.K. Sharma", "Rahul K.", "Raju"],
        "phone_numbers": ["PH0001", "PH0045"],  // current and historical
        "addresses": ["L0001", "L0087"],        // current and historical
        "vehicles": ["V0023"],                 // owned/registered
        "organizations": ["O0012", "O0034"],   // employed by, associated with
        "bank_accounts": ["A0056", "A0089"],
        "demographics": {"age": 32, "gender": "M", "occupation": "business"},
        "network_affiliations": ["N003", "N007"], // criminal network IDs
        "case_involvements": ["C001", "C005", "C012"], // case IDs
        "validity_period": {"start": "2023-01-01", "end": "2026-12-31"},
        "notes": "Primary suspect in drug trafficking network"
      }
    },
    "phone_numbers": { ... },
    "vehicles": { ... },
    "locations": { ... },
    "organizations": { ... },
    "bank_accounts": { ... },
    "events": { ... }
  },
  "record_mappings": {
    "fir_reports/fir_0001.txt": {
      "document_type": "FIR",
      "case_id": "C001",
      "timestamp": "2024-03-15",
      "mentions": {
        "people": [{"entity_id": "P0001", "confidence": 0.95, "context": "complainant", "name_variation": "Rahul Kumar Sharma"}],
        "phone_numbers": [{"entity_id": "PH0001", "confidence": 0.90, "context": "contact_number"}],
        "locations": [{"entity_id": "L0001", "confidence": 0.88, "context": "incident_location"}],
        "organizations": [],
        "vehicles": [],
        "bank_accounts": [],
        "events": [{"entity_id": "E0005", "confidence": 0.70, "context": "related_incident"}]
      },
      "relationships_implied": [
        {"subject": "P0001", "predicate": "lives_at", "object": "L0001", "confidence": 0.85, "evidence": "address_on_record"}
      ]
    }
    // ... similar for all 20,000+ records
  },
  "true_relationships": {
    // Relationships that are factually true in the synthetic world
    "P0001-PH0001": {"type": "owns_uses", "confidence": 1.0, "validity": "2024-01-01 to 2026-06-30"},
    "P0001-L0001": {"type": "resides_at", "confidence": 0.95, "validity": "2024-03-01 to 2026-06-30"},
    "P0001-O0012": {"type": "employed_by", "confidence": 0.90, "validity": "2024-01-15 to 2025-08-30"},
    "P0001-P0002": {"type": "communicates_with", "confidence": 0.85, "validity": "2024-05-10 to 2024-08-20", "frequency": "daily"},
    "A0056-A0089": {"type": "funds_transfer", "confidence": 0.95, "validity": "2024-06-15", "amount": 250000, "method": "NEFT"},
    // ... thousands of true relationships
  },
  "false_relationships": {
    // Relationships that might be inferred incorrectly but are actually false
    "P0001-P0050": {"type": "communicates_with", "actually_false": true, "reason": "wrong_number_calls", "evidence": "PH0001 called PH0150 by mistake 3 times"},
    "L0001-L0050": {"type": "frequently_visited_together", "actually_false": true, "reason": "common_landmark", "evidence": "both near same railway station but different purposes"},
    // ... false relationships to test precision
  },
  "criminal_networks": {
    "N001": {
      "name": "Northern Drug Cartel",
      "type": "hierarchical",
      "primary_activity": "narcotics_trafficking",
      "geographic_focus": ["Delhi", "Uttar Pradesh", "Haryana"],
      "members": ["P0001", "P0002", "P0005", "P0008", "P0012", "P0015", "P0020"],
      "structure": {
        "leader": "P0001",
        "lieutenants": ["P0002", "P0005"],
        "enforcers": ["P0008", "P0012"],
        "technicians": ["P0015"],
        "foot_soldiers": ["P0020", "P0025", "P0030"]
      },
      "communication_pattern": "burner_phones_with_hierarchical_flow",
      "financial_pattern": "layered_transfers_via_shell_companies",
      "typical_transaction_size": "500000-5000000",
      "communication_frequency": "burst_before_operations",
      "known_fronts": ["O0012", "O0034", "O0056"],
      "known_vehicles": ["V0023", "V0045", "V0067"],
      "known_locations": ["L0001", "L0034", "L0078", "L0099"]
    }
    // ... 8-15 networks
  },
  "cases": {
    "C001": {
      "case_number": "FIR/IND/2024/00123",
      "title": "Suspected Narcotics Activity - Indore",
      "case_type": "narcotics",
      "opening_date": "2024-03-15",
      "investigating_officer": "P0050",  // refers to person entity
      "supervising_officer": "P0051",
      "primary_network": "N003",
      "secondary_networks": [],
      "status": "open",
      "classification": "confidential",
      "evidence_items": ["fir_reports/fir_0001.txt", "police_reports/pr_0001.txt", ...],
      "linked_cases": ["C005", "C012"],  // cases with genuine connections
      "superficially_similar_cases": ["C003", "C007", "C015"],  // cases with red herring similarities
      "expected_discoveries": {
        "central_entities": ["P0001", "P0002"],
        "bridge_entities": ["P0005"],
        "suspicious_patterns": ["call-transfer-delivery_sequence", "burner_phone_usage"],
        "cross_case_links": ["C005-via-investigator-P0050"]
      }
    }
    // ... 50-100 cases
  },
  "entity_resolution_challenges": {
    "ambiguous_name_clusters": {
      "NC001": {
        "canonical_entities": ["P0001", "P0150", "P0300"],  // these different people share name variants
        "name_variations": ["Rahul Kumar", "R.K. Sharma", "Rahul K.", "Raju"],
        "occurrences": {
          "P0001": ["fir_0001.txt", "surv_0005.txt", "cdrs_week1.csv:row_125"],
          "P0150": ["fir_0050.txt", "ws_0012.txt", "social_0030.txt"],
          "P0300": ["fin_0020.txt", "surv_0015.txt", "cdrs_week2.csv:row_890"]
        },
        "distinguishing_features": {
          "P0001": ["phone_PH0001", "location_L0001", "vehicle_V0023"],
          "P0150": ["phone_PH0150", "location_L0150", "organization_O0075"],
          "P0300": ["phone_PH0300", "location_L0300", "bank_account_A0300"]
        }
      }
      // ... many such clusters
    }
  },
  "temporal_patterns": {
    "expected_to_detect": [
      {
        "pattern_type": "pre_event_communication_burst",
        "description": "Increased communication frequency 2-6 hours before meetings/transactions",
        "expected_precision": ">0.80",
        "expected_recall": ">0.75",
        "networks_affected": ["N001", "N003", "N005", "N007"]
      },
      {
        "pattern_type": "call-transfer-delivery_sequence",
        "description": "Call coordination → financial transfer → physical delivery within 4-8 hour window",
        "expected_precision": ">0.85",
        "expected_recall": ">0.70",
        "networks_affected": ["N001", "N002", "N004"]
      },
      {
        "pattern_type": "location_temporal_pattern",
        "description": "Specific location used repeatedly at specific times for specific purposes",
        "expected_precision": ">0.75",
        "expected_recall": ">0.80",
        "networks_affected": ["N001", "N003", N006"]
      }
    ],
    "legitimate_patterns_that_should_not_trigger": [
      {
        "pattern_type": "regular_business_hours_calls",
        "description": "Calls between 9 AM-7 PM on weekdays for legitimate business",
        "should_flag_as_suspicious": false
      },
      {
        "pattern_type": "family_evening_calls",
        "description": "Calls between 7 PM-9 PM daily to family members",
        "should_flag_as_suspicious": false
      },
      {
        "pattern_type": "salary_credit_pattern",
        "description": "Regular monthly credits to salary accounts",
        "should_flag_as_suspicious": false
      }
    ]
  },
  "benchmark_sets": {
    "EASY": {
      "description": "Clear mentions, complete information, minimal ambiguity",
      "record_count": 5000,
      "expected_entity_extraction_f1": ">0.90",
      "expected_relationship_extraction_f1": ">0.85",
      "expected_entity_resolution_accuracy": ">0.95"
    },
    "MEDIUM": {
      "description": "Some aliases, missing fields, multiple source correlation needed",
      "record_count": 8000,
      "expected_entity_extraction_f1": ">0.80",
      "expected_relationship_extraction_f1": ">0.70",
      "expected_entity_resolution_accuracy": ">0.85"
    },
    "HARD": {
      "description": "Ambiguous names, OCR errors, conflicting information, requires deep reasoning",
      "record_count": 5000,
      "expected_entity_extraction_f1": ">0.70",
      "expected_relationship_extraction_f1": ">0.60",
      "expected_entity_resolution_accuracy": ">0.75"
    },
    "ADVERSARIAL": {
      "description": "Strong red herrings that should NOT be merged or flagged as suspicious",
      "record_count": 2000,
      "expected_false_positive_rate": "<0.10",
      "expected_incorrect_merge_rate": "<0.05",
      "expected_correct_rejection_rate": ">0.90"
    },
    "CROSS_CASE": {
      "description": "Connections only discoverable by comparing multiple cases",
      "record_count": 3000,  // spread across cases
      "expected_cross_case_link_discovery": ">0.75",
      "expected_false_cross_case_link_rate": "<0.15"
    }
  }
}
```

### 12. Benchmark Sets Documentation
Each benchmark set will have clear expectations for measuring BlackBox performance:

**Metrics to Measure:**
- **Entity Extraction**:
  - Precision: % of extracted entities that are correct
  - Recall: % of actual entities that were extracted
  - F1-Score: Harmonic mean of precision and recall
  - Entity Type Accuracy: Correct categorization (person, phone, location, etc.)

- **Relationship Extraction**:
  - Precision: % of extracted relationships that are correct
  - Recall: % of actual relationships that were extracted
  - F1-Score
  - Relationship Type Accuracy: Correct categorization of relationship types

- **Entity Resolution**:
  - Accuracy: % of entity mentions correctly mapped to canonical entities
  - Merge Accuracy: % of entity pairs correctly decided as same/different
  - Alias Handling: Correctly recognizing aliases as same entity
  - Distinction Handling: Correctly distinguishing similar names as different entities

- **Graph Analysis**:
  - Centrality Ranking Accuracy: How well the system ranks importance of nodes
  - Bridge Detection: Correctly identifying bridge nodes between communities
  - Community Detection: Accuracy in identifying network clusters
  - Link Prediction: Ability to predict missing connections

- **Cross-Case Analysis**:
  - Cross-Case Link Discovery: Finding genuine connections between cases
  - False Cross-Case Link Rate: Incorrectly linking unrelated cases
  - Pattern Similarity Detection: Recognizing similar M.O. across cases

- **Anomaly Detection**:
  - Suspicious Pattern Detection: Finding genuinely anomalous behavior
  - False Positive Rate: Flagging legitimate behavior as suspicious
  - False Negative Rate: Missing genuinely suspicious behavior

- **Explainability/Tractability**:
  - Evidence Traceability: % of AI conclusions traceable to source evidence
  - Explanation Quality: How well the system explains its reasoning
  - Confidence Calibration: Whether confidence scores match actual accuracy

- **Performance Metrics**:
  - Processing Time: Time to ingest, process, and analyze datasets of various sizes
  - Memory Usage: Resource consumption during processing
  - Scalability: How performance scales with dataset size

### 13. Demo Subset (Curated 5-10 Minute SIH Demonstration)
Even with 20,000+ records, we'll create a curated subset for effective demonstration:

**Demo Subset Characteristics:**
- **Total Records**: ~200-300 carefully selected records
- **Cases**: 2-3 interconnected cases showing the full workflow
- **Networks**: 1-2 primary criminal networks visible
- **Cross-Case Connection**: At least one genuine cross-case link
- **Red Herrings**: Several convincing red herrings that should be rejected
- **Entity Resolution Challenges**: Examples of aliases, OCR errors, etc.
- **Temporal Patterns**: Clear examples of detectable patterns
- **Financial Chains**: Visible A→B→C→D transaction sequences
- **Communication Patterns**: Clear call-transfer-delivery sequences

**Demo Flow:**
1. **Case Creation**: Investigator opens Case "Narcotics Investigation - Mumbai"
2. **Evidence Upload**: Loads ~50 evidence records (FIRs, reports, CDRs, financial, surveillance)
3. **Automatic Processing**: BlackBox runs through pipeline stages
4. **Entity Emergence**: Entities appear with confidence scores and source tracking
5. **Relationship Building**: Relationships extracted and displayed
6. **Graph Formation**: Knowledge graph visualization appears
7. **AI Identification**: System highlights non-obvious connection (e.g., burner phone usage pattern)
8. **Explainable AI**: Investigator clicks node → sees supporting evidence from multiple sources
9. **Cross-Case Revelation**: Switching to second case shows same financial pattern + shared investigator
10. **Red Herring Rejection**: System correctly flags and explains why certain connections are NOT significant
11. **Investigative Insights**: System provides actionable recommendations based on analysis
12. **Evidence Drill-Down**: Clicking on any graph element shows exact source records

**Demo Dataset Location**: `demo_data/demo_subset/` with its own ground truth and documentation

### 14. Performance and Scalability Organization
Dataset organized for benchmarking at different scales:

**Scale Tiers:**
- **Tier 1 (1K records)**: ~50 FIRs, 200 CDRs, 150 financial, 100 surveillance, 100 vehicles/locations, 100 social, 100 witness, 100 other
- **Tier 2 (5K records)**: 5x Tier 1 with increased complexity and interconnections
- **Tier 3 (10K records)**: 2x Tier 2 or 10x Tier 1 with broader network coverage
- **Tier 4 (20K+ records)**: Full dataset as specified

**Organization Strategy:**
- **Partitioning by Case**: Records grouped by investigative case
- **Partitioning by Time**: Monthly or quarterly buckets
- **Partitioning by Source Type**: Separate directories for each record type
- **Indexing Recommendations**: Suggested indexing strategies for different query patterns
- **Incremental Loading**: Design allows loading subsets without full dataset
- **Reference Integrity**: Foreign keys/IDs maintained across partitions for cross-case queries

### 15. Dataset Documentation Structure
Will create/update these documents:

```
demo_data/
├── README.md                    # Overview and usage instructions
├── GROUND_TRUTH.md             # Explanation of ground truth structure and usage
├── DATA_DICTIONARY.md          # Detailed schema of all entities, attributes, relationships
├── GENERATION_REPORT.md        # How the dataset was generated, parameters, validation
├── DEMO_SCENARIO.md            # Step-by-step demo walkthrough
├── benchmarks/                 # Benchmark definitions and expected metrics
│   ├── EASY/
│   ├── MEDIUM/
│   ├── HARD/
│   ├── ADVERSARIAL/
│   └── CROSS_CASE/
├── demo_subset/                # Curated 5-10 minute demo
│   ├── README.md
│   ├── GROUND_TRUTH.md
│   └── [data files organized by source type]
├── full_dataset/               # The complete 20,000+ record corpus
│   ├── cases/                  # Organized by case ID
│   │   ├── C0001/
│   │   │   ├── fir_reports/
│   │   │   ├── police_reports/
│   │   │   ├── witness_statements/
│   │   │   ├── cdrs/
│   │   │   ├── financial_transactions/
│   │   │   ├── surveillance_reports/
│   │   │   ├── social_media_intelligence/
│   │   │   ├── intelligence_notes/
│   │   │   ├── criminal_history/
│   │   │   └── vehicle_records/
│   │   └── ... (more cases)
│   ├── entities/               # Canonical entity definitions (ground truth core)
│   │   ├── people.json
│   │   ├── phone_numbers.json
        ... (other entity types)
│   ├── networks/               # Criminal network definitions
│   │   └── networks.json
│   └── relationships/          # Ground truth relationships
│       ├── true_relationships.json
│       └── false_relationships.json
├── world_model/                # Foundational synthetic world definitions
│   ├── locations_catalog.json
│   ├── organizations_catalog.json
│   ├── vehicle_models_catalog.json
│   └── name_databases.json     # For generating realistic names
└── generation_scripts/         # Scripts used to generate the dataset (for transparency)
```

### 16. Validation Protocol
Before completion, rigorous validation will ensure:

**Validation Checks:**
- **Referential Integrity**: All foreign/entity IDs in records point to valid canonical entities
- **Timestamp Validity**: All timestamps within 2024-01-01 to 2026-06-30 range, logically sequenced
- **Relationship Consistency**: If record A implies relationship R, ground truth confirms or explains why
- **Case Membership**: Records properly assigned to cases, case membership consistent
- **Entity Mapping**: Each record mention maps to exactly one canonical entity (with confidence)
- **ID Uniqueness**: No duplicate canonical entity IDs
- **Red Herring Validation**: Intended red herrings confirmed as non-criminal through ground truth
- **Relationship Discoverability**: Intended hidden relationships actually inferable from source records
- **PII Scrubbing**: No real personal information used (all synthetic)
- **Ground Truth Isolation**: Ground truth not leaked into evidence files
- **Format Consistency**: Appropriate formats used for each source type
- **Completeness**: Target record counts met for each category
- **Realism Spot Check**: Manual review of samples for investigative realism

## Next Steps

Before generating the 20,000+ records, I need your approval on:

1. **Overall Architecture**: Does the proposed structure meet your requirements?
2. **Scale Targets**: Are the approximate counts per source type acceptable?
3. **Network Design**: Do the 8-15 network types and 50-100 cases sound appropriate?
4. **Ground Truth Structure**: Does the proposed JSON structure work for your evaluation needs?
5. **Benchmark Sets**: Are the EASY/MEDIUM/HARD/ADVERSARIAL/CROSS_CASE categories useful?
6. **Demo Subset**: Should this be extracted from the full dataset or generated separately?
7. **Any Specific Requirements**: Particular patterns, entity types, or relationships you want emphasized?

Once approved, I will:
1. Create the directory structure
2. Generate the foundational world model (entities, attributes)
3. Create the criminal networks and case definitions
4. Generate the 20,000+ records across all source types
5. Create the comprehensive ground truth
6. Build the benchmark sets and demo subset
7. Create all documentation files
8. Run validation checks
9. Provide a final generation report

Please review this plan and let me know if you'd like any adjustments before I begin generation.