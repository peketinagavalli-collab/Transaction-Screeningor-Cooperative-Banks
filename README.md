# AI-Based Suspicious Transaction Screening System for Cooperative Banks
### Academic Capstone Project (DBMS, DMGT, ADSA, OOPJ, Python)

---

## 📌 Project Overview
A cooperative bank currently has no automated first-level screening system for suspicious transfers and high-value cash withdrawals before transactions reach manual review. This academic prototype builds an automated multi-modal screening system combining:
1. **DMGT Propositional Logic** (Atomic propositions $A, N, Z, G$ and compound rules)
2. **Python Statistical Anomaly Detection** (Gaussian Mean $\mu$, Standard Deviation $\sigma$, and Z-score $z$)
3. **ADSA Directed Weighted Graphs** (NetworkX account networks, hub centrality, degree distribution)
4. **DBMS Relational Database & SQL** (MySQL / SQLite dual engine, ER modeling, foreign key constraints, aggregations)
5. **OOPJ Object-Oriented Design** (Encapsulated entity classes, services, and cryptographic SHA-256 OTP management)
6. **Section 19: Large Cash Withdrawal & Simulated 2FA OTP Verification** (Customer-specific historical baseline deviation analysis with virtual mobile SMS authorization)

> **⚠️ Academic Disclaimer:**  
> This system is an academic prototype for first-level transaction screening. It does not determine whether a transaction is actually fraudulent. Decision classifications (*Normal*, *Review Required*, *Suspicious*) indicate the level of recommended manual verification by bank officers.

---

## 🎓 Academic Subject Mapping

| Subject | Core Theory | Implementation in Project |
| :--- | :--- | :--- |
| **1. DBMS** | Relational Schemas, Constraints, Normalization, SQL Aggregates & Joins | `database/schema.sql`, `database/queries.sql`, `database/db_connection.py`, `pages/08_🗄️_DBMS_ER_and_SQL.py` |
| **2. DMGT** | Propositional Logic ($A, N, Z, G$), Truth Tables, Binary Relations ($R_1, R_2, R_3$), Set Theory | `services/rule_engine.py`, `pages/07_📐_DMGT_Logic_Relations.py` |
| **3. ADSA** | Directed Weighted Graphs $\mathcal{G}=(\mathcal{V},\mathcal{E},\mathcal{W})$, Degree Centrality, Hub Detection | `services/graph_analyzer.py`, `pages/05_🕸️_Transaction_Network.py` |
| **4. OOPJ** | Encapsulation, Properties, Constructors, Multi-Service Composition, Security Hashing | `models/*.py`, `services/*.py` |
| **5. Python** | Descriptive Statistics ($\mu, \sigma, z$), Data Processing with Pandas/NumPy, Streamlit UI | `services/anomaly_detector.py`, `app.py`, `pages/*.py` |

---

## 🚀 Quick Start & Windows Setup

### Step 1: Clone or Open Workspace
Open a PowerShell terminal in the project directory:
```powershell
cd "c:\Users\CFIN\Transaction Screening for Cooperative Banks\Transaction Screening for Cooperative Banks"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Unit Tests
```powershell
python -m unittest discover tests
```

### Step 4: Launch Streamlit Application
```powershell
streamlit run app.py
```
The application will launch in your browser at `http://localhost:8501`.

---

## 🗄️ Database Setup (MySQL & SQLite)

### Automatic Mode (Zero-Config SQLite)
By default, the system runs with a self-contained, zero-configuration local SQLite database (`database/coop_bank.db`). It automatically boots tables and seeds sample data upon first run.

### Optional MySQL Server Configuration
If you have a MySQL server installed and wish to run directly against MySQL:
1. Open MySQL Workbench or Command Line.
2. Create the database:
   ```sql
   CREATE DATABASE coop_bank_screening;
   ```
3. Execute the schema script:
   ```powershell
   mysql -u root -p coop_bank_screening < database/schema.sql
   ```
4. Update your `.env` file:
   ```ini
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=coop_bank_screening
   ```
5. Initialize data:
   ```powershell
   python database/init_db.py
   ```

---

## 📐 Propositional Logic & Formulas

### Atomic Propositions:
- **$A$ (Amount Exceeds Threshold):** $x \ge \text{Threshold}$ (default: ₹50,000)
- **$N$ (Payee is New):** First transfer between source account and payee
- **$Z$ (Statistical Anomaly):** $|z| = \left|\frac{x - \mu}{\sigma}\right| \ge 3.0$
- **$G$ (Graph Risk):** $\text{Graph Risk Indicator} \ge 0.5$

### Compound Rules:
- **Rule 1:** $A \land N \implies \text{Review Required}$
- **Rule 2:** $A \land N \land Z \implies \text{Suspicious}$
- **Rule 3:** $Z \land G \implies \text{Review Required}$
- **Rule 4:** $A \land N \land Z \land G \implies \text{Suspicious}$

### Multi-Signal Risk Score:
$$\text{RiskScore} = w_1(\text{RuleRisk}) + w_2(\text{StatisticalRisk}) + w_3(\text{GraphRisk}) + w_4(\text{PatternRisk})$$
- Default Weights: $w_1 = 30\%, w_2 = 30\%, w_3 = 20\%, w_4 = 20\%$
- Decision Bands: **Normal** ($0 - 39$), **Review Required** ($40 - 69$), **Suspicious** ($70 - 100$).

---

## 💵 Section 19: Large Cash Withdrawal + OTP Verification
- Calculates individual customer withdrawal mean $\mu_{\text{cust}}$ and customer-specific Z-score $z_{\text{cust}}$.
- If withdrawal $\ge ₹50,000$: Prompts for simulated 2FA OTP verification.
- Virtual phone notification displays simulated 6-digit OTP.
- Verifies SHA-256 hash in `OTP_VERIFICATION` table.
- Output clearly distinguishes between authentication verification and screening surveillance risk.
