# 📖 Automated Data Dictionary & Model Schema

*This document is dynamically generated from the project's TMDL schemas. Do not edit directly.*

---

## 🗂️ Model Tables
- **[DimCampaign](#dimcampaign)** (Dimension) — 6 Columns, 0 Measures
- **[DimCustomer](#dimcustomer)** (Dimension) — 12 Columns, 0 Measures
- **[DimDate](#dimdate)** (Dimension) — 9 Columns, 0 Measures
- **[DimGeo](#dimgeo)** (Dimension) — 3 Columns, 0 Measures
- **[DimOrderFlags](#dimorderflags)** (Dimension) — 5 Columns, 0 Measures
- **[DimProduct](#dimproduct)** (Dimension) — 8 Columns, 0 Measures
- **[FactCampaignSpend](#factcampaignspend)** (Fact) — 5 Columns, 0 Measures
- **[FactInventory](#factinventory)** (Fact) — 3 Columns, 0 Measures
- **[FactOrderFulfillment](#factorderfulfillment)** (Fact) — 7 Columns, 0 Measures
- **[FactPromotionCoverage](#factpromotioncoverage)** (Fact) — 2 Columns, 0 Measures
- **[FactSales](#factsales)** (Fact) — 13 Columns, 0 Measures
- **[FactSalesTargets](#factsalestargets)** (Fact) — 2 Columns, 0 Measures
- **[Measures](#measures)** (Fact) — 0 Columns, 30 Measures
- **[Security](#security)** (Fact) — 2 Columns, 0 Measures

---

## 🕸️ Model Relationships
| From Table | From Column | Active Connection | To Table | To Column |
| :--- | :--- | :---: | :--- | :--- |
| `FactSales` | `FlagKey` | `──►` | `DimOrderFlags` | `FlagKey` |
| `FactSales` | `CustomerID` | `──►` | `DimCustomer` | `CustomerID` |
| `FactSales` | `ProductKey` | `──►` | `DimProduct` | `ProductKey` |
| `FactSales` | `BillToCityKey` | `──►` | `DimGeo` | `GeoKey` |
| `FactSales` | `ShipToCityKey` | `──(inactive)──►` | `DimGeo` | `GeoKey` |
| `FactInventory` | `ProductKey` | `──►` | `DimProduct` | `ProductKey` |
| `FactCampaignSpend` | `CampaignKey` | `──►` | `DimCampaign` | `CampaignKey` |
| `FactPromotionCoverage` | `CampaignKey` | `──►` | `DimCampaign` | `CampaignKey` |
| `FactPromotionCoverage` | `ProductKey` | `──►` | `DimProduct` | `ProductKey` |
| `FactOrderFulfillment` | `CustomerID` | `──►` | `DimCustomer` | `CustomerID` |
| `FactSales` | `OrderDate` | `──►` | `DimDate` | `Date` |
| `FactOrderFulfillment` | `OrderDate` | `──►` | `DimDate` | `Date` |
| `FactOrderFulfillment` | `DeliveryDate` | `──(inactive)──►` | `DimDate` | `Date` |
| `FactOrderFulfillment` | `InvoiceDate` | `──(inactive)──►` | `DimDate` | `Date` |
| `FactOrderFulfillment` | `ShipDate` | `──(inactive)──►` | `DimDate` | `Date` |
| `FactOrderFulfillment` | `PayDate` | `──(inactive)──►` | `DimDate` | `Date` |
| `FactInventory` | `YearMonth` | `──►` | `DimDate` | `Date` |
| `DimDate` | `Date` | `──►` | `FactSalesTargets` | `Period` |
| `DimCustomer` | `City` | `──(inactive)──►` | `DimGeo` | `City` |

---

## DimCampaign
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`CampaignKey`** | `int64` | `CampaignKey` | `none` | - |
| **`CampaignName`** | `string` | `CampaignName` | `none` | - |
| **`Channel`** | `string` | `Channel` | `none` | - |
| **`StartDate`** | `dateTime` | `StartDate` | `none` | - |
| **`EndDate`** | `dateTime` | `EndDate` | `none` | - |
| **`Budget`** | `int64` | `Budget` | `sum` | - |

---

## DimCustomer
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`CustomerID`** | `int64` | `CustomerID` | `none` | - |
| **`CustomerName`** | `string` | `CustomerName` | `none` | - |
| **`Segment`** | `string` | `Segment` | `none` | - |
| **`AccountManager`** | `string` | `AccountManager` | `none` | - |
| **`PaymentTerms`** | `string` | `PaymentTerms` | `none` | - |
| **`ContactName`** | `string` | `ContactName` | `none` | - |
| **`Email`** | `string` | `Email` | `none` | - |
| **`CreditLimit`** | `int64` | `CreditLimit` | `sum` | - |
| **`Phone`** | `string` | `Phone` | `none` | - |
| **`Street`** | `string` | `Street` | `none` | - |
| **`City`** | `string` | `City` | `none` | - |
| **`Region`** | `string` | `Region` | `none` | - |

---

## DimDate
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`Date`** | `dateTime` | `Date` | `none` | - |
| **`DateKey`** | `int64` | `DateKey` | `none` | - |
| **`Year`** | `int64` | `Year` | `sum` | - |
| **`QuarterNo`** | `int64` | `QuarterNo` | `sum` | - |
| **`Quarter`** | `string` | `Quarter` | `none` | - |
| **`MonthNo`** | `int64` | `MonthNo` | `sum` | - |
| **`Month`** | `string` | `Month` | `none` | - |
| **`MonthShort`** | `string` | `MonthShort` | `none` | - |
| **`Day`** | `int64` | `Day` | `sum` | - |

---

## DimGeo
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`GeoKey`** | `int64` | `GeoKey` | `none` | - |
| **`City`** | `string` | `City` | `none` | - |
| **`Region`** | `string` | `Region` | `none` | - |

---

## DimOrderFlags
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`FlagKey`** | `int64` | `FlagKey` | `none` | - |
| **`Channel`** | `string` | `Channel` | `none` | - |
| **`Status`** | `string` | `Status` | `none` | - |
| **`Priority`** | `string` | `Priority` | `none` | - |
| **`OrderChannel`** | `int64` | `OrderChannel` | `none` | - |

---

## DimProduct
*Type: `Dimension`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`ProductKey`** | `int64` | `ProductKey` | `none` | - |
| **`ProductCode`** | `string` | `ProductCode` | `none` | - |
| **`ProductName`** | `string` | `ProductName` | `none` | - |
| **`Brand`** | `string` | `Brand` | `none` | - |
| **`Category`** | `string` | `Category` | `none` | - |
| **`Subcategory`** | `string` | `Subcategory` | `none` | - |
| **`UnitPrice`** | `double` | `UnitPrice` | `sum` | - |
| **`PrimarySupplier`** | `string` | `PrimarySupplier` | `none` | - |

---

## FactCampaignSpend
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`CampaignKey`** | `int64` | `CampaignKey` | `none` | - |
| **`Date`** | `dateTime` | `Date` | `none` | - |
| **`Impressions`** | `int64` | `Impressions` | `sum` | - |
| **`Clicks`** | `int64` | `Clicks` | `sum` | - |
| **`Spend`** | `double` | `Spend` | `sum` | - |

---

## FactInventory
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`ProductKey`** | `int64` | `ProductKey` | `none` | - |
| **`YearMonth`** | `dateTime` | `YearMonth` | `none` | - |
| **`Units`** | `int64` | `Units` | `sum` | - |

---

## FactOrderFulfillment
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`OrderID`** | `string` | `OrderID` | `none` | - |
| **`CustomerID`** | `int64` | `CustomerID` | `none` | - |
| **`OrderDate`** | `dateTime` | `OrderDate` | `none` | - |
| **`ShipDate`** | `dateTime` | `ShipDate` | `none` | - |
| **`DeliveryDate`** | `dateTime` | `DeliveryDate` | `none` | - |
| **`InvoiceDate`** | `dateTime` | `InvoiceDate` | `none` | - |
| **`PayDate`** | `dateTime` | `PayDate` | `none` | - |

---

## FactPromotionCoverage
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`CampaignKey`** | `int64` | `CampaignKey` | `none` | - |
| **`ProductKey`** | `int64` | `ProductKey` | `none` | - |

---

## FactSales
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`LineID`** | `string` | `LineID` | `none` | - |
| **`OrderID`** | `string` | `OrderID` | `none` | - |
| **`Quantity`** | `int64` | `Quantity` | `sum` | - |
| **`UnitPrice`** | `double` | `UnitPrice` | `sum` | - |
| **`UnitCost`** | `double` | `UnitCost` | `sum` | - |
| **`DiscountPct`** | `double` | `DiscountPct` | `sum` | - |
| **`LineTotal`** | `double` | `LineTotal` | `sum` | - |
| **`CustomerID`** | `int64` | `CustomerID` | `none` | - |
| **`ProductKey`** | `int64` | `ProductKey` | `none` | - |
| **`FlagKey`** | `int64` | `FlagKey` | `none` | - |
| **`OrderDate`** | `dateTime` | `OrderDate` | `none` | - |
| **`ShipToCityKey`** | `int64` | `ShipToCityKey` | `count` | - |
| **`BillToCityKey`** | `int64` | `BillToCityKey` | `none` | - |

---

## FactSalesTargets
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`Period`** | `dateTime` | `Period` | `none` | - |
| **`TargetRevenue`** | `int64` | `TargetRevenue` | `sum` | - |

---

## Measures
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |

### Measures
| Measure Name | DAX Expression | Description |
| :--- | :--- | :--- |
| **`'Total Sales'`** | `SUM(FactSales[LineTotal]) formatString: \$#,##0.00 displa...` | - |
| **`'Total Quantity Sold'`** | `SUM(FactSales[Quantity]) formatString: #,##0 displayFolde...` | - |
| **`'Sales Target'`** | `SUM(FactSalesTargets[TargetAmount]) formatString: \$#,##0...` | - |
| **`'Sales Variance'`** | `[Total Sales] - [Sales Target] formatString: \$#,##0.00;(...` | - |
| **`'Sales Variance`** | `DIVIDE([Sales Variance], [Sales Target], BLANK()) formatS...` | - |
| **`'Sales YTD'`** | `CALCULATE( [Total Sales], DATESYTD(DimDate[Date]) ) forma...` | - |
| **`'Sales PYTD'`** | `CALCULATE( [Total Sales], DATESYTD(SAMEPERIODLASTYEAR(Dim...` | - |
| **`'Sales YoY Growth`** | `DIVIDE( [Sales YTD] - [Sales PYTD], [Sales PYTD], BLANK()...` | - |
| **`'Sales MoM Growth`** | `VAR _CurrentMonth = [Total Sales] VAR _PreviousMonth = CA...` | - |
| **`'Avg Order Value'`** | `DIVIDE( [Total Sales], DISTINCTCOUNT(FactSales[OrderID]),...` | - |
| **`'Total COGS'`** | `SUM(FactSales[COGS]) formatString: \$#,##0.00 displayFold...` | - |
| **`'Gross Profit'`** | `[Total Sales] - [Total COGS] formatString: \$#,##0.00 dis...` | - |
| **`'Gross Margin`** | `DIVIDE([Gross Profit], [Total Sales], BLANK()) formatStri...` | - |
| **`'Total Stock Units'`** | `SUM(FactInventory[Units]) formatString: #,##0 displayFold...` | - |
| **`'Avg Daily Sales`** | `CALCULATE( DIVIDE([Total Quantity Sold], 30), DATESINPERI...` | - |
| **`'Days of Inventory Cover'`** | `DIVIDE([Total Stock Units], [Avg Daily Sales (30d)], BLAN...` | - |
| **`'Total Orders'`** | `DISTINCTCOUNT(FactOrderFulfillment[OrderID]) formatString...` | - |
| **`'On-Time Deliveries'`** | `CALCULATE( [Total Orders], FactOrderFulfillment[DeliveryD...` | - |
| **`'OTIF`** | `DIVIDE([On-Time Deliveries], [Total Orders], BLANK()) for...` | - |
| **`'Avg Lead Time`** | `AVERAGEX( FactOrderFulfillment, DATEDIFF( FactOrderFulfil...` | - |
| **`'Avg Ship-to-Delivery`** | `AVERAGEX( FactOrderFulfillment, DATEDIFF( FactOrderFulfil...` | - |
| **`'Total Campaign Spend'`** | `SUM(FactCampaignSpend[SpendAmount]) formatString: \$#,##0...` | - |
| **`'Marketing ROI'`** | `DIVIDE( [Total Sales], [Total Campaign Spend], BLANK() ) ...` | - |
| **`'Revenue per Campaign`** | `DIVIDE([Total Sales], DISTINCTCOUNT(FactCampaignSpend[Cam...` | - |
| **`'Total Customers'`** | `DISTINCTCOUNT(FactSales[CustomerID]) formatString: #,##0 ...` | - |
| **`'Sales per Customer'`** | `DIVIDE([Total Sales], [Total Customers], BLANK()) formatS...` | - |
| **`'Repeat Customer Rate`** | `VAR _RepeatCustomers = COUNTROWS( FILTER( ADDCOLUMNS( VAL...` | - |
| **`'Selected Period Sales'`** | `CALCULATE( [Total Sales], ALLSELECTED(DimDate) ) formatSt...` | - |
| **`'Running Total Sales'`** | `CALCULATE( [Total Sales], FILTER( ALL(DimDate[Date]), Dim...` | - |
| **`'Sales Rolling 3M'`** | `CALCULATE( [Total Sales], DATESINPERIOD(DimDate[Date], LA...` | - |

---

## Security
*Type: `Fact`*

### Columns
| Column Name | Data Type | Source Field | Summarize By | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`UserEmail`** | `string` | `UserEmail` | `none` | - |
| **`Region`** | `string` | `Region` | `none` | - |

---
