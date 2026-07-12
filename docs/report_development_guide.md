# 📊 Report & Visualization Phase Design Guide

This guide outlines the layout, visual hierarchy, and recommended report pages for the **Omnichannel Sales & Operations (S&OP) Dashboard** in Power BI, utilizing the newly created `KeyMeasures` table.

---

## 🎨 Design System & Theme Settings

A custom Power BI theme file has been created to enforce a consistent, modern corporate design (glassmorphism/sleek light hybrid) across the entire report.

### Theme File Location

**`StaticResources/SharedResources/BaseThemes/SOPTheme.json`**

### How to Import

1. Open Power BI Desktop.
2. Go to **View** → **Themes** → **Browse for themes...**
3. Navigate to the `S&OP_Dashboard.Report/StaticResources/SharedResources/BaseThemes/` folder and select **`SOPTheme.json`**.
4. The theme will apply globally to all pages and visuals.

> **Note:** The theme file is checked into version control alongside the report definition. If you update the theme, re-import it to refresh the report's styling. All team members should use the same theme file to maintain consistency.

### Theme Specification Summary

The `SOPTheme.json` defines the following design tokens:

* **Primary Font:** `Segoe UI` (with `Segoe UI Semibold` for titles/headers)
* **Data Colors Palette:**
  * 🔵 **Navy Blue (#1E3A8A) & Blue (#3B82F6):** Primary KPIs, Dimensions, and Active Flows.
  * 🟣 **Purple (#7C3AED) & Lavender (#A78BFA):** Fact tables, forecasts, and target variations.
  * 🟢 **Emerald Green (#10B981):** Successful indicators, OTIF, and Stock within safety bounds.
  * 🟡 **Amber (#F59E0B):** Warning thresholds and mid-range alerts.
  * 🔴 **Crimson Red (#EF4444):** Exception flags, delayed shipments, and budget deficits.
  * ⚪ **Slate (#64748B):** Secondary descriptions and gridlines.
* **Page Background:** Light gray (`#F9FAFB`) — subtle contrast from pure white.
* **Visual Style:**
  * White card backgrounds (`#FFFFFF`)
  * Rounded borders (8px radius) with light gray (`#E5E7EB`) borders
  * Soft drop shadows (2px distance, 4px blur, 95% transparency) for a glassmorphism effect
  * Clean alignment with consistent padding

---

## 📑 Recommended Report Pages

### Page 1 — Executive S&OP Summary

* **Target Audience:** Senior Leadership & Executives (using `Executive` role).
* **Layout:**
  * **Top Row (KPI Cards):**
    * `Total Sales` vs. `Sales Target` (variance color-coded)
    * `Gross Margin %`
    * `OTIF %`
    * `Days of Inventory Cover`
  * **Left Column (Interactive Slicers):**
    * `DimDate[Year-Month]`
    * `DimCustomer[Segment]`
    * `DimGeo[Region]`
  * **Main Visual (Combo Line & Clustered Column Chart):**
    * **X-Axis:** `DimDate[MonthName]`
    * **Columns:** `Total Sales`
    * **Lines:** `Sales Target`
  * **Right Visual (Bar Chart):**
    * **Y-Axis:** `DimProduct[Category]`
    * **X-Axis:** `Sales Variance %` (shows which categories are beating/trailing targets)

---

### Page 2 — Demand & Customer Insights

* **Target Audience:** Sales Coordinators & Demand Planners.
* **Layout:**
  * **Top Row (KPI Cards):**
    * `Total Customers`
    * `Sales per Customer`
    * `Repeat Customer Rate %`
  * **Left Visual (Decomposition Tree):**
    * **Analyze:** `Total Sales`
    * **Explain By:** `DimCustomer[Segment]`, `DimGeo[Region]`, `DimProduct[Category]`
  * **Right Visual (Scatter Chart for Customer Segmentation):**
    * **X-Axis:** `Avg Order Value`
    * **Y-Axis:** `Total Orders` (per customer)
    * **Details:** `DimCustomer[CustomerName]`
  * **Bottom Visual (Matrix Table):**
    * **Rows:** `DimCustomer[CustomerName]`
    * **Columns:** `DimDate[Quarter]`
    * **Values:** `Total Sales`, `Sales MoM Growth %`

---

### Page 3 — Supply & Inventory Cover

* **Target Audience:** Warehouse Managers & Supply Planners.
* **Layout:**
  * **Top Row (KPI Cards):**
    * `Total Stock Units`
    * `Avg Daily Sales (30d)`
    * `Days of Inventory Cover` (Target: 30–45 days)
  * **Main Visual (Gauge Chart):**
    * **Value:** `Days of Inventory Cover`
    * **Target:** 30 (Minimum safety threshold)
  * **Middle Visual (Area Chart):**
    * **X-Axis:** `DimDate[Date]`
    * **Values:** `Total Stock Units` vs. `Running Total Sales` (helps visualize inventory depletion rates)
  * **Right Visual (Table with Conditional Formatting):**
    * **Columns:** `DimProduct[ProductName]`, `Total Stock Units`, `Days of Inventory Cover`
    * *Conditional Formatting:* Highlight cells in Red if cover is < 15 days (Stockout risk), Green if 15–45 days, and Yellow if > 45 days (Overstock risk).

---

### Page 4 — Logistics & Fulfillment

* **Target Audience:** Logistics Operations & Carrier Managers.
* **Layout:**
  * **Top Row (KPI Cards):**
    * `Total Orders`
    * `OTIF %`
    * `Avg Lead Time (Days)`
  * **Left Visual (Clustered Column Chart):**
    * **X-Axis:** `DimOrderFlags[FlagDescription]` (e.g., Damaged, Delayed Carrier, Wrong Address)
    * **Y-Axis:** `Total Orders` (helps pinpoint root cause of fulfillment failures)
  * **Right Visual (Line Chart):**
    * **X-Axis:** `DimDate[Date]`
    * **Values:** `Avg Lead Time (Days)` vs. `Avg Ship-to-Delivery (Days)` (tracks shipment efficiency over time)

---

### Page 5 — Marketing ROI & Campaigns

* **Target Audience:** Marketing Directors & Campaign Managers.
* **Layout:**
  * **Top Row (KPI Cards):**
    * `Total Campaign Spend`
    * `Marketing ROI`
    * `Revenue per Campaign $`
  * **Left Visual (Waterfall Chart):**
    * Shows the step-by-step contribution of campaigns to overall sales revenue.
  * **Right Visual (Clustered Bar Chart):**
    * **Y-Axis:** `DimCampaign[CampaignName]`
    * **X-Axis:** `Marketing ROI` (highlighting top performing campaigns)

---

## 🧪 Visual Best Practices & Optimization

1. **Leverage Inactive Date Relationships:**
   Use the inactive dates on the Logistics page by using dedicated measures like `Avg Lead Time` which internally use `USERRELATIONSHIP()` in DAX. Do not create duplicate date tables.
2. **Conditional Formatting for Insights:**
   Apply color indicators (Red/Yellow/Green) to the `Days of Inventory Cover` and `OTIF %` metrics to make exceptions instantly identifiable.
3. **Use Tooltip Pages:**
   Create a small hidden tooltip page containing a bar chart of `Sales YoY Growth %` by Category, and assign it as the hover tooltip for the main Sales visuals.
