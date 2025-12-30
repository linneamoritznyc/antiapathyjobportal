# Changelog - Anti-Apathy Job Portal

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/)

---

## [1.0.0] - 2024-12-28

### 🎉 Initial MVP Release

**Major Features:**
- Full-stack job application automation system
- AI-powered cover letter generation
- Gmail draft creation via IMAP
- Swedish job market integration (Platsbanken)
- 8 industry-specific CV personas
- Application tracking database

---

### Added

#### Backend (Python/FastAPI)
- FastAPI server with 15+ REST endpoints
- SQLite database with jobs and applications tables
- Job scraping from Platsbanken
- Claude Sonnet 4 integration for cover letter generation
- Google Gemini integration as backup AI
- IMAP-based Gmail draft creation
- CV selection algorithm based on job industry
- Application statistics endpoint
- Background task processing for scraping
- CORS middleware for frontend communication

#### Frontend (React/Tailwind)
- Single-page application with React (CDN)
- Tailwind CSS styling
- Job browsing interface
- Cover letter preview and editing
- Statistics dashboard
- Scraping controls
- Job status management (pending/applied/skipped)

#### Database
- Jobs table with full metadata tracking
- Applications table with status management
- Indexes for performance optimization
- Foreign key relationships
- Timestamp tracking for all records

#### CV System
- 8 PDF personas covering major Swedish industries:
  - Retail & Cashier (Butik & Kassa)
  - Content Moderation
  - Industrial & Gardening (Industri & Trädgård)
  - Arts & Culture (Konst & Kultur)
  - Customer Service (Kundtjänst)
  - Hospitality (Restaurang & Café)
  - Tech & Office (Tech & Kontor)
  - Healthcare (Vård & Omsorg)
- Automatic CV selection based on job category

#### Security
- Environment variables for all credentials
- Gmail App Password support
- No hardcoded API keys
- SQL parameterization (injection prevention)
- HTTPS for all AI API calls

#### Documentation
- README with quick start guide
- API endpoint documentation
- Environment variable configuration guide
- Troubleshooting section

---

### Changed

**December 27-28, 2024:**
- Migrated from concept to working MVP
- Switched from multiple AI providers testing to Claude primary
- Changed from npm Claude Code to bash installer (then to npm due to issues)
- Repository published to GitHub (linneamoritznyc/antiapathyjobportal)

**December 24, 2024:**
- Initial architecture decisions made
- Database schema finalized
- API structure designed

---

### Fixed

**December 28:**
- Gmail draft creation endpoint added to api_server.py
- IMAP authentication issues resolved
- Environment variable handling improved
- CORS configuration for frontend-backend communication

---

### Known Issues

#### Critical 🔴
- Frontend button for Gmail drafts not yet connected
- Email extraction not automated (manual entry required)
- Some error messages are technical, not user-friendly

#### Important 🟡
- Cover letter quality varies (needs prompt refinement)
- No mobile responsive design yet
- Statistics dashboard shows numbers only (no charts)
- CV selection algorithm could be smarter

#### Minor 🟢
- No interview tracking system
- No follow-up automation
- No PDF export of applications
- No calendar integration

---

## [Unreleased]

### Planned for 1.1.0 (Week of Jan 1, 2025)

#### Will Add
- Frontend button connected to Gmail draft endpoint
- User-friendly error messages in Swedish
- Email extraction from job postings using AI
- End-to-end testing of Gmail flow

#### Will Fix
- All critical bugs from 1.0.0
- Error handling improvements
- Input validation on frontend

---

### Planned for 1.5.0 (February 2025)

#### Will Add
- Chart.js visualization for statistics
- Mobile-responsive design
- Improved cover letter prompts (target: 95% approval rate)
- Contact enrichment via company research

#### Will Improve
- AI prompt quality
- Database query performance
- Frontend UX polish

---

### Planned for 2.0.0 (Q1 2025)

#### Will Add
- Interview tracking and scheduling
- Automated follow-up system
- Calendar integration (Google Calendar)
- Success rate analytics
- PDF generation for applications
- Email sending (not just drafts)

#### Will Change
- Potential migration from SQLite to PostgreSQL
- Multi-user architecture groundwork
- Cloud deployment preparation

---

## Version History

### Development Timeline

**December 24-28, 2024:** Core development
- Day 1: Architecture design, database schema
- Day 2: Backend API implementation
- Day 3: Frontend creation, AI integration
- Day 4: Gmail integration, debugging
- Day 5: Git setup, documentation, deployment prep

**Total Development Time:** ~40 hours

---

## Breaking Changes

None yet (first version)

### Future Breaking Changes (Planned)

**Version 2.0.0 will introduce:**
- Database migration (SQLite → PostgreSQL)
- API authentication requirement
- Multi-user support (changes data model)
- Configuration file format changes

**Migration path will be provided.**

---

## Deprecations

None yet (first version)

### Future Deprecations (Tentative)

**Version 1.5.0:**
- Gemini as backup AI might be removed (focus on Claude)
- Manual email entry might become optional-only

**Version 2.0.0:**
- Local-only mode might be deprecated in favor of cloud option
- Single-user SQLite configuration

---

## Security Updates

### 1.0.0 (2024-12-28)
- Initial security implementation
- Environment variables for credentials
- App Password authentication for Gmail
- No secrets in code or version control

---

## Performance Improvements

### 1.0.0 Baseline
- Job scraping: ~20 seconds for 10 jobs
- AI generation: 2-4 seconds per letter
- Gmail draft: ~1 second creation time
- Database queries: <50ms average

---

## Bug Fixes by Version

### 1.0.0
- **Fixed:** Gmail authentication failing with main password
  - **Solution:** Implemented App Password support
  
- **Fixed:** CORS blocking frontend requests
  - **Solution:** Added CORS middleware with proper config
  
- **Fixed:** Environment variables not loading
  - **Solution:** Added os.environ.get() with validation

---

## Contributors

**Author:** Linnea Moritz ([@linneamoritznyc](https://github.com/linneamoritznyc))

**AI Assistance:**
- Claude (Anthropic) - Architecture, code generation, debugging
- Claude Code - Development tooling (attempted installation)

---

## Acknowledgments

- **Anthropic** - Claude AI platform
- **Google** - Gemini AI (backup provider)
- **FastAPI Team** - Excellent web framework
- **React Team** - Frontend framework
- **Platsbanken/Arbetsförmedlingen** - Job data source

---

## Release Notes Format

Each release includes:
- **Added:** New features
- **Changed:** Changes to existing functionality
- **Deprecated:** Soon-to-be removed features
- **Removed:** Now removed features
- **Fixed:** Bug fixes
- **Security:** Security improvements

---

## Upcoming Milestones

- **v1.1.0** - Week of January 1, 2025 (Gmail integration complete)
- **v1.5.0** - February 2025 (Mobile + Analytics)
- **v2.0.0** - Q1 2025 (Advanced automation)
- **v3.0.0** - Q2 2025 (Multi-user deployment)

---

**Last Updated:** December 28, 2024  
**Next Review:** January 5, 2025 (after 1.1.0 release)
