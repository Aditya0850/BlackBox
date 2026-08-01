# BlackBox

## Vision
BlackBox is a digital forensic evidence management platform designed to help investigators securely manage cases, evidence, metadata, and chain of custody records.

## Target Users
General-purpose investigators, law enforcement, corporate security teams, and legal professionals needing a secure, auditable system for handling digital evidence.

## Overview
BlackBox provides a full-stack application with a backend server and a frontend user interface. The platform focuses on security, integrity, and usability for forensic workflows.

### Core Components
- **Backend**: Server-side logic handling API requests, data storage, evidence processing, and cryptographic verification.
- **Frontend**: Web-based interface for case management, evidence upload, metadata viewing, and report generation.
- **Documentation**: Requirements and specifications located in the `docs/` directory.

## MVP Features
- **Case Management**: Create, update, and close cases; assign investigators; track status.
- **Evidence Upload**: Securely upload files with automatic SHA256 hash generation for integrity verification.
- **Metadata Extraction**: Extract embedded metadata (EXIF, file properties) from uploaded evidence.
- **Chain of Custody Logging**: Immutable log of all actions performed on evidence (who, what, when).
- **PDF Report Generation**: Generate comprehensive reports summarizing case details, evidence list, and chain of custody.

## Technical Stack (Planned)
- **Backend**: Node.js with Express or Python with Flask/Django (to be determined)
- **Database**: PostgreSQL or MongoDB for case and evidence records
- **Frontend**: React with TypeScript, utilizing shadcn/ui and Tailwind CSS for a modern UI
- **Authentication**: JWT-based authentication with role-based access control
- **Storage**: Encrypted storage for evidence files, with metadata stored in the database
- **Verification**: Client-side and server-side SHA256 hashing to ensure file integrity

## Getting Started
Since the project is in early stages, there are no runnable components yet. The `backend/` and `frontend/` directories currently contain placeholder files.

Future setup steps will include:
1. Cloning the repository
2. Installing backend dependencies (`npm install` or `pip install -r requirements.txt`)
3. Installing frontend dependencies (`npm install`)
4. Configuring environment variables (database connection, secret keys)
5. Running database migrations
6. Starting the backend server
7. Starting the frontend development server

## Contributing
Please read the contributing guidelines (to be added) before submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details (to be added).

## Contact
For questions or support, please open an issue on this repository.