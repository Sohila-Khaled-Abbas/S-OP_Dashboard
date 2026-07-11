# 🧮 DAX Calculation, Modeling & RLS Standards

This guide outlines modeling best practices, row-level security (RLS), and advanced DAX measure patterns implemented for the Omnichannel Sales & Operations (S&OP) project.

---

## 🏗️ Modeling & Star Schema Layout

Our semantic model enforces a strict separation between dimension and fact tables to ensure optimal performance, clear filter propagation, and maintainability.

1. **Dimension Tables (Prefix: `Dim`)**: Contain descriptive and filtering attributes (e.g., `DimCustomer`, `DimProduct`, `DimDate`, `DimGeo`, `DimCampaign`, `DimOrderFlags`). Filtering propagates **down** from dimensions to facts (One-to-Many).
2. **Fact Tables (Prefix: `Fact`)**: Contain numeric transactions, measures, and keys (e.g., `FactSales`, `FactInventory`, `FactOrderFulfillment`, `FactSalesTargets`, `FactCampaignSpend`, `FactPromotionCoverage`).
3. **Disconnected Security Table (`Security`)**: Used for dynamic security mapping. Physical relationships are omitted to prevent many-to-many filter chains and ambiguity.

---

## 🔒 Row-Level Security (RLS) Architecture

Security is enforced dynamically using the **Disconnected Security Table** pattern combined with active relationships from dimensions to facts.

### 👥 Defined Roles

*   **`Regional Sales Rep`**: Restricts customer and geo attributes based on the logged-in user's assigned region.
*   **`Executive`**: Unfiltered access across all regions for senior leadership.
*   **`Admin`**: Unfiltered access with model definition modification rights.

### 📐 RLS DAX Implementation
The `Regional Sales Rep` role filters `DimCustomer` and `DimGeo` using the `LOOKUPVALUE` function against the disconnected `Security` table:

```dax
// DimCustomer Table Filter Expression:
[Region] = LOOKUPVALUE(Security[Region], Security[UserEmail], USERPRINCIPALNAME())

// DimGeo Table Filter Expression:
[Region] = LOOKUPVALUE(Security[Region], Security[UserEmail], USERPRINCIPALNAME())
```

Once dimensions are filtered, the filters naturally flow downstream to `FactSales` (via `CustomerID` and `BillToCityKey` / `ShipToCityKey` respectively), securing all metrics in report visuals.

---

## 📐 KeyMeasures Catalog (28 Core Measures)

All measures are consolidated inside the `KeyMeasures` table (renamed from `Measures` to avoid reserved keyword conflicts) and categorized into clear display folders.

### 1. Sales Performance (`01_Sales Performance`)

*   **Total Sales**
    ```dax
    Total Sales = SUM(FactSales[LineTotal])
    ```
    *Format:* Currency `$#,##0.00`
*   **Total Quantity Sold**
    ```dax
    Total Quantity Sold = SUM(FactSales[Quantity])
    ```
    *Format:* Decimal `#,##0`
*   **Sales Target**
    ```dax
    Sales Target = SUM(FactSalesTargets[TargetAmount])
    ```
    *Format:* Currency `$#,##0.00`
*   **Sales Variance**
    ```dax
    Sales Variance = [Total Sales] - [Sales Target]
    ```
    *Format:* Currency `$#,##0.00;($#,##0.00);"-"`
*   **Sales Variance %**
    ```dax
    Sales Variance % = DIVIDE([Sales Variance], [Sales Target], BLANK())
    ```
    *Format:* Percentage `0.0%`
*   **Sales YTD** (Year-to-Date)
    ```dax
    Sales YTD = CALCULATE([Total Sales], DATESYTD(DimDate[Date]))
    ```
*   **Sales PYTD** (Prior Year-to-Date)
    ```dax
    Sales PYTD = CALCULATE([Total Sales], DATESYTD(SAMEPERIODLASTYEAR(DimDate[Date])))
    ```
*   **Sales YoY Growth %**
    ```dax
    Sales YoY Growth % = DIVIDE([Sales YTD] - [Sales PYTD], [Sales PYTD], BLANK())
    ```
*   **Sales MoM Growth %**
    ```dax
    Sales MoM Growth % = 
    VAR _CurrentMonth = [Total Sales]
    VAR _PreviousMonth = CALCULATE([Total Sales], DATEADD(DimDate[Date], -1, MONTH))
    RETURN DIVIDE(_CurrentMonth - _PreviousMonth, _PreviousMonth, BLANK())
    ```
*   **Avg Order Value (AOV)**
    ```dax
    Avg Order Value = DIVIDE([Total Sales], DISTINCTCOUNT(FactSales[OrderID]), BLANK())
    ```

### 2. Profitability (`02_Profitability`)

*   **Total COGS**
    ```dax
    Total COGS = SUM(FactSales[COGS])
    ```
*   **Gross Profit**
    ```dax
    Gross Profit = [Total Sales] - [Total COGS]
    ```
*   **Gross Margin %**
    ```dax
    Gross Margin % = DIVIDE([Gross Profit], [Total Sales], BLANK())
    ```

### 3. Supply & Inventory (`03_Supply & Inventory`)

*   **Total Stock Units**
    ```dax
    Total Stock Units = SUM(FactInventory[Units])
    ```
*   **Avg Daily Sales (30d)**
    ```dax
    Avg Daily Sales (30d) = 
    CALCULATE(
        DIVIDE([Total Quantity Sold], 30),
        DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -30, DAY)
    )
    ```
*   **Days of Inventory Cover**
    ```dax
    Days of Inventory Cover = DIVIDE([Total Stock Units], [Avg Daily Sales (30d)], BLANK())
    ```
    *Format:* `#,##0.0 "days"`

### 4. Fulfillment & Logistics (`04_Fulfillment & Logistics`)

*   **Total Orders**
    ```dax
    Total Orders = DISTINCTCOUNT(FactOrderFulfillment[OrderID])
    ```
*   **On-Time Deliveries** (Delivered within 7 days of ship date)
    ```dax
    On-Time Deliveries = CALCULATE([Total Orders], FactOrderFulfillment[DeliveryDate] <= FactOrderFulfillment[ShipDate] + 7)
    ```
*   **OTIF %** (On-Time In-Full)
    ```dax
    OTIF % = DIVIDE([On-Time Deliveries], [Total Orders], BLANK())
    ```
*   **Avg Lead Time (Days)**
    ```dax
    Avg Lead Time (Days) = AVERAGEX(FactOrderFulfillment, DATEDIFF(FactOrderFulfillment[OrderDate], FactOrderFulfillment[DeliveryDate], DAY))
    ```
*   **Avg Ship-to-Delivery (Days)**
    ```dax
    Avg Ship-to-Delivery (Days) = AVERAGEX(FactOrderFulfillment, DATEDIFF(FactOrderFulfillment[ShipDate], FactOrderFulfillment[DeliveryDate], DAY))
    ```

### 5. Marketing & Campaigns (`05_Marketing & Campaigns`)

*   **Total Campaign Spend**
    ```dax
    Total Campaign Spend = SUM(FactCampaignSpend[SpendAmount])
    ```
*   **Marketing ROI**
    ```dax
    Marketing ROI = DIVIDE([Total Sales], [Total Campaign Spend], BLANK())
    ```
    *Format:* `#,##0.00"x"`
*   **Revenue per Campaign $**
    ```dax
    Revenue per Campaign $ = DIVIDE([Total Sales], DISTINCTCOUNT(FactCampaignSpend[CampaignKey]), BLANK())
    ```

### 6. Customer Analytics (`06_Customer Analytics`)

*   **Total Customers**
    ```dax
    Total Customers = DISTINCTCOUNT(FactSales[CustomerID])
    ```
*   **Sales per Customer**
    ```dax
    Sales per Customer = DIVIDE([Total Sales], [Total Customers], BLANK())
    ```
*   **Repeat Customer Rate %**
    ```dax
    Repeat Customer Rate % = 
    VAR _RepeatCustomers = 
        COUNTROWS(
            FILTER(
                ADDCOLUMNS(
                    VALUES(FactSales[CustomerID]),
                    "OrderCount", CALCULATE(DISTINCTCOUNT(FactSales[OrderID]))
                ),
                [OrderCount] > 1
            )
        )
    RETURN DIVIDE(_RepeatCustomers, [Total Customers], BLANK())
    ```

### 7. Dynamic & Context (`07_Dynamic & Context`)

*   **Selected Period Sales** (Ignores date filters inside visual context)
    ```dax
    Selected Period Sales = CALCULATE([Total Sales], ALLSELECTED(DimDate))
    ```
*   **Running Total Sales**
    ```dax
    Running Total Sales = CALCULATE([Total Sales], FILTER(ALL(DimDate[Date]), DimDate[Date] <= MAX(DimDate[Date])))
    ```
*   **Sales Rolling 3M**
    ```dax
    Sales Rolling 3M = CALCULATE([Total Sales], DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -3, MONTH))
    ```
