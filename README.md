# Asset Usage & Rental Tracking System

A comprehensive end-to-end workflow prototype for hospital asset management, featuring QR code scanning, AI-powered knowledge layer, real-time tracking, and advanced analytics.

## 🎯 Overview

This system implements the complete Asset Usage & Rental Tracking workflow as specified, providing:

- **Asset Usage Initiation** via QR code scanning
- **AI Assistant & Knowledge Layer** (Atlas of Assets)
- **Session Assignment & Logging** with detailed tracking
- **Real-time Monitoring** and alert generation
- **Asset Return & Transition** management
- **Comprehensive Reporting & Analytics**
- **Integration-ready** architecture for other workflows

## 🚀 Features

### 1. Asset Usage Initiation
- QR code/barcode scanning interface
- Asset recognition and validation
- Status checking (available/in-use/maintenance)
- Ownership verification (hospital vs rental)
- Location and last usage retrieval

### 2. Atlas of Assets - AI Knowledge Layer
- **Standard Operating Procedures** for each asset category
- **Training requirements** detection
- **Critical device** warnings
- **Safety protocols** and guidelines
- **Usage limits** and maintenance intervals

### 3. Usage Management
- **Usage assignment** with user tracking
- **Duration tracking** and overuse detection
- **Patient pseudonymization** for privacy
- **Department accountability**
- **Real-time status updates**

### 4. Real-Time Tracking
- **Location tracking** via asset status
- **Utilization patterns** analysis
- **Alert generation** for:
  - Rental expiry warnings
  - Overuse detection
  - Inactivity alerts
  - Location mismatches

### 5. Analytics & Reporting
- **Utilization rates** by department
- **Rental ROI** analysis
- **Idle asset detection**
- **Audit trails** and compliance
- **Lifecycle prediction** and insights

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Frontend**: HTML5, Bootstrap 5, Font Awesome
- **QR Code**: Python qrcode library
- **Authentication**: Flask-Login
- **Data Visualization**: Bootstrap components + custom charts

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Asset_workflows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the system**
   - Open your browser and go to `http://localhost:5000`
   - Login with demo credentials:
     - Username: `admin`
     - Password: `admin123`

## 📊 Database Schema

### Core Tables

#### Users
- Hospital staff (nurses, technicians, administrators)
- Department assignment
- Role-based access control

#### Assets
- Asset inventory with unique IDs
- Categories (infusion_pump, ventilator, monitor, wheelchair)
- Ownership (hospital vs rental)
- Status tracking (available, in-use, maintenance)
- QR code generation

#### Asset Sessions
- Usage tracking with start/end times
- User and patient assignment
- Department accountability
- Reason for use documentation

#### Alerts
- Automated alert generation
- Multiple alert types (rental_expiry, overuse, inactivity)
- Severity levels and resolution tracking

#### Asset SOPs
- Standard Operating Procedures
- Training requirements
- Safety guidelines

## 🔄 Workflow Implementation

### 1. Asset Scanning Process
```
User scans QR code → Asset recognition → Status check → Atlas query → Session initiation
```

### 2. Atlas of Assets Integration
- **Infusion Pumps**: Flow rate settings, air bubble checks, patient monitoring
- **Ventilators**: Settings verification, alarm monitoring, connection checks
- **Monitors**: Sensor calibration, reading verification, battery status
- **Wheelchairs**: Brake checks, proper fit, cleaning protocols

### 3. Real-Time Monitoring
- **Location tracking** via asset status updates
- **Duration monitoring** with overuse alerts
- **Rental management** with expiry warnings
- **Utilization analytics** for optimization

### 4. Session Lifecycle
```
Start Session → Active Monitoring → End Session → Asset Return → Analytics Update
```

## 📈 Analytics & Reporting

### Utilization Reports
- **Department-wise** utilization rates
- **Asset category** performance
- **Time-based** usage patterns
- **ROI analysis** for rentals

### Predictive Insights
- **Lifecycle prediction** based on usage patterns
- **Maintenance scheduling** recommendations
- **Reallocation opportunities** identification
- **Purchase vs rental** cost analysis

### Compliance & Audit
- **Full audit trails** for all asset movements
- **User accountability** tracking
- **Training compliance** monitoring
- **Safety protocol** adherence

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///asset_tracking.db
FLASK_ENV=production
```

### Atlas of Assets Configuration
The knowledge layer can be extended in `app.py`:
```python
ATLAS_OF_ASSETS = {
    'new_device_type': {
        'sop': 'Standard operating procedures...',
        'training_required': True,
        'critical_device': False,
        'max_continuous_use': 8,
        'maintenance_interval': 30
    }
}
```

## 🔌 API Endpoints

### Asset Management
- `GET /api/assets` - List all assets
- `GET /api/scan/<asset_id>` - Scan and recognize asset
- `POST /initiate_session` - Start asset session
- `POST /end_session/<session_id>` - End asset session

### Reporting
- `GET /reports` - Analytics dashboard
- `GET /assets` - Asset inventory
- `GET /asset/<asset_id>` - Asset details

## 🎨 UI/UX Features

### Modern Interface
- **Responsive design** for mobile and desktop
- **Bootstrap 5** components for consistency
- **Font Awesome** icons for intuitive navigation
- **Real-time updates** without page refresh

### User Experience
- **QR code scanning** simulation
- **Quick action buttons** for common tasks
- **Alert system** with severity indicators
- **Dashboard overview** with key metrics

## 🔒 Security Features

- **User authentication** with Flask-Login
- **Password hashing** with bcrypt
- **Session management** for secure access
- **Role-based access** control
- **Patient data pseudonymization**

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (using Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔄 Integration Points

### CMMS Integration
- Asset status synchronization
- Maintenance workflow triggers
- Inventory management integration

### IoT Integration
- Real-time location tracking
- Sensor data integration
- Automated status updates

### Vendor Systems
- Rental management integration
- Billing system connectivity
- Return scheduling automation

## 📊 Sample Data

The system comes pre-loaded with sample assets:
- **INF001**: Infusion Pump A (Hospital owned)
- **VENT001**: Ventilator B (Rental from MedEquip Inc)
- **MON001**: Patient Monitor C (Hospital owned)
- **WC001**: Wheelchair D (Hospital owned)

## 🎯 Value Proposition

### Operational Efficiency
- **Prevents overbuying** through utilization analysis
- **Enables right-sizing** of inventory
- **Ensures smooth transfers** across departments

### Cost Reduction
- **Reduces rental overruns** via timely alerts
- **Avoids unnecessary purchases** through data insights
- **Enables fast return** of idle rental equipment

### Accountability & Compliance
- **Full usage audit trails**
- **Department-wise tracking**
- **Training compliance** monitoring

### Smart AI Guidance
- **Real-time knowledge access**
- **Reduces training load**
- **Ensures safe usage**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for healthcare asset management** 