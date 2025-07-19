# Tobacco Manufacturing Module for Odoo 17

![Odoo Manufacturing](https://img.shields.io/badge/Odoo-17.0-%23A347B6)
![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue)

Enhanced manufacturing operations with waste management, sub-BOMs, and OEE tracking for tobacco production.

## Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start Guide](#-quick-start-guide)
- [OEE Calculation](#-oee-calculation)
- [Troubleshooting](#-troubleshooting)
- [Technical Reference](#-technical-reference)
- [License](#-license)
- [Support](#-support)

## 📦 Features

### Core Components
- **Precision Waste Management**
  - Wizard-based scrap registration
  - 5% maximum waste enforcement
  - Automatic component scrap calculation FG & Components

- **Hierarchical BOM System**
  - Main BOM with production factors
  - Sub-BOMs with cigarette-level material ratios
  ```python
  # Sample Sub-BOM Line
  {
      'material': product_obj,
      'qty_per_cig': 0.00095,  # kg per cigarette
      'special_calc': False
  }
  ```

## 🛠 Installation

### Requirements
- Odoo 17.0 Enterprise or Community
- PostgreSQL 12+
- Python 3.8+

### Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install module:
   ```bash
   odoo-bin -i tobacco_mrp -d your_database
   ```

## 📚 Technical Reference

### Key Models
| Model | Path | Purpose |
|-------|------|---------|
| `mrp.waste.wizard` | `waste_wizard.py` | Scrap UI |
| `sub.bom` | `sub_bom.py` | Material ratios |

## 📜 License
This module is licensed under LGPL-3.

## 📧 Support
For assistance contact:
- Email: mansour.agied@khotawat.com
- Phone: +1 (555) 123-4567

---

**Version**: 1.1.0  
**Last Updated**: 2025-07-19
