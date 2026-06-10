# GitHub-ზე ატვირთვა — ნაბიჯ-ნაბიჯ (ქართულად)

## 0. Git დაინსტალირე (ერთხელ)

1. გადადი: https://git-scm.com/download/win
2. დააინსტალირე (Next → Next, default OK)
3. **PowerShell/Cursor/PyCharm დახურე და თავიდან გახსენი**

შემოწმება:
```powershell
git --version
```

---

## 1. GitHub-ზე ახალი რეპო

1. https://github.com/new
2. **Repository name:** `vehicle-vin-analytics-platform` (ან სხვა)
3. **Public**
4. ❌ **Add README** — არ ჩართო (პროექტში უკვე არის)
5. **Create repository**

---

## 2. პროექტის ატვირთვა (Terminal)

```powershell
cd "C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform"

git init
git branch -M main
git add .
git status
```

`git status`-ში **არ უნდა** ჩანდეს `.env` — ის `.gitignore`-შია.

```powershell
git commit -m "feat: VIN analytics platform — Python ETL, MySQL, Power BI docs"
```

---

## 3. GitHub-თან დაკავშირება

შეცვალე `YOUR_USERNAME` შენი GitHub username-ით:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/vehicle-vin-analytics-platform.git
git push -u origin main
```

Browser გაიხსნება → GitHub login → authorize.

---

## 4. ან ერთი სკრიპტით

Git დაყენების შემდეგ:

```powershell
cd "C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform"
.\scripts\push_to_github.ps1 -GitHubUsername YOUR_USERNAME
```

---

## რა ავიდა / არ ავიდა Git-ზე

| ✅ ავიდა | ❌ არ ავიდა |
|---------|------------|
| `etl/`, `scripts/`, `sql/` | `.env` (პაროლები) |
| `powerbi/` (DAX, MD, CSV) | `.venv/` |
| `docs/screenshots/pycharm_*.png` | `docs/screenshots/pbi_*.png` |
| `docs/screenshots/datagrip_*.png` | `*.pbix` |
| `README.md`, `docker-compose.yml` | `data/raw/*.csv`, gold layers |

---

## პრობლემები

| შეცდომა | გამოსავალი |
|---------|------------|
| `git is not recognized` | Git დააინსტალირე, terminal გადატვირთე |
| `failed to push` / auth | GitHub → Settings → Developer settings → Personal access token |
| `remote origin already exists` | `git remote set-url origin https://github.com/USER/REPO.git` |

---

## Repository description (GitHub About)

```
BMW auction VIN inventory → Python ETL (Medallion) → MySQL star schema → Power BI / Excel analytics. Portfolio data engineering project.
```

**Topics:** `data-engineering` `python` `mysql` `etl` `power-bi` `docker` `automotive`
