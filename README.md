<div align="center">


# Project D.R.I.S.H.T.I.
### **D**ual-Frequency **R**adar **I**nformed **S**ubsurface **H**ydration & **T**errain **I**ntelligence

*A Physics-Informed, Multi-Modal Fusion Framework for Lunar Subsurface Ice Detection and Mission Accessibility*

[![Hackathon](https://img.shields.io/badge/ISRO-Bharatiya%20Antariksh%20Hackathon%202026-orange)](https://github.com/Deepmalya2506/DRISHTI)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Deployed-green)](https://fastapi.tiangolo.com/)

</div>

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Key Features](#-key-features)
- [Physics Core & Mathematical Foundation](#-physics-core--mathematical-foundation)
- [End-to-End System Architecture](#-end-to-end-system-architecture)
- [Proof of Concept: Crater Shoemaker](#-proof-of-concept-crater-shoemaker)
- [Benchmark Results](#-benchmark-results)
- [Tech Stack](#-tech-stack)
- [Cost & Implementation Breakdown](#-cost--implementation-breakdown)
- [Team "From Light Years Away"](#-team-from-light-years-away)

---

## 🌌 Overview

**Project D.R.I.S.H.T.I** is a unified physics-constrained framework developed for the **Bharatiya Antariksh Hackathon 2026**. It integrates fully polarimetric radar scattering physics (CPR-FP, DOP, SRI), Maxwell-Garnett dielectric mixing models, kinematic geomorphology, and mobility-aware path planning.

By fusing **Chandrayaan-2 DFSAR** full-polarimetric/dual-frequency radar observations with **OHRC** high-resolution optical imagery, **LOLA GDR DEM**, and lunar illumination models, DRISHTI identifies, quantifies, and validates subsurface water-ice deposits within Permanently Shadowed Regions (PSRs) and Doubly Shadowed Regions (DSRs) while determining safe landing sites and traversable rover trajectories.

---

## 🎯 Problem Statement

> **Detection and Characterization of Subsurface Ice in Lunar South Polar Regions Using Chandrayaan-2 Radar and Imagery Data for Landing Site and Rover Traverse Planning**

Traditional radar-based detection methods often ignore spatial terrain heterogeneity and suffer from topographic ambiguity, leading to false positives caused by rocky ejecta. DRISHTI resolves these ambiguities by mathematically isolating true volumetric ice scattering from surface roughness and ejecta artifacts.

---

## ✨ Key Features

* **Multi-Modal Geospatial Intelligence:** Combines Chandrayaan-2 DFSAR radar observations with OHRC morphology, LOLA GDR DEM, and solar illumination models into a unified interpretation engine.
* **Multi-Evidence Ice Validation:** Correlates Circular Polarization Ratio (CPR-FP), Degree of Polarization (DOP), Surface Roughness Index (SRI), and shadow persistence to isolate genuine subsurface ice candidates.
* **Dielectric Ice Fraction Estimation:** Utilizes Maxwell-Garnett dielectric mixing models and Thompson lookup table inversion mapping to quantitatively estimate subsurface ice volume fraction (top 5 meters) beyond binary ice detection.
* **Accessibility-Driven Mission Analytics:** Integrates slope, roughness, boulder density, and illumination power constraints into a 2.5D Reverse Minimum Cost Path (MCP) algorithm for risk-free landing site selection and optimal rover routing.
* **Interactive Lunar Decision Workspace:** Provides an intuitive GIS-based interface for visualizing radar products, ice heatmaps, hazard layers, and trajectory routes within a single environment.

---

## 🔬 Physics Core & Mathematical Foundation

DRISHTI uses full-polarimetric radar processing and scattering physics to eliminate false positives:

* **Polarimetric Disambiguation Rules (Crater Shoemaker PoC):**
  * $\text{High CPR} + \text{Low DOP} \implies \text{Volumetric multiple-scattering (True Ice Candidate)}$
  * $\text{High CPR} + \text{Slope} (>12^\circ) \implies \text{Dihedral surface roughness / Rocky Ejecta (False Positive)}$
  * $\text{PSR Mask} + \text{CPR Anomaly} \implies \text{Thermally plausible cold trap ice zone}$
  * $\text{High CPR} + \text{Low OHRC-SRI} \implies \text{Decoupled surface roughness (Subsurface Volumetric Ice)}$

### Maxwell-Garnett Dielectric Modeling
To estimate effective permittivity ($\epsilon_{eff}$) and ice volume fraction ($f$), the framework models the dielectric behavior of regolith-ice mixtures:

$$\epsilon_{eff} = \epsilon_m \frac{1 + 2f \frac{\epsilon_i - \epsilon_m}{\epsilon_i + 2\epsilon_m}}{1 - f \frac{\epsilon_i - \epsilon_m}{\epsilon_i + 2\epsilon_m}}$$

*Where $\epsilon_m$ represents matrix permittivity of dry lunar regolith and $\epsilon_i$ represents ice permittivity.*

![Mathematical Architecture & Pipeline](./assets/09_math_architecture.png)

---

## 🏗️ End-to-End System Architecture

The complete processing pipeline spans data ingestion, physics analysis, multi-modal validation, and mission accessibility planning:

![Process Flow Diagram](./assets/04_process_flow_diagram.png)

### Pipeline Stages:
1. **Data Inputs:** Raw DFSAR full-pol data, OHRC imagery, LOLA DEM, and solar illumination models.
2. **Physics-Based Analysis:** Extract polarimetric parameters (CPR, DOP, SRI), compute Yamaguchi YR4 4-component decomposition (Surface, Double-bounce, Volume scattering), apply Maxwell-Garnett dielectric mixing, and estimate ice fraction (top 5 m).
3. **Multi-Modal Validation:** Apply PSR/DSR shadow masking, terrain & morphologic checks, thermal stability checks, and cross-validation to remove false positives.
4. **Mission Accessibility:** Score landing site feasibility, build hazard maps, and execute Reverse Minimum Cost Path (MCP) rover trajectory planning.
5. **Outputs:** Subsurface ice heat maps, recommended landing site coordinates, traversable route vectors, and volumetric ice estimates ($m^3$).

---

## 🧪 Proof of Concept: Crater Shoemaker

The PoC was benchmarked using Chandrayaan-2 DFSAR observations over **Crater Shoemaker** across a scale of 19 Million pixels.

### Data Strip & Region of Interest (ROI)
![DFSAR Strip ROI](./assets/02_dfsar_roi_strip.png)

### Shadow Masking & Surface Roughness Analysis
![Shadowed Crater Mask & Roughness](./assets/03_shadow_mask_roughness.png)

### Processing Interfaces & Visualizations
| MIDAS Ingestion & Filtering | Polarimetric Decomposition |
| :---: | :---: |
| ![MIDAS Processing](./assets/05_midas_processing.png) | ![Radar Decomposition](./assets/06_radar_decomposition.png) |

| Elevation & Shadowed Contours | 3D Terrain & Slope Mesh |
| :---: | :---: |
| ![Crater Elevation](./assets/07_elevation_crater_map.png) | ![3D Terrain Visualization](./assets/08_3d_terrain_visualization.png) |

---

## 📊 Benchmark Results

| Benchmark Metric | Existing Work | **DRISHTI PoC** | Source / Notes |
| :--- | :---: | :---: | :--- |
| **$R^2$ Ordinary Least Square Coeff.** | `0.5287` | **`0.99`** | Masked 7M pixels where spatial heterogeneity dominates over inverse CPR-DOP relationship |
| **Mean Effective Permittivity ($\epsilon_{eff}$)** | `2.70` to `3.15` | **`2.947`** | Benchmark derived from Mini-RF S-band literature |
| **Volumetric Ice Estimate** | 40 to 200m thick *(S-band)* | **$2.70 \times 10^6 \text{ m}^3$** | Top 5m depth (L-band DFSAR), Uncertainty: $\pm 25\%$ |

*\*PoC benchmarked on available L-band DFSAR data over Crater Shoemaker.*

---

## 🛠️ Tech Stack

* **Modeling & Processing:** Python, NumPy, SciPy, Pandas, OpenCV-Python, scikit-image, PyProj, Statsmodels, MIDAS
* **Radar & Geospatial Analysis:** QGIS, GDAL Driver, Rasterio
* **Validation & Quantification:** Maxwell-Garnett Modelling, Thompson LUT Inversion
* **Visualization & Demo:** Matplotlib, Plotly, Streamlit
* **Deployment:** FastAPI, Docker

---

## 💰 Cost & Implementation Breakdown

| Module / Item | Cost (₹) | Description |
| :--- | :---: | :--- |
| **DFSAR SLI Processing** | ₹1,00,000 | MIDAS import, multilooking, and radar preprocessing |
| **Polarimetric Filtering** | ₹75,000 | $9\times9$ Refined Lee filtering & speckle suppression |
| **Radar Feature Extraction** | ₹90,000 | CPR, DOP, coherency matrix ($T_3$), decomposition outputs |
| **Ice Candidate Modelling** | ₹85,000 | Maxwell-Garnett dielectric modelling & Thompson LUT inversion |
| **PSR & DSR Masking** | ₹60,000 | Thermal cold-trap validation & shadow region filtering |
| **Terrain Hazard Mapping** | ₹75,000 | LOLA DEM slope and surface roughness generation |
| **Candidate Clustering & Validation** | ₹70,000 | Density clustering & false-positive rejection |
| **Reverse Path Planning** | ₹95,000 | Landing-site feasibility, rover traverse & mission routing |
| **Total Estimated Budget** | **₹6,50,000** | *(Estimated implementation cost)* |

---

## 👥 Team "From Light Years Away"

Developed at **Institute of Engineering & Management, Kolkata** for the **Bharatiya Antariksh Hackathon 2026 (ISRO)**.

| Member | Role | Institution |
| :--- | :--- | :--- |
| **Deepmalya Koley** | Team Leader | Institute of Engineering & Management, Kolkata |
| **Rishav Kumar Mishra** | Team Member | Institute of Engineering & Management, Kolkata |
| **Anurag Paul** | Team Member | Institute of Engineering & Management, Kolkata |
| **Ujaan Mukherjee** | Team Member | Institute of Engineering & Management, Kolkata |

---

<div align="center">

![ISRO Banner](./assets/10_thank_you_banner.png)

**"We, as a dedicated team, are excited and humbled to solve this problem and actively contribute to India's Future Lunar Mission."**

[GitHub Repository](https://github.com/Deepmalya2506/DRISHTI)

</div>