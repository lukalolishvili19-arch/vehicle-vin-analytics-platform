# PyCharm — ნაშრომის დემონსტრაცია (Python)

> კი, პროექტში **რეალურად Python** გამოიყენება. PyCharm არის სწორი არჩევანი კოდის ჩვენებისთვის.

---

## 1. პროექტის გახსნა

**File → Open** → აირჩიე:

```
C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform
```

PyCharm Professional: იგივე პროექტში ჩანს **Database** (DataGrip-ის კავშირი უკვე `.idea/dataSources.xml`-შია).

---

## 2. Python Interpreter

**File → Settings → Project → Python Interpreter**

| ვარიანტი | გზა |
|----------|-----|
| **რეკომენდებული** | პროექტის `.venv\Scripts\python.exe` (Python 3.12) |
| **ალტერნატივა** | `C:\msys64\ucrt64\bin\python.exe` |

> ⚠️ Windows-ზე გზა არის **`.venv\Scripts\python.exe`**, არა `.venv\bin\python` (ეს Linux/Mac-ია).

---

## 3. Run Configurations (უკვე მზადაა)

ზედა მენიუში **Run** dropdown:

| კონფიგურაცია | რას აკეთებს |
|--------------|-------------|
| **ETL Stdlib** | CSV → Bronze/Silver/Gold + Power BI export |
| **Load MySQL** | Gold CSV → MySQL (555 row) |
| **Excel Workbook** | `vehicle_analytics.xlsx` |
| **ETL Full** | `python -m etl` (pandas საჭიროა) |

დემოზე: აირჩიე **ETL Stdlib** → **Run** → ტერმინალში ჩანს `rows_valid: 555`.

---

## 4. რა ფაილები აჩვენო ნაშრომში (Python კოდი)

### ETL Pipeline (მთავარი)

```
etl/
├── extract/csv_extractor.py      # წაკითხვა
├── validate/rules.py             # VIN, grade, mileage ვალიდაცია
├── validate/vin.py               # VIN ფორმატი
├── transform/medallion.py        # Bronze → Silver → Gold
├── load/mysql_client.py          # MySQL ჩატვირთვა
└── pipeline/runner.py            # ორკესტრაცია
```

### სკრიპტები (გაშვება PyCharm-დან)

```
scripts/run_etl_stdlib.py         # Medallion ETL (stdlib)
scripts/load_mysql_stdlib.py      # MySQL load
excel/generate_workbook_stdlib.py # Excel
```

### ტესტები

```
tests/unit/test_etl_validation.py
tests/unit/test_vin_validator.py
```

**Run → Run 'pytest in tests'** ან ტესტის გვერდით **▶**.

---

## 5. ნაშრომის დემო სცენარი (10 წუთი)

```
1. PyCharm  → ETL Stdlib Run     → "555 rows_valid"
2. PyCharm  → ფაილები: etl/transform/medallion.py, validate/vin.py
3. PyCharm  → Database panel   → SELECT COUNT(*) FROM fct_vehicle_inventory → 555
4. Excel      → vehicle_analytics.xlsx (KPI ფურცელი)
5. Power BI   → VIN_Analytics.pbix (დეშბორდი)
```

**ამბავი ერთ წინადადებაში:**

> „Python ETL-ით CSV მონაცემები გადავიყვანე Medallion არქიტექტურაში, MySQL star schema-ში ჩავტვირთე და Power BI / Excel-ით ვიზუალიზაცია შევქმენი.“

---

## 6. რა არის Python vs სხვა ხელსაწყო

| ხელსაწყო | როლი |
|----------|------|
| **PyCharm + Python** | ETL, ვალიდაცია, ტრანსფორმაცია, Excel გენერაცია |
| **DataGrip / PyCharm DB** | SQL, სქემა, ანალიტიკური მოთხოვნები |
| **Power BI** | ინტერაქტიული დეშბორდი |
| **Excel** | ანგარიში / pivot-ებისთვის |

Power BI-ში Python **არ** ჩანს — ამიტომ ნაშრომში PyCharm აუცილებელია Python ნაწილის ჩვენებისთვის.

---

## 7. სასარგებლო პანელები PyCharm-ში

- **Project** — ფოლდერების ხე
- **Run** — სკრიპტის გაშვება
- **Database** — MySQL `vehicle_analytics`
- **Terminal** — `docker compose up -d`

---

## 8. პრობლემები

| პრობლემა | გამოსავალი |
|----------|------------|
| `No module named pandas` | გამოიყენე **ETL Stdlib** ან დააინსტალირე `pip install -r requirements.txt` |
| MySQL connection refused | `docker start vehicle_analytics_mysql` |
| Interpreter არ ჩანს | Settings → Add → `C:\msys64\ucrt64\bin\python.exe` |
