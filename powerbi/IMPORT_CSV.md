# CSV Import — Power BI Desktop

## ⚠️ მნიშვნელოვანი

`VIN_Analytics.pbids` = **MySQL** კავშირი (არა CSV).

CSV-სთვის **pbids არ გამოიყენო**. გააკეთე ასე:

---

## ნაბიჯები

1. გახსენი **Power BI Desktop** (ცარიელი report)
2. **Home** → **Get data** → **Text/CSV**
3. აირჩიე ფაილი:

```
C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform\powerbi\data\fct_vehicle_inventory.csv
```

4. Preview-ში უნდა ჩანდეს **555 rows**, **29 columns**
5. **Load** (ან Transform Data → ტიპები → Close & Apply)

---

## თუ ფაილი არ ჩანს Browse-ში

File type dropdown: **All files (*.*)** ან **Text Files (*.txt; *.csv)**

---

## თუ preview ცარიელია

გაუშვი ექსპორტი თავიდან:

```powershell
C:\msys64\ucrt64\bin\python.exe scripts\run_etl_stdlib.py
```
