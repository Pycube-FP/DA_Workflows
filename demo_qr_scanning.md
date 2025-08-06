# QR Code Scanning Demo Guide

## 🏥 Asset Tracking System - QR Code Scanner

### 📱 How to Demo the QR Code Scanning Feature

#### **Step 1: Access the Scanner**
1. Open the application: `http://127.0.0.1:5000`
2. Login with: `admin` / `password123`
3. Click on **"Scan Asset"** in the navigation

#### **Step 2: QR Code Scanner Interface**
- **Large QR Code Icon** - Visual indicator for scanning
- **Single "Scan QR Code" Button** - Click to start scanning
- **Demo QR Code Buttons** - For testing without physical scanner

#### **Step 3: Real QR Code Scanning Process**

**Option A: Physical QR Code Scanner**
1. Click **"Scan QR Code"** button
2. **Scanning Modal** appears with input field
3. **Point your scanner** at the asset QR code
4. **QR code value appears** in the input field automatically
5. Click **"Get Asset Info"** or press **Enter**
6. **Asset Information Popup** shows device details

**Option B: Manual Entry (for demo)**
1. Click **"Scan QR Code"** button
2. **Scanning Modal** appears
3. **Manually enter one of these QR codes:**
   - `200000001192024000004099` (Welch Allyn MicroPAQ)
   - `00000000000000000000000000000134` (Masimo Radical-7)
   - `200000001192024000004039` (Sigma Spectrum)
4. Click **"Get Asset Info"** or press **Enter**
5. **Asset Information Popup** shows device details

#### **Step 4: Available QR Codes**

| QR Code | Device Name | Manufacturer | Location | Status |
|---------|-------------|--------------|----------|---------|
| `200000001192024000004099` | Welch Allyn MicroPAQ | Welch Allyn | ICU Zone A | Available |
| `00000000000000000000000000000134` | Masimo Radical-7 | Masimo Corporation | ER Trauma Bay | In Use |
| `200000001192024000004039` | Sigma Spectrum | B. Braun Medical | ICU Zone B | Available |

### 🎯 **Asset Information Popup Features**

#### **📋 Device Details Displayed:**
- **Device Name & Icon** - Clear identification
- **Manufacturer** - Company information
- **Category** - Device type classification
- **Current Location** - Where the device is located
- **Status** - Available/In Use/Maintenance
- **Description** - Brief device overview
- **Specifications** - Technical details

#### **❓ Interactive Question System:**
- **Maintenance Schedule** - When is next maintenance due?
- **Training Required** - What training is needed?
- **Safety Procedures** - Safety guidelines and protocols
- **Usage Guidelines** - How to use the device properly

### 🎪 **Demo Scenarios**

#### **Scenario 1: Real QR Code Scanning**
1. Click **"Scan QR Code"** button
2. **Point scanner** at Welch Allyn MicroPAQ QR code
3. **QR code appears** in input field: `200000001192024000004099`
4. Click **"Get Asset Info"**
5. **Popup shows:**
   - Welch Allyn MicroPAQ device information
   - Manufacturer: Welch Allyn
   - Location: ICU Zone A
   - Available status
6. **Ask "Maintenance Schedule"** - Shows calibration every 6 months
7. **Ask "Training Required"** - Shows basic training for nursing staff

#### **Scenario 2: Masimo Radical-7**
1. Click **"Scan QR Code"** button
2. **Point scanner** at Masimo Radical-7 QR code
3. **QR code appears** in input field: `00000000000000000000000000000134`
4. Click **"Get Asset Info"**
5. **Popup shows:**
   - Masimo Radical-7 pulse oximeter
   - Manufacturer: Masimo Corporation
   - Location: ER Trauma Bay
   - In Use status
6. **Ask "Safety Procedures"** - Shows sensor placement guidelines
7. **Ask "Usage Guidelines"** - Shows continuous monitoring procedures

#### **Scenario 3: Sigma Spectrum**
1. Click **"Scan QR Code"** button
2. **Point scanner** at Sigma Spectrum QR code
3. **QR code appears** in input field: `200000001192024000004039`
4. Click **"Get Asset Info"**
5. **Popup shows:**
   - Sigma Spectrum infusion pump
   - Manufacturer: B. Braun Medical
   - Location: ICU Zone B
   - Available status
6. **Ask "Training Required"** - Shows comprehensive training needed
7. **Ask "Safety Procedures"** - Shows critical safety device protocols

### 🔍 **Key Features Demonstrated**

✅ **Single QR Code Scanning Button**
- One-click access to scanning interface
- Clean, simple user experience
- Professional hospital interface

✅ **Real QR Code Recognition**
- Instant asset identification from scanned QR codes
- Support for the exact QR codes you provided
- Real-time information display

✅ **Comprehensive Asset Information**
- Device specifications
- Manufacturer details
- Location and status tracking
- Usage guidelines

✅ **Interactive Q&A System**
- Pre-programmed answers for common questions
- Device-specific information
- Safety and training guidelines
- Maintenance schedules

✅ **Professional Interface**
- Clean, hospital-appropriate design
- Modal popups for focused information
- Easy-to-use scanning interface
- Clear visual indicators

### 🏥 **Value Proposition**

**For Hospital Staff:**
- Instant access to device information via QR code scanning
- Quick answers to common questions
- Reduced training time
- Improved safety compliance

**For Management:**
- Real-time asset tracking
- Usage analytics
- Maintenance scheduling
- Cost optimization

### 📊 **Technical Implementation**

- **Frontend:** Bootstrap modals for popup display
- **JavaScript:** Asset database with QR code mapping
- **QR Code Input:** Automatic field population from scanner
- **Responsive Design:** Works on mobile and desktop
- **Keyboard Support:** Enter key to submit scanned codes

### 🚀 **Ready to Demo!**

**Access the scanner:** `http://127.0.0.1:5000/scan_asset`

**Demo Flow:**
1. Click **"Scan QR Code"** button
2. **Point scanner** at asset QR code (or manually enter for demo)
3. **QR code appears** in input field
4. Click **"Get Asset Info"** or press **Enter**
5. View **asset information popup**
6. Click **question buttons** to get detailed information
7. Close popup and scan another QR code

---

**Perfect for customer demonstrations!** 🎯

The system now provides exactly what you requested - a **single "Scan QR Code" button** that allows users to scan the actual QR codes on physical assets and get instant device information with an interactive question system! 🏥✨ 