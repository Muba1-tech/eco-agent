# 🌿 EcoAgent: Judge Quick-Start & Demonstration Guide

> **Submission for:** 1M1B AI for Sustainability / AICTE / IBM SkillsBuild Hackathon  
> **SDG Alignment:** UN SDG 12 (Responsible Consumption & Production) & UN SDG 13 (Climate Action)  
> **Tech Stack:** 100% Free & Open-Source (Streamlit, FAISS, Sentence-Transformers, ReportLab, SQLite, Local Ollama / Gemini Free-Tier fallback)

---

## ⚡ Quick 60-Second Test Instructions for Judges

1. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```
2. **Instant Pre-Loaded Demo**:
   - The application automatically pre-loads **Preset 1 (Urban Retail Store)** upon launch. All charts, benchmark comparisons, RAG citations, and ROI calculations are live immediately.
3. **Switch Between 4 Realistic Scenarios**:
   - Open the **Sidebar** on the left and select any scenario from the **"Quick Demo Presets"** dropdown. The multi-agent pipeline immediately re-evaluates in real time!
4. **Inspect Policy Citations**:
   - Navigate to **Tab 3 ("Grounded Recommendations")** to verify that every recommendation cites real Indian gazetted standards (BEE, MNRE PM-Surya Ghar, CPCB SWM Rules 2016) with semantic RAG confidence scores.
5. **Simulate Decarbonization & Download PDF**:
   - Navigate to **Tab 4 ("Carbon & Financial ROI")**, adjust the **"What-If" sliders**, and click **"Generate & Prepare Official PDF Report"** to download the audit document.
6. **Direct Policy Search**:
   - Navigate to **Tab 5 ("Govt Scheme & Policy Explorer")** and test natural language queries directly against the vector database.

---

## 🏢 Scenario 1: Small Commercial Retail Store & Office (Bengaluru)
- **Profile:** 8 personnel, commercial tariff (₹8.5/kWh), 1,150 kWh/month (Bill: ₹9,800/mo).
- **Equipment:** 3 unrated older ACs set at 20°C, 6 induction fans (75W), no solar (650 sq.ft roof available), frequent single-use packaging.
- **Expected Diagnostic Flags (Agent 1):**
  - Sustainability Score: ~**44 / 100 (High Waste & Inefficiency)**
  - Flagged: Sub-optimal AC efficiency, Low thermostat (20°C vs BEE 24°C), High fan power draw (6 induction units), Unutilized rooftop solar, Lack of waste segregation.
- **Expected Grounded Recommendations (Agent 2):**
  - **MNRE PM-Surya Ghar Solar:** Install 3 kW Rooftop PV under MNRE operational guidelines.
  - **BEE S&L 2023-24:** Upgrade cooling to 5-Star Inverter ACs (saves 28-35% cooling load).
  - **BEE 24°C Thermostat Rule:** Increase setpoint from 20°C to 24°C (saves 24% cooling power immediately).
  - **BEE BLDC Fans:** Switch 6 induction fans to 28W BLDC fans (saves 55-60% fan electricity).
  - **CPCB SWM Rules 2016 (Rule 4):** Establish mandatory 3-stream segregation (Green/Blue/Red).
- **Expected Quantified Impact (Agent 3):**
  - **Annual Cost Savings:** ~**₹68,000 – ₹74,000 / year**
  - **Annual CO₂ Emissions Avoided:** ~**6,800 – 7,300 kg CO₂e / year** (~7.1 metric tonnes)
  - **Tree Absorption Equivalent:** ~**310 – 335 mature trees**
  - **Capital Payback Period:** ~**2.6 years**

---

## 🏡 Scenario 2: High-Consumption Urban Family Villa (South Delhi)
- **Profile:** 4 occupants, residential tariff (₹8.0/kWh), 650 kWh/month (Bill: ₹5,400/mo).
- **Equipment:** 2 older 1-2 Star ACs set at 21°C, 5 induction fans, 450 sq.ft roof, high water consumption (180 LPCD), no waste segregation.
- **Expected Diagnostic Flags (Agent 1):**
  - Per-Capita Power: **162.5 kWh/mo** (+71% above CEA 95 kWh benchmark).
  - Water: **180 LPCD** (+33% above CPHEEO 135 LPCD benchmark).
  - Flagged: Solar rooftop gap, Cooling inefficiencies, Induction fans, Waste mixing, Tap water flow.
- **Expected Grounded Recommendations (Agent 2):**
  - **MNRE PM-Surya Ghar:** 3 kW solar plant with ₹78,000 central subsidy.
  - **BEE AC Guidelines:** Upgrade to 5-Star inverter units + set thermostat to 24°C.
  - **Swachh Bharat Urban 2.0:** In-situ home composting diverts ~220 kg wet waste annually, preventing landfill methane.
  - **CPHEEO Water Conservation:** Low-flow tap aerators cut faucet draw by 50-60%.
- **Expected Quantified Impact (Agent 3):**
  - **Annual Cost Savings:** ~**₹49,000 – ₹54,000 / year**
  - **Annual CO₂ Emissions Avoided:** ~**4,900 – 5,300 kg CO₂e / year** (~5.1 metric tonnes)
  - **Water Conserved:** ~**18,000 Litres / year**
  - **Waste Diverted:** ~**220 kg wet waste composted / year**

---

## 🏙️ Scenario 3: Suburban Apartment (Thane, Mumbai)
- **Profile:** 3 occupants, residential tariff (₹8.4/kWh), 380 kWh/month (Bill: ₹3,200/mo).
- **Equipment:** 1 3-Star AC set at 23°C, 3 induction fans, segregates waste but does not compost, 170 LPCD water usage.
- **Expected Diagnostic Flags (Agent 1):**
  - Sustainability Score: ~**66 / 100 (Moderate Efficiency)**
  - Flagged: Induction fans, Organic waste landfill diversion gap, Faucet aerator gap.
- **Expected Grounded Recommendations (Agent 2):**
  - **BEE BLDC Fans:** Transition 3 fans to 5-Star BLDC (saves ~400 kWh/year).
  - **BEE Thermostat Nudge:** Adjust thermostat from 23°C to 24°C (saves 6% cooling energy).
  - **Swachh Bharat Decentralized Composting:** Aerobic pot composting for balcony kitchen scraps.
  - **CPHEEO Water Aerators:** Install aerators on 3 sinks saving ~13,500 L water/year.
- **Expected Quantified Impact (Agent 3):**
  - **Annual Cost Savings:** ~**₹6,500 – ₹8,200 / year**
  - **Annual CO₂ Emissions Avoided:** ~**650 – 850 kg CO₂e / year**
  - **Capital Investment:** Under ₹9,000 with simple payback under 1.2 years!

---

## 🌿 Scenario 4: Eco-Conscious Studio & Micro-Enterprise (Pune)
- **Profile:** 5 team members, 320 kWh/month (Bill: ₹2,600/mo).
- **Equipment:** 1 5-Star Inverter AC set at 25°C, 4 5-Star BLDC fans, 100% BEE LED lighting, tap aerators installed, full waste segregation & aerobic composting.
- **Expected Diagnostic Flags (Agent 1):**
  - Sustainability Score: ~**88 / 100 (Exemplary - Grade A)**
  - Primary Flag: Rooftop Solar PV adoption opportunity (350 sq.ft roof available to achieve Net-Zero).
- **Expected Grounded Recommendations (Agent 2):**
  - **MNRE PM-Surya Ghar:** Install 2 kW Rooftop Solar to eliminate 100% of remaining grid fossil emissions and achieve **Net-Zero Operational Energy status**.
- **Expected Quantified Impact (Agent 3):**
  - **Annual Cost Savings:** ~**₹24,000 – ₹27,000 / year**
  - **Net-Zero Status:** 100% of facility electricity offset by clean solar power.

---

## 🔍 Sample Queries to Test in the "Govt Scheme Explorer" (Tab 5)

1. `"What is the central financial assistance subsidy for 3kW rooftop solar under PM-Surya Ghar?"`
   - *Expected Match:* MNRE PM-Surya Ghar Operational Guidelines (₹78,000 subsidy, 4-5 units/day/kW).
2. `"What does BEE mandate for air conditioner thermostat temperature settings?"`
   - *Expected Match:* BEE Room Air Conditioner Regulations (default 24°C setting, 6% energy saving per degree increase).
3. `"What are the statutory duties of waste generators under CPCB 2016 rules?"`
   - *Expected Match:* CPCB Solid Waste Management Rules 2016 Rule 4 (3-stream segregation: Green/Blue/Red bins).
4. `"What is the official baseline grid emission factor for electricity in India?"`
   - *Expected Match:* CEA CO₂ Baseline Database Version 19.0 (0.82 kg CO₂/kWh national grid weighted average).
