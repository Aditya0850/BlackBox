# Using the Demo Dataset with BlackBox

This guide explains how to use the synthetic demo dataset to test and demonstrate the BlackBox system's capabilities for PS 26189.

## Prerequisites
- BlackBox backend running (`docker compose up backend`)
- PostgreSQL, MinIO, and Redis services healthy
- Basic understanding of the API endpoints

## Step-by-Step Usage

### 1. Prepare the Evidence Files
All demo data files are located in `A:\BlackBox\demo_data\` organized by type:
- `fir_reports/` - FIR-style text documents
- `cdrs/` - Call Detail Records (CSV)
- `financial_records/` - Bank transaction records (CSV)
- `surveillance_reports/` - Field observation reports
- `social_media/` - Social media intelligence snippets

### 2. Upload Evidence via API
You can upload files individually or in batches using the evidence API:

**Single file upload (using curl):**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/evidence/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@"./demo_data/fir_reports/fir_001.txt"' \
  -F 'reason="Initial investigation - missing person and suspected drug activity"'
```

**Batch upload script (Python example):**
```python
import requests
import os

def upload_evidence(file_path, reason):
    url = "http://localhost:8000/api/v1/evidence/upload"
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'reason': reason}
        response = requests.post(url, files=files, data=data)
    return response.json()

# Upload all FIR reports
fir_dir = "./demo_data/fir_reports/"
for filename in os.listdir(fir_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(fir_dir, filename)
        result = upload_evidence(filepath, f"FIR report: {filename}")
        print(f"Uploaded {filename}: {result}")

# Similar loops for other directories...
```

### 3. Link Evidence to Cases
After uploading evidence, create a case and link the evidence:

```bash
# Create a case
curl -X 'POST' \
  'http://localhost:8000/api/v1/cases/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Drug Trafficking Investigation - Indore/Bhopal",
    "case_number": "DTI/2026/001",
    "description": "Investigation into drug trafficking network with money laundering elements",
    "created_by": "00000000-0000-0000-0000-000000000001"
  }'

# Get evidence IDs (from upload responses or list endpoint)
# Link evidence to case
curl -X 'POST' \
  'http://localhost:8000/api/v1/evidence/{evidence_id}/link' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "case_id": "case-uuid-here",
    "reason": "Evidence related to drug trafficking investigation"
  }'
```

### 4. Trigger Analysis Pipeline
Once evidence is linked to a case, the analysis pipeline will automatically process it through:
1. Integrity check (hash verification)
2. Metadata extraction (EXIF, timestamps, etc.)
3. OCR stage (text extraction from documents/images)
4. Entity extraction (people, phones, locations, etc.) [TO BE IMPLEMENTED]
5. Relationship extraction (connections between entities) [TO BE IMPLEMENTED]
6. AI summary generation [CURRENTLY STUBBED - NEEDS REAL LLM]

### 5. View Results
After processing, you can view the results:

**Get case details:**
```bash
curl -X 'GET' 'http://localhost:8000/api/v1/cases/{case_id}'
```

**Get evidence list for case:**
```bash
curl -X 'GET' 'http://localhost:8000/api/v1/cases/{case_id}/evidence'
```

**Get findings/snapshots:**
```bash
curl -X 'GET' 'http://localhost:8000/api/v1/evidence/{evidence_id}/snapshots'
```

**Future endpoints to be implemented:**
- `GET /api/v1/cases/{case_id}/entities` - Extracted entities
- `GET /api/v1/cases/{case_id}/relationships` - Entity relationships  
- `GET /api/v1/cases/{case_id}/graph` - Knowledge graph visualization data

## Expected Entity Extraction Results

From the demo dataset, the system should extract:

### People Entities:
- Rajesh Kumar (phone: +91 98765 43210)
- Priya Sharma (phone: +91 87654 32109) 
- Vikram Singh (phone: +91 76543 21098)
- Suresh Patel (landlord/complainant)
- Anita Desai (investigating officer)
- Ramesh Kumar (surveillance officer)
- etc.

### Phone Number Entities:
- +91 98765 43210 (Rajesh)
- +91 87654 32109 (Priya)
- +91 76543 21098 (Vikram)
- +91 99887 76655 (Vikram's burner phone)
- etc.

### Location Entities:
- 123 MG Road, Indore
- 456 Palace Colony, Bhopal
- 789 VIP Road, Indore (safe house)
- Nehru Nagar Bus Stand, Indore
- etc.

### Vehicle Entities:
- MH02 AB 1234 (Rajesh's motorcycle)
- MP04 CD 5678 (Priya's/shyam traders sedan)
- MH02 EF 9012 (Vikram's motorcycle)
- etc.

### Organization Entities:
- Shyam Traders (Priya's front company)
- QuickLogistics (mentioned in chats)
- etc.

### Expected Relationship Results:
- Rajesh Kumar --(calls)--> Priya Sharma
- Priya Sharma --(pays via bank transfer)--> Vikram Singh  
- Vikram Singh --(delivers to)--> Nehru Nagar Bus Stand
- Rajesh Kumar --(meets at)--> 789 VIP Road, Indore <--(meets at)--> Priya Sharma
- Vikram Singh --(uses)--> +91 99887 76655 (burner phone)
- etc.

## Demonstration Flow for PS 26189

1. **Upload** the 12+ demo documents (FIRs, CDRs, financial records, surveillance reports, social media snippets)
2. **Create** a case for "Drug Trafficking Network Investigation"
3. **Link** all evidence to the case
4. **Wait** for pipeline processing (should take 1-2 minutes depending on OCR/LLM speed)
5. **View** the knowledge graph showing:
   - Nodes: People (colored by role), phones, locations, vehicles, organizations
   - Edges: Relationships with labels (calls, pays, delivers, meets at, uses)
6. **Click** on any node to see the source evidence (e.g., click on "Rajesh Kumar" to see FIR_001.txt, CDR records, surveillance report, WhatsApp chat excerpt)
7. **Explain** how the system traced the AI conclusions back to specific evidence pieces

## Notes for Hackathon Demo

- The dataset is designed to show a clear network: Rajesh (supplier) ↔ Priya (financier/logistics) ↔ Vikram (courier) with money flow and communication patterns
- Timestamps in CDRs and financial records correlate to show the sequence: calls → transfers → cash deposits → deliveries
- Social media snippets provide additional context and relationship confirmation
- All connections are traceable to specific source documents through the existing snapshot/finding/evidence architecture
- This demonstrates the "explainable AI, not black box" principle perfectly - every node in the graph can be clicked back to its source evidence

## Customization

You can modify the dataset to:
- Add more complex relationships
- Introduce red herrings or false leads
- Change the criminal activity type (extortion, human trafficking, etc.)
- Adjust difficulty levels for different demo scenarios

The key is maintaining the traceability: every AI-extracted entity/relationship must be linkable to specific source evidence in the system.