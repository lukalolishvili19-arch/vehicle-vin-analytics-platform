# Phase 7 — Business Insights (20)

**Source:** BMW auction inventory extract, 555 vehicles, 2026-06-09  
**Note:** Insights based on **Grade**, **Mileage**, **Lights**, and **Condition Report** — price data is not in the dataset.

---

1. **SUV dominance:** X3 (92) and X5 (88) together represent **32.4%** of inventory — SUVs are the largest segment in this wholesale BMW pool.

2. **Sedan core:** 3-Series alone holds **20.7%** (115 units), making it the single largest model line despite SUV growth.

3. **Color preference:** **BLACK (35%)** and **WHITE (25%)** account for 60% of inventory — neutral colors dominate auction listings.

4. **High mileage fleet:** Average mileage is **~99,090 miles** — this is a high-mileage wholesale market, not late-model retail.

5. **Condition report gap:** **32.1%** of vehicles lack a condition report — these listings carry higher buyer risk and often lack Grade.

6. **Grade correlation:** When Grade is present, fleet average is **3.49/5.0** — slightly above mid-tier condition.

7. **Red light majority:** Among vehicles with a light assigned, **Red (238)** outnumbers **Green (117) 2:1** — more units flagged for issues than cleared.

8. **AS IS exposure:** **67 listings (12%)** contain "AS IS" in announcements — buyers assume full mechanical risk.

9. **Structural damage:** **16 vehicles (~2.9%)** explicitly mention structural damage — material for risk segmentation.

10. **Salvage / total loss:** At least **11 units** reference salvage, total loss, or rebuilt title in announcements.

11. **2-Series quality leader:** Among models with ≥5 graded units, **2-Series averages 4.07 Grade** — highest in the dataset.

12. **3-Series volume vs quality:** Largest model count (115) but **lowest avg Grade (3.15)** among top models — volume ≠ quality.

13. **X5 premium segment:** X5 averages **3.82 Grade** with **54 graded units** — strong condition in luxury SUV tier.

14. **Newest inventory skew:** Only **23 vehicles (4.1%)** are model year **2024+** — mostly older wholesale stock.

15. **Mileage anomaly flag:** **5 vehicles** show 0 or 1 mile — likely data entry placeholders requiring quarantine review.

16. **Photo completeness:** **11 listings (2%)** have zero pictures — weaker merchandising and possible stale listings.

17. **xDrive penetration:** Parsing Style shows significant **xDrive/AWD** share in 3-Series and X-models — AWD is standard in premium trims.

18. **Electric/hybrid presence:** Models **i3, i4, iX, 330e, 530e, xDrive45e** appear — small but growing PHEV/BEV footprint.

19. **INOP inventory:** **13 units** marked inoperable — immediate filter for operational buyers.

20. **VIN geographic mix:** WMI prefixes **WBA (Germany)** and **5UX (USA)** dominate — mix of import and US-built BMW units.

---

### Strategic Recommendations

- **Buyers:** Prioritize Green Light + Grade ≥ 4.0 + condition report = true.
- **Risk filter:** Exclude AS IS + structural + salvage flags for retail reconditioning.
- **Data team:** Ingest sale price from auction API to enable true market analytics.
- **Merchandising:** Flag zero-photo listings for seller follow-up.
