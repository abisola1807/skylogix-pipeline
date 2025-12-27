## 🏗️ Data Architecture Diagram


flowchart LR
    A[OpenWeather API] --> B[Python Ingestion]
    B --> C[MongoDB (Raw Layer)]
    C --> D[Airflow Orchestration]
    D --> E[PostgreSQL Analytics Warehouse]
    E --> F[Dashboards & Analytics]
