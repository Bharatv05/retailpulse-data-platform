<h1 align="center"><b style="color: #2E86C1;">RetailPulse Data Platform</b></h1>

<p align="center">
  <i>An end-to-end <b style="color: #E67E22;">Data Engineering</b> project simulating a production-style e-commerce data platform.</i>
</p>

---

## 🎯 <b style="color: #8E44AD;">Project Goal</b>
Build an end-to-end data platform that progressively evolves from a local <b style="color: #F39C12;">Python</b> + <b style="color: #336699;">PostgreSQL</b> ETL pipeline into a robust, production-style data engineering architecture.

## 🛠️ <b style="color: #27AE60;">Technology Stack</b>
*   <b style="color: #3776AB;">Python</b> (Core processing & pipelining)
*   <b style="color: #336791;">PostgreSQL</b> (Relational database & storage)
*   <b style="color: #F2CA27;">SQL</b> (Transformations & querying)
*   <b style="color: #150458;">Pandas</b> (Data manipulation)
*   <b style="color: #F05032;">Git</b> (Version control)

## 🏗️ <b style="color: #D35400;">Architecture Roadmap</b>

### Current State (Phase 1)
<b style="color: #3776AB;">Python Application</b> ➔ <b style="color: #336791;">PostgreSQL Database</b>

### Future State (Medallion Architecture)
`Source Systems` ➔ `Data Ingestion` ➔ `<b style="color: #CD7F32;">Bronze (Raw)</b>` ➔ `<b style="color: #C0C0C0;">Silver (Cleaned)</b>` ➔ `<b style="color: #FFD700;">Gold (Aggregated)</b>` ➔ `Data Warehouse` ➔ `Analytics / BI`

---

## 🚀 <b style="color: #2980B9;">Current Phase: Phase 1 — Environment & Developer Setup</b>
**Status:** <b style="color: #27AE60;">Completed ✅</b>

### ⚙️ <b style="color: #C0392B;">Local Setup Instructions</b>

#### 1. Prerequisites
Ensure you have the following installed and running on your local machine:
*   **Python 3.8+**
*   **PostgreSQL**

#### 2. Environment Configuration
It is highly recommended to isolate your dependencies using a virtual environment. Run the following commands in your project root terminal:

**Create the Virtual Environment:**
```bash
python -m venv .venv
```

**Activate the Environment:**
*Windows (Command Prompt):*
```cmd
.venv\Scriptsctivate.bat
```
*Windows (PowerShell):*
```powershell
.venv\Scriptsctivate.ps1
```

**Install Required Dependencies:**
```bash
pip install -r requirements.txt
```

#### 3. Database Configuration
Create a `.env` file in your root directory. You can use `.env.example` as a template structure. 

Your `.env` file must contain your PostgreSQL connection details:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_NAME=retailpulse
```
> ⚠️ **Important:** Ensure you have manually created a database named <b style="color: #16A085;">retailpulse</b> in your local PostgreSQL instance before proceeding.

#### 4. Connection Validation
After configuring the `.env` file, test your database connection by executing the database test script:

```bash
python src/retailpulse/db_test.py
```

✅ **Success Criteria:** 
If configured correctly, the terminal should output your PostgreSQL version details, similar to:
`PostgreSQL 18.4 on x86_64-windows, compiled by ***********, 64-bit`

Once you see this success message, your environment is ready to go! 🎉
