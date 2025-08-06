# Asset Sessions Explained

## 🎯 What is a Session?

A session is like "borrowing time" with an asset. It tracks from when you start using an asset until you finish using it.

## 📊 Session Lifecycle

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AVAILABLE     │    │    IN USE       │    │   AVAILABLE     │
│                 │    │                 │    │                 │
│ Asset is ready  │───▶│ Session Active  │───▶│ Asset is ready  │
│ for use         │    │ Asset being     │    │ for use         │
│                 │    │ used by someone │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
   "Scan Asset"            "Use Asset"              "End Session"
   - QR Code scan         - Monitor patient        - Return asset
   - Asset recognition    - Track duration         - Update status
   - Start session        - Check for overuse      - Record usage

```

## 🏥 Real Hospital Example

### Scenario: Nurse Sarah needs an infusion pump

#### 1. **Before Session** (Asset Available)
```
Infusion Pump INF001
├── Status: Available ✅
├── Location: Storage
├── Last Used: 2 hours ago
└── Ready for: Next patient
```

#### 2. **Start Session** (Nurse scans pump)
```
Session Started:
├── Asset: INF001 (Infusion Pump)
├── User: Nurse Sarah
├── Patient: P12345 (pseudonymized)
├── Department: ICU
├── Expected Duration: 4 hours
├── Reason: Post-operative monitoring
└── Start Time: 14:30
```

#### 3. **During Session** (Asset in use)
```
Session Active:
├── Asset: INF001 (Infusion Pump)
├── Status: In Use ⏳
├── Current Duration: 2.5 hours
├── Remaining: 1.5 hours
├── Location: ICU Room 302
├── Patient: P12345
└── Nurse: Sarah
```

#### 4. **End Session** (Nurse returns pump)
```
Session Completed:
├── Asset: INF001 (Infusion Pump)
├── Status: Available ✅
├── Total Duration: 3.8 hours
├── End Time: 18:18
├── Patient: P12345
├── Notes: No issues
└── Ready for: Next use
```

## 🎯 Why Sessions Matter

### 1. **Accountability**
- Know who used what, when, and for how long
- Track which department used which assets
- Monitor individual usage patterns

### 2. **Patient Safety**
- Link assets to specific patients (pseudonymized)
- Track if equipment was used properly
- Ensure proper cleaning between uses

### 3. **Cost Management**
- Track rental costs vs usage
- Identify underutilized assets
- Optimize asset allocation

### 4. **Compliance**
- Maintain audit trails for regulations
- Track training requirements
- Monitor safety protocols

## 🔍 Session Data Examples

### Session Record in Database:
```json
{
  "session_id": "SESS_001",
  "asset_id": "INF001",
  "user_id": "nurse_sarah",
  "start_time": "2024-01-15 14:30:00",
  "end_time": "2024-01-15 18:18:00",
  "expected_duration": 4,
  "actual_duration": 3.8,
  "patient_id": "P12345",
  "reason": "post_op_monitoring",
  "department": "ICU",
  "status": "completed",
  "notes": "No issues encountered"
}
```

## 🚨 Session Alerts

The system monitors sessions for:

### ⏰ **Overuse Alerts**
- Asset used longer than recommended
- Example: Infusion pump used for 10 hours (max: 8 hours)

### 🏥 **Location Mismatch**
- Asset used in wrong department
- Example: ICU pump found in ER

### 💰 **Rental Expiry**
- Rental asset not returned on time
- Example: Rental ventilator overdue for return

### 📊 **Inactivity**
- Asset not used for extended period
- Example: Wheelchair unused for 30 days

## 🎨 In the UI

### Dashboard Shows:
- **Active Sessions**: Currently running sessions
- **Session History**: Past sessions
- **Session Details**: Who, what, when, where, why

### Session Management:
- **Start Session**: Scan asset → Fill form → Begin tracking
- **Monitor Session**: Real-time duration and status
- **End Session**: Complete usage → Return asset

## 💡 Think of it Like...

- **Library Book**: Check out → Read → Return
- **Hotel Room**: Check in → Stay → Check out
- **Car Rental**: Pick up → Drive → Return
- **Hospital Asset**: Scan → Use → Return

The session concept ensures we know exactly how our valuable hospital assets are being used, by whom, and for how long - which is crucial for patient safety, cost management, and regulatory compliance! 