# 🏡 Scrapy Real Estate Scraper

## 📌 Overview
This project is a complete end-to-end real estate data pipeline built with **Scrapy**, **PostgreSQL**, **Apache Airflow**, and **Docker**. It scrapes property listings from multiple websites, cleans the data, stores it in a PostgreSQL database, and optionally exports it to CSV/JSON formats for further analysis.

---

## 🚀 Features
- **Automated Scraping**: Scrapy spiders collect real estate data from various websites.
- **Data Cleaning**: Custom functions clean price, size, and address fields.
- **PostgreSQL Integration**: Stores structured data in a relational database.
- **Airflow Scheduling**: Monthly scraping jobs managed by Apache Airflow.
- **Dockerized Environment**: Easily deployable and reproducible setup using Docker.
- **Format Exports**: Save data in CSV and JSON formats for additional use cases.

---

## 🧱 Tech Stack
- **Python** – Core language used
- **Scrapy** – Web scraping framework
- **PostgreSQL** – Relational database for persistent storage
- **Apache Airflow** – Workflow orchestration and scheduling
- **Docker** – Containerization for portability
- **Power BI** *(Optional)* – For data visualization and trend analysis

---

## 🔧 Project Structure
```
├── real_estate_scraper/
│── spiders/          # Five spiders targeting different real estate sites
├── tests/                # Unit tests for spiders, pipeline, and cleaners
├── dags/             # Airflow DAGs to schedule monthly spider runs
├── docker/               # Dockerfiles and docker-compose for local orchestration
├── items.py          # Data structure definitions
├── pipelines.py      # PostgreSQL saving logic
├── settings.py       # Scrapy configurations
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works
1. **Spiders** collect listing details (price, location, size, type, amenities).
2. **Data cleaning functions** normalize currency, square footage, and missing fields.
3. **Pipeline** sends clean data into PostgreSQL.
4. **Airflow DAGs** run spiders once a month.
5. **Docker** ensures the whole environment can run anywhere.

---

## 🧪 Running Locally

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/real_estate_scraper.git
cd real_estate_scraper
```

### 2. Run a Spider (without Docker)
```bash
scrapy crawl london  # or paris, berlin, etc.
```

### 3. Export to CSV or JSON
```bash
scrapy crawl london -o output.csv
scrapy crawl london -o output.json
```

---

## 🐳 Running with Docker
Once Docker support is fully added:

### 1. Build the Image
```bash
docker build -t real-estate-scraper .
```

### 2. Run a Spider
```bash
docker run -it real-estate-scraper scrapy crawl london
```

### 3. With Docker Compose (Airflow + Scraper)
```bash
docker-compose up
```
> This will bring up Airflow, PostgreSQL, and your spiders for scheduling.

---

## 🗃️ PostgreSQL Setup
Update your connection info in `settings.py`:
```python
POSTGRES_HOST = 'localhost'
POSTGRES_DB = 'realestate'
POSTGRES_USER = 'user'
POSTGRES_PASSWORD = 'password'
```
The pipeline will automatically create the table `real_estate` if it doesn't exist.

---

## 📅 Airflow DAGs
DAGs are stored in `airflow/dags/`. They:
- Trigger all spiders once a month.
- Include logging and health check notifications.

To test:
```bash
cd airflow
airflow standalone
```
Then open Airflow UI at [http://localhost:8080](http://localhost:8080)

---

## 🧪 Testing
```bash
python -m unittest discover tests
```
Includes unit tests for:
- Data cleaning functions
- PostgreSQL pipeline
- Individual spider logic and fallback behavior

---

## 📈 Potential Use Cases
- Price trend analysis by city or property type
- Size vs price correlation
- Feature impact (amenities, location)
- Budget vs luxury classification

---

## 🔮 Future Improvements
- Add property image URLs and geolocation data
- Validate and deduplicate listings
- Integrate Power BI dashboard
- Add predictive price modeling

---

## 📄 License
Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Note:** Please respect each website's `robots.txt` and terms of service when using this scraper.


