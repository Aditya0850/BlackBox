# BlackBox

## Project Overview
BlackBox is a digital forensic evidence management platform designed to help investigators securely manage cases, evidence, metadata, and chain of custody records.

## Features
- Case Management: Create, update, and close cases; assign investigators; track status.
- Evidence Upload: Securely upload files with automatic SHA256 hash generation for integrity verification.
- Metadata Extraction: Extract embedded metadata (EXIF, file properties) from uploaded evidence.
- Chain of Custody Logging: Immutable log of all actions performed on evidence (who, what, when).
- PDF Report Generation: Generate comprehensive reports summarizing case details, evidence list, and chain of custody.
- Role-Based Access Control: Different permissions for investigators, administrators, and auditors.
- Audit Trail: Tamper-proof logging of all system activities.
- Secure Storage: Encryption of evidence at rest and in transit.

## Tech Stack
- Backend: Node.js with Express.js (or Python/Django - to be decided)
- Database: PostgreSQL for relational data (cases, evidence, logs)
- Frontend: React with TypeScript, using shadcn/ui and Tailwind CSS
- Authentication: JWT-based authentication with role-based access
- Storage: AWS S3 or local encrypted storage for evidence files
- Verification: Client-side and server-side SHA256 hashing
- Additional: Lombok (if Java), but currently undecided

## Folder Structure
```
blackbox/
├── backend/          # Backend source code
│   ├── src/          # Source files
│   ├── tests/        # Unit and integration tests
│   ├── Dockerfile    # Containerization
│   └── ...           # Configuration files
├── frontend/         # Frontend source code
│   ├── public/       # Static assets
│   ├── src/          # React components, hooks, styles
│   └── ...           # Configuration files
├── docs/             # Documentation (SRS, design diagrams, etc.)
├── scripts/          # Utility scripts (setup, deployment, etc.)
├── README.md
├── LICENSE
└── .gitignore
```

## Installation
Since the project is in early stages, there are no runnable components yet. The backend/ and frontend/ directories currently contain placeholder files.

Future setup steps will include:
1. Clone the repository: `git clone https://github.com/Aditya0850/BlackBox.git`
2. Backend setup:
   - Navigate to `backend/` directory
   - Install dependencies: `npm install` (or `pip install -r requirements.txt`)
   - Set up environment variables (copy `.env.example` to `.env` and configure)
   - Run database migrations: `npx prisma migrate dev` (or equivalent)
   - Start the development server: `npm run dev`
3. Frontend setup:
   - Navigate to `frontend/` directory
   - Install dependencies: `npm install`
   - Set up environment variables (if any)
   - Start the development server: `npm start`
4. Ensure backend is running on http://localhost:5000 and frontend on http://localhost:3000

## Usage
Once installed, users can:
1. Register an account or log in (if authentication is enabled).
2. Create a new case with details like case number, title, description, and assigned investigator.
3. Upload evidence files to a case; the system will automatically compute SHA256 hashes and extract metadata.
4. View evidence details, including metadata and chain of custody log.
5. Generate PDF reports for a case or specific evidence items.
6. Audit trail: administrators can view system-wide logs.

## API/Backend Details
The backend will provide a RESTful API (or GraphQL) for the frontend to interact with. Planned endpoints include:
- POST /cases - Create a new case
- GET /cases - List all cases (with filtering)
- GET /cases/:id - Get a specific case
- PUT /cases/:id - Update a case
- DELETE /cases/:id - Delete a case (or soft delete)
- POST /cases/:id/evidence - Upload evidence to a case
- GET /evidence/:id - Get evidence details
- POST /evidence/:id/metadata - Extract and store metadata for evidence
- GET /evidence/:id/log - Get chain of custody log for evidence
- POST /reports/generate - Generate PDF report for a case
- POST /auth/login - User login
- POST /auth/logout - User logout
- GET /audit/logs - Retrieve audit trail (admin only)

## Future Improvements
- Implement blockchain-based evidence tamper-proofing
- Add support for bulk evidence import/export
- Integrate with law enforcement databases (e.g., NCIC)
- Add facial recognition and object detection for media evidence
- Implement role-based workflow automation
- Add multi-language support
- Develop mobile application for field investigators
- Integrate with SIEM systems for real-time alerts
- Add cloud-native deployment options (Kubernetes, AWS)
- Implement machine learning for anomaly detection in evidence access patterns