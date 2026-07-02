# Project D.R.I.S.H.T.I 🌕🛰️
**Dual-Frequency Radar Informed Subsurface Hydration & Terrain Intelligence**


**Detection and Characterization of Subsurface Ice in Lunar South Polar Regions Using Chandrayaan-2 Radar and Imagery Data for Landing Site and Rover Traverse Planning.**

---

## 🚀 Project Overview
Project D.R.I.S.H.T.I is a Physics-Informed, Multi-Modal Fusion Framework designed for Lunar Subsurface Ice Detection and Mission Accessibility. It acts as a unified framework integrating:
* Fully polarimetric radar scattering physics (CPR-FP, DOP, and SRI)
* Maxwell-Garnett dielectric mixing models
* Kinematic geomorphology
* Mobility-aware path planning

**Goal:** To identify scientifically reliable and operationally accessible subsurface water-ice deposits within permanently and doubly shadowed lunar regions using Chandrayaan-2 DFSAR full-pol/dual-frequency radar observations fused with OHRC-derived morphology, LOLA GDR DEM, and lunar illumination models.

---

## ✨ Key Features & USP
* **Multi-Modal Geospatial Intelligence:** Fuses Chandrayaan-2 DFSAR radar observations with OHRC morphology, LOLA DEM, and illumination models for a unified interpretation of ice-bearing terrain.
* **Multi-Evidence Ice Validation:** Correlates CPR-FP, DOP, SRI, shadow persistence, and terrain characteristics to minimize false positives and identify highly reliable ice candidates.
* **Dielectric Ice Fraction Estimation:** Uses Maxwell-Garnett mixing models to transition from binary (ice/no-ice) mapping to quantitative subsurface ice volume fractions (within 5m depth).
* **Accessibility-Driven Mission Analytics:** Integrates terrain hazards, rover mobility constraints, and reverse Minimum Cost Path (MCP) analysis to map feasible landing zones and rover routes.
* **Interactive Lunar Decision Workspace:** A GIS-based interface for visualizing radar products, ice candidates, terrain hazards, and mission planning layers.

---

## 🧠 Core Architecture & Pipeline

### 1. Data Inputs
* **DFSAR:** Full Polarimetric Radar (Dual Frequency)
* **OHRC Imagery:** High-Resolution Optical Camera
* **LOLA DEM:** Digital Elevation Model
* **Illumination Model**

### 2. Physics-Based Analysis
* **Polarimetric Feature Extraction:** Compute CPR, DOP, SRI from full polarimetric data.
* **Scattering Decomposition:** Yamaguchi YR4 Decomposition (Surface, Double-bounce, Volume Scattering).
* **Ice-like Signature Detection:** High CPR, Low DOP, High Volume Scattering.
* **Dielectric Modeling & Concentration Estimation:** Maxwell-Garnett Mixing Model to convert radar responses into ice fractions and estimate volume (m³) within Top-5m.

### 3. Multi-Modal Validation
* **PSR/DSR Masking:** Isolating permanently/doubly shadowed regions.
* **Terrain & Morphology Check:** Slope, roughness, boulder density, crater morphology.
* **Thermal Plausibility & Cross-Validation:** Combining radar, terrain, and thermal evidence to eliminate False Positives (e.g., rocky ejecta).

### 4. Mission Accessibility
* **Hazard Mapping:** Steep slopes, rough terrain, large boulders, illumination (power).
* **Landing Site Selection:** Near high-confidence ice, inside PSR/DSR, safe slope/communication.
* **Rover Traverse Planning & Simulation:** Reverse Minimum Cost Path based on kinematics constraints.

---

## 💻 Technology Stack
| Category | Technologies / Tools |
| :--- | :--- |
| **Modeling & Processing** | MIDAS, Python, NumPy, Pandas, OpenCV, scikit-image |
| **Radar & Geospatial Analysis** | QGIS, GDAL driver, rasterio |
| **Validation & Quantification** | Maxwell-Garnett modelling, Thompson LUT Inversion |
| **Visualization & Demo** | Matplotlib, Plotly, Streamlit |
| **Deployment** | FastAPI, PostGIS, Docker |

---

## 📊 Benchmarks & Results (POC: Crater Shoemaker)
* **Scale:** 7 Million pixels
* **R² Benchmark:** Existing Work (0.99) vs. DRISHTI POC (0.5287) - *Focused on regions where spatial heterogeneity dominates over inverse CPR_DOP relationship.*
* **Mean Effective Permittivity:** 2.947
* **Volumetric Ice Estimate (top 5m - L band):** 2.70 × 10⁶ m³ (Uncertainty: ±25%)

---

