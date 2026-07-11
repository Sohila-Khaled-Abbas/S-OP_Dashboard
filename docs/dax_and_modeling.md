# 🧮 DAX Calculation & Modeling Standards

This guide outlines modeling best practices and DAX measure patterns for the Omnichannel Sales & Operations (S&OP) project. It serves as a reference for developers adding or modifying measures.

---

## 🏗️ Modeling Guidelines

1.  **Star Schema Layout:** Maintain a strict separation of dimensions and facts.
    *   **Dimension Tables (Prefix: `Dim`):** Contain descriptive attributes. Filtering should propagate *down* from dimensions to facts (One-to-Many).
    *   **Fact Tables (Prefix: `Fact`):** Contain numeric metrics and keys. Avoid placing textual descriptors here.
2.  **Date Relationships:**
    *   [`FactSales`](../S&OP_Dashboard.SemanticModel/definition/tables/FactSales.tmdl) and [`FactOrderFulfillment`](../S&OP_Dashboard.SemanticModel/definition/tables/FactOrderFulfillment.tmdl) link to `DimDate[Date]`.
    *   `FactSales` uses an **active** relationship with `OrderDate`.
    *   `FactOrderFulfillment` uses an **active** relationship with `OrderDate` and **inactive** relationships with `DeliveryDate`, `ShipDate`, `PayDate`, and `InvoiceDate`. To use inactive dates, activate them in DAX via:
        ```dax
        Fulfillments by Delivery Date = 
        CALCULATE(
            COUNT(FactOrderFulfillment[FulfillmentID]),
            USERELATIONSHIP(FactOrderFulfillment[DeliveryDate], DimDate[Date])
        )
        ```

---

## 📐 Standard DAX Measure Calculations

Below are the standard calculations recommended/planned for the S&OP dashboard:

### 1. Sales Performance Measures

#### Total Sales
```dax
Total Sales = SUM(FactSales[LineTotal])
```
*   **Format:** Currency `$#,##0`

#### Sales Target
```dax
Sales Target = SUM(FactSalesTargets[TargetAmount])
```
*   **Format:** Currency `$#,##0`

#### Sales Variance vs Target
```dax
Sales Variance vs Target = [Total Sales] - [Sales Target]
```
*   **Format:** Currency `$#,##0;($#,##0);"-"`

#### Sales Variance %
```dax
Sales Variance % = 
DIVIDE(
    [Sales Variance vs Target],
    [Sales Target],
    BLANK()
)
```
*   **Format:** Percentage `0.0%`

---

### 2. Supply & Inventory Measures

#### Total Inventory Quantity
```dax
Total Stock Quantity = SUM(FactInventory[Quantity])
```
*   **Format:** Decimal Number `#,##0`

#### Days of Inventory Cover
Estimates how many days the current stock will last based on average daily sales over the last 30 days:
```dax
Average Daily Sales (Last 30d) = 
CALCULATE(
    DIVIDE(SUM(FactSales[Quantity]), 30),
    DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -30, DAY)
)

Days of Inventory Cover = 
DIVIDE(
    [Total Stock Quantity],
    [Average Daily Sales (Last 30d)],
    BLANK()
)
```
*   **Format:** Decimal Number `0.0`

---

### 3. Fulfillment & Logistics Measures

#### On-Time In-Full (OTIF) %
Tracks shipments delivered on or before the planned date without shortages:
```dax
Total Deliveries = COUNT(FactOrderFulfillment[FulfillmentID])

OTIF Deliveries = 
CALCULATE(
    [Total Deliveries],
    DimOrderFlags[FulfillmentStatus] = "On-Time In-Full"
)

OTIF % = 
DIVIDE(
    [OTIF Deliveries],
    [Total Deliveries],
    0
)
```
*   **Format:** Percentage `0.0%`

---

### 4. Marketing Campaign ROI

#### Campaign ROI %
```dax
Total Campaign Spend = SUM(FactCampaignSpend[SpendAmount])

Campaign ROI % = 
DIVIDE(
    [Total Sales] - [Total Campaign Spend],
    [Total Campaign Spend],
    BLANK()
)
```
*   **Format:** Percentage `0.0%`
