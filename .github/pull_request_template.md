## 📝 Description
Please include a summary of the changes and the business problem they solve.

*   **Target Page(s):** `[Specify report pages changed, e.g. Inventory Overview, Sales Performance]`
*   **DAX Measures added/modified:**
    > [!NOTE]
    > List any new calculations or modifications to existing DAX measures below.
    *   `[Measure Name]`: Describe calculation logic and goal.
*   **Data Model & Relationships:**
    *   `[e.g., Added relationship DimCustomer[CustomerID] -> FactSales[CustomerID]]`

---

## 🚀 Type of Change
*Check all that apply:*

| Category | Type of Change | Description |
| :---: | :--- | :--- |
| 📊 | **New Visual / Page Layout** | Adding or styling visual cards, slicers, charts, and grids. |
| 🧮 | **DAX Measure Addition / Edit** | Writing new calculations, KPI metrics, or time intelligence. |
| 🔧 | **Power Query (M) Script** | Modifying queries, parameter adjustments, or data types. |
| 🕸️ | **Model Schema Modification** | Adjusting relationships, cross-filtering, or tables. |
| 🐛 | **Bug Fix** | Resolving bugs, wrong calculation totals, or visual errors. |
| 🧹 | **TMDL Refactor** | Code formatting, table description updates, cleaning model. |

---

## 🧪 Verification & Testing Checklist

- [ ] **DAX Formulas Verified:** Logic has been verified against raw inputs or SQL staging checks.
- [ ] **Performance Analyzer Checked:** Visuals load in under 1 second. No rendering lags detected.
- [ ] **Formatting & Theme Compliance:** Visuals conform to the project color palette and are aligned perfectly.
- [ ] **Row-Level Security (RLS) Tested:** RLS configurations were validated using "View as..." and work as intended.
- [ ] **Tooltips & Cross-filtering Checked:** Hover-overs and interactions work properly across cards and charts.

---

## 📷 Screenshots / Visual Demos

Please provide visual proof of changes in the Power BI Desktop layout.

| Before Change | After Change |
| :--- | :--- |
| *Insert screenshot / GIF here* | *Insert screenshot / GIF here* |

---

> [!IMPORTANT]
> **Pre-merge Checklist:**
> 1. Verified that local cache files (`cache.abf`) are not staged for commit.
> 2. Verified that local settings (`localSettings.json`) are not staged for commit.
> 3. Ran TMDL code reviews for formatting and naming conventions.
