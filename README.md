# 🌍 Global Command Intelligence Dashboard

An orchestrated **Common Operational Picture (COP)** designed for military decision support. This platform integrates a **Streamlit** frontend with a **MongoDB** backend, all containerized via **Docker**, to provide 3D geospatial situational awareness across Unified Combatant Command (CCMD) Areas of Responsibility.

## 🎯 Strategic Purpose
Military commanders at the CCMD level (USEUCOM, USCENTCOM, USINDOPACOM) face significant "information overload." This dashboard serves as a **Decision Support System (DSS)** that:
* **Synthesizes Data:** Aggregates unstructured intelligence into a high-fidelity 3D map.
* **Operationalizing Scale:** Adjusts map resolution to account for the "Tyranny of Distance" in the Pacific vs. land-based logistics in Europe.
* **Identifies Anomalies:** Uses 3D spikes to highlight "intensity" clusters, allowing analysts to spot narrative shifts or strategic movements in real-time.

---

## 🏗️ Project Structure
```text
intel-dashboard/
├── app.py              # Streamlit Frontend & Map Logic
├── seeder.py           # Database Utility (Mock Intel Generator)
├── requirements.txt    # Python Dependencies
├── Dockerfile          # Containerization Blueprint
└── docker-compose.yml  # Multi-Container Orchestrator
```

---

## 🚀 Quick Start

### Prerequisites
Ensure you have **Docker** and **Docker Compose** installed on your system.

This command:
- Builds the Streamlit app from the Dockerfile
- Starts MongoDB on port `27017`
- Starts the Streamlit frontend on port `8501`
- Both services are networked together automatically

```
bash docker-compose up --build
```

### Step 2: Seed the Database
In a **new terminal**, populate MongoDB with 100 mock intelligence reports: 
```
bash python seeder.py
```

This script:
- Connects to MongoDB running in Docker
- Inserts 100+ synthetic intelligence points across the three AORs
- Clears previous data to ensure fresh demo data

### Step 3: Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8501
```

You should now see the 3D geospatial map with intelligence distribution across USEUCOM, USCENTCOM, and USINDOPACOM.

---

## 🔄 System Architecture & Data Flow


### How It Works

1. **seeder.py** is run **once** to populate the database with mock data
   - Defines `AOR_CONFIG` with lat/lon/zoom for each AOR
   - Generates 100 realistic intelligence reports
   - Uses MongoDB to store them persistently

2. **app.py** (Streamlit) runs **continuously** serving the web interface
   - Imports `AOR_CONFIG` from seeder.py (single source of truth)
   - Reads from MongoDB based on user's AOR selection
   - Renders PyDeck 3D ColumnLayer with geographic distribution
   - Displays metadata in tabular format below the map

3. **MongoDB** persists the data between app restarts
   - No need to re-seed every time the app starts
   - Only re-run `seeder.py` if you want to refresh the mock data

---

## 📊 Database Schema

Each intelligence report in the `reports` collection contains:


## 🛠️ Data Strategy: Placeholder vs. Production
Currently, `seeder.py` generates **synthetic intelligence points** to demonstrate the platform’s visualization capabilities. This serves as a "Mission-Ready" placeholder.

### How to Extend This Project
This architecture is built for **Plug-and-Play** extensibility. A developer can easily replace the seeder logic with:
* **Real-time API Ingestion:** Swap the random generator for a live news API (e.g., GDELT) that filters for military keywords.
* **Automated Scrapers:** Monitor official `.mil` press releases and push them directly into the `intel_db.reports` collection.
* **NLP Analysis:** Integrate a sentiment analysis model (like HuggingFace) to automatically assign an **intensity score** to incoming text, which dynamically updates the height of the 3D spikes on the map.

---

## 🛡️ Technical Stack
* **Frontend:** Streamlit & PyDeck (High-performance 3D GL rendering)
* **Backend:** MongoDB (NoSQL for flexible, unstructured data storage)
* **Orchestration:** Docker Compose (Ensures environment parity)
* **Analysis:** Pandas & NumPy (Geospatial variance calculations)

