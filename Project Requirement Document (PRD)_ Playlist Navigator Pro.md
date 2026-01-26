# Project Requirement Document (PRD): Playlist Navigator Pro

**Project Title:** Playlist Navigator Pro (PNP)
**Author:** Manus AI (Senior Electronics Engineer & Project Manager)
**Date:** January 20, 2026
**Client:** DK_TLL (via Chat History Analysis)
**Version:** 1.0

## 1. Executive Summary

This document outlines the requirements for **Playlist Navigator Pro (PNP)**, a professional, modern web application designed to save, store, arrange, and analyze YouTube video playlists. The application will leverage the technical foundation established during the proof-of-concept phase (YouTube API integration, automated indexing, and rich metadata extraction) to provide a superior user experience for managing large video collections.

The core value proposition is to transform raw YouTube playlist data into an **interactive, searchable, and thematically organized knowledge base**.

## 2. Project Goals and Objectives

| Goal ID | Goal Description | Success Metric | Alignment with Client Need |
| :--- | :--- | :--- | :--- |
| G-01 | **Automated Data Ingestion** | 99.9% success rate for playlist extraction via YouTube API. | Eliminates manual data entry and ensures data accuracy [1]. |
| G-02 | **Advanced Data Organization** | Implementation of **Tags**, **Chronological Sorting**, and **Thematic Clustering** [2]. | Provides multiple, professional methods for organizing video content. |
| G-03 | **Modern UX/UI** | User satisfaction score > 4.5/5.0 in pilot testing. | Delivers the "professional, modern looking application" requested by the client. |
| G-04 | **Interactive Navigation** | All generated indexes (HTML/PDF) are fully searchable and expandable. | Scales the successful proof-of-concept (MIDI, TEENSY, DAISY indexes) to the entire platform [3]. |
| G-05 | **Data Export & Interoperability** | Successful export of all data to CSV and JSON formats. | Ensures data is portable and can be used in external analysis tools [4]. |

## 3. Functional Requirements

### 3.1. Data Ingestion and Processing (Backend)

| Req ID | Requirement | Description | Source |
| :--- | :--- | :--- | :--- |
| FR-01 | **YouTube API Integration** | The system MUST integrate with the YouTube Data API v3 to ingest playlist data (title, description, video list, metadata) [1]. | Chat History (API Integration) |
| FR-02 | **Automated Metadata Extraction** | The system MUST extract and store rich metadata for each video, including **Duration**, **View Count**, **Like Count**, **Comment Count**, and **Thumbnail URL** [4]. | Chat History (API Integration) |
| FR-03 | **CSV/JSON Export** | The system MUST allow users to export the processed playlist data into both **CSV** (for spreadsheet analysis) and **JSON** (for programmatic use) formats [4]. | Chat History (CSV Export) |
| FR-04 | **Data Refresh** | The system MUST provide a one-click function to refresh a stored playlist's data from the YouTube API to check for new videos or updated metadata. | Project Manager Analysis |

### 3.2. Data Organization and Filtering (Core Logic)

The application will offer three primary techniques for sorting and organizing video data:

| Req ID | Technique | Description | Implementation Detail |
| :--- | :--- | :--- | :--- |
| FR-05 | **Tags (Primary Filter)** | The system MUST allow users to assign and filter videos by custom tags (e.g., `#Teensy`, `#MIDI`, `#Arduino`) and MUST automatically suggest tags based on video title/description [3]. | Leverages the successful tag generation logic from the proof-of-concept. |
| FR-06 | **Chronological Sorting** | The system MUST allow sorting of videos by **Publication Date** (newest to oldest and vice-versa) [5]. | Uses the `Published Date` metadata extracted via API. |
| FR-07 | **Thematic Clustering** | The system MUST use a clustering algorithm (e.g., K-Means on vectorized titles/descriptions) to group videos into **Thematic Categories** (e.g., 'Hardware Projects', 'Audio Development') [2]. | Scales the manual categorization logic from the initial navigator. |
| FR-08 | **Metadata Filtering** | The system MUST allow filtering by **Duration** (e.g., videos > 10 min) and **View Count** (e.g., videos > 50,000 views) [4]. | Uses the rich metadata extracted via API. |
| FR-09 | **Duplicate Detection** | The system MUST flag and allow users to manage duplicate videos across different stored playlists [2]. | Leverages the successful duplicate detection logic from the initial navigator. |

### 3.3. User Interface and Experience (Frontend)

| Req ID | Requirement | Description | UX/UI Detail |
| :--- | :--- | :--- | :--- |
| FR-10 | **Dashboard View** | A clean, modern dashboard MUST display a list of all stored playlists with key metrics (total videos, last refresh date). | Card-based layout with clear status indicators. |
| FR-11 | **Interactive Playlist View** | The main view MUST display videos in an **expandable/collapsible tree structure** based on the selected sorting method (e.g., Thematic Cluster or Tags) [3]. | Utilizes the successful HTML/JS interactive design from the proof-of-concept. |
| FR-12 | **Global Search** | A fast, real-time search bar MUST filter videos across all stored playlists by **Title**, **Description**, and **Tags** [3]. | Implements the search functionality from the proof-of-concept. |
| FR-13 | **Video Card Display** | Each video entry MUST display the **Thumbnail**, **Title** (as a hyperlink), **Short Description**, and **Tags** [3]. | Clean, minimal card design with a focus on readability. |
| FR-14 | **Theming** | The application MUST support multiple color themes (e.g., 'Teal' for hardware, 'Purple' for general) [4]. | Leverages the successful theming logic from the indexer. |

## 4. Non-Functional Requirements

| NFR ID | Requirement | Description | Metric |
| :--- | :--- | :--- | :--- |
| NFR-01 | **Performance** | Playlist data ingestion MUST complete within 10 seconds for playlists up to 200 videos [4]. | Max Latency < 10s (for 200 videos) |
| NFR-02 | **Scalability** | The backend database MUST support up to 10,000 stored videos without performance degradation. | Database read/write latency < 50ms |
| NFR-03 | **Security** | All API keys (YouTube) MUST be stored securely as environment variables or in a vault, never in source code [4]. | API Key Exposure: Zero |
| NFR-04 | **Maintainability** | The codebase MUST be modular, well-documented, and follow modern best practices. | Code Coverage > 80% |
| NFR-05 | **Responsiveness** | The frontend MUST be fully responsive and optimized for desktop, tablet, and mobile viewing. | Lighthouse Score > 90 (Mobile & Desktop) |

## 5. Technical Architecture and Tech Stack

The application will follow a modern, decoupled **Microservices Architecture** to ensure scalability and maintainability.

### 5.1. Frontend (Client-Side)

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Framework** | **React** (with Vite) | Modern, component-based, high performance, and aligns with current web development standards. |
| **Styling** | **Tailwind CSS** | Utility-first framework for rapid, responsive, and modern UI development. Aligns with the "modern looking" requirement. |
| **State Management** | **Zustand** or **Redux Toolkit** | Efficient and scalable state management for complex filtering and interactive views. |
| **Interactive Views** | **D3.js / Vis.js** | To implement the expandable tree structure (FR-11) and potentially data visualizations. |

### 5.2. Backend (Server-Side)

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **API Framework** | **FastAPI** (Python) | High performance, asynchronous, and leverages the existing Python expertise from the proof-of-concept (FR-01, FR-03). |
| **Database** | **PostgreSQL** (with PostGIS for potential future geo-tagging) | Robust, scalable, and reliable relational database. |
| **ORM** | **SQLAlchemy** or **Drizzle** | Python ORM for clean database interaction. |
| **Data Processing** | **Pandas / Scikit-learn** | Used within the FastAPI service for **Thematic Clustering** (FR-07) and advanced data manipulation. |
| **API Integration** | **`requests`** library | Used for all YouTube Data API v3 calls (FR-01). |

### 5.3. Deployment and Infrastructure

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Containerization** | **Docker** | Ensures consistent environment across development, testing, and production. |
| **Orchestration** | **Docker Compose** | Simple local development and deployment setup. |
| **Cloud Platform** | **AWS / DigitalOcean** | Scalable, reliable cloud hosting. |

## 6. Implementation Plan (Roadmap)

The project will be executed in three phases, leveraging the existing proof-of-concept assets to accelerate development.

| Phase | Duration | Key Deliverables | Dependencies |
| :--- | :--- | :--- | :--- |
| **Phase 1: Foundation & Data Layer** | 4 Weeks | - **Backend API** (FastAPI) with CRUD for Playlists. - **Database Schema** (PostgreSQL) implemented. - **YouTube API Service** (FR-01, FR-02) fully integrated. - **CSV/JSON Export Endpoint** (FR-03) complete. | Existing `youtube_api_extractor.py` [4]. |
| **Phase 2: Core Logic & Frontend MVP** | 6 Weeks | - **Frontend Dashboard** (React/Tailwind) with basic playlist listing (FR-10). - **Interactive Playlist View** (FR-11) with basic sorting. - **Tags & Filtering Logic** (FR-05, FR-08) implemented. - **Thematic Clustering** (FR-07) algorithm integrated. | Phase 1 Completion. |
| **Phase 3: Polish, Advanced Features & Deployment** | 4 Weeks | - **Global Search** (FR-12) implemented. - **Duplicate Detection** (FR-09) and management UI. - **Theming** (FR-14) and final UX/UI polish. - **Deployment** to production environment (NFR-01, NFR-05). | Phase 2 Completion. |

## 7. Project Management and Quality Assurance

### 7.1. Quality Assurance Techniques

| Technique | Description | Alignment with Client Need |
| :--- | :--- | :--- |
| **Test-Driven Development (TDD)** | Writing unit and integration tests before writing production code. | Ensures **Robustness** (NFR-04) and **Accuracy** (FR-02). |
| **Code Review Chains** | Mandatory peer review for all pull requests. | Ensures **Maintainability** (NFR-04) and adherence to best practices. |
| **User-Guided Refinement** | Continuous feedback loop with the client during Phase 2 and 3. | Ensures **Goal Alignment** (G-03) and high **User Experience** (FR-10). |

### 7.2. Other Sorting and Organizing Techniques

In addition to **Tags** and **Thematic Clustering**, the application will employ two other advanced techniques:

1.  **Sentiment Analysis (Advanced Filtering)**:
    - **Technique**: Use a Natural Language Processing (NLP) model (e.g., VADER or a fine-tuned BERT model) to analyze the sentiment of video titles and descriptions.
    - **Functionality**: Allow users to filter videos by **Sentiment Score** (e.g., 'Highly Positive', 'Neutral', 'Negative'). This is useful for filtering out overly negative or clickbait content.

2.  **Temporal Density Analysis (Visualization)**:
    - **Technique**: Analyze the publication dates of videos within a playlist to identify periods of high and low activity.
    - **Functionality**: Present a **Temporal Density Chart** (a histogram or time-series graph) showing when the content was created. This helps the user understand the historical context and relevance of the playlist content.

## 8. References

[1] Chat History: Initial request for automated, optimized navigator.
[2] Chat History: Request for core thematics, duplicates removal, and optimized navigation.
[3] Chat History: Proof-of-concept for MIDI, TEENSY, and DAISY interactive indexes (FR-11, FR-12, FR-13).
[4] Chat History: Final enhancement request for YouTube API integration and CSV export (FR-01, FR-02, FR-03, NFR-01, NFR-03).
[5] Project Manager Analysis: Standard data organization technique for time-series data.

---
*End of Document*
