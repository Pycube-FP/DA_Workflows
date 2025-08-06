from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import qrcode
import io
import base64
import json
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_tracking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # nurse, technician, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='available')  # available, in-use, maintenance, retired
    ownership = db.Column(db.String(50), nullable=False)  # hospital, rental
    location = db.Column(db.String(100), default='Storage')
    manufacturer = db.Column(db.String(200))  # Manufacturer name
    last_usage = db.Column(db.DateTime)
    purchase_date = db.Column(db.DateTime)
    expected_lifespan = db.Column(db.Integer)  # in months
    vendor = db.Column(db.String(200))
    rental_rate = db.Column(db.Float)
    qr_code = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AssetUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    expected_duration = db.Column(db.Integer)  # in hours
    patient_id = db.Column(db.String(100))  # pseudonymized
    reason = db.Column(db.String(200))
    department = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active')  # active, completed, overdue
    notes = db.Column(db.Text)

class AssetSOP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)  # rental_expiry, overuse, inactivity, location_mismatch
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), default='medium')  # low, medium, high, critical
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Atlas of Assets - Knowledge Layer
ATLAS_OF_ASSETS = {
    'wheelchair': {
        'sop': 'Check brakes and wheels. Ensure proper fit for patient. Clean after use. Verify patient safety.',
        'training_required': False,
        'critical_device': False,
        'max_continuous_use': 4,  # hours
        'maintenance_interval': 90  # days
    },
    'stretcher_gurney': {
        'sop': 'Verify safety straps. Check wheels and brakes. Ensure clean linens. Test emergency functions.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 2,
        'maintenance_interval': 30
    },
    'portable_xray': {
        'sop': 'Calibrate imaging sensors. Verify radiation safety protocols. Check battery status. Ensure proper positioning.',
        'training_required': True,
        'critical_device': False,
        'max_continuous_use': 6,
        'maintenance_interval': 60
    },
    'portable_ultrasound': {
        'sop': 'Calibrate transducer. Verify image quality. Check battery. Clean probe after use.',
        'training_required': True,
        'critical_device': False,
        'max_continuous_use': 4,
        'maintenance_interval': 45
    },
    'mobile_ecg': {
        'sop': 'Apply electrodes correctly. Verify signal quality. Monitor for arrhythmias. Clean electrodes after use.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 2,
        'maintenance_interval': 30
    },
    'iv_pole_wheeled': {
        'sop': 'Check IV bag security. Verify pump connections. Ensure proper height adjustment. Clean wheels.',
        'training_required': False,
        'critical_device': False,
        'max_continuous_use': 12,
        'maintenance_interval': 60
    },
    'mobile_vital_signs': {
        'sop': 'Calibrate sensors. Verify readings accuracy. Check battery status. Clean sensors after use.',
        'training_required': False,
        'critical_device': False,
        'max_continuous_use': 8,
        'maintenance_interval': 45
    },
    'defibrillator_cart': {
        'sop': 'Check battery charge. Verify electrode pads. Test emergency functions. Ensure rapid response capability.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 1,
        'maintenance_interval': 15
    },
    'infusion_pump_stand': {
        'sop': 'Verify pump settings. Check IV line connections. Monitor flow rate. Ensure proper medication delivery.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 8,
        'maintenance_interval': 30
    },
    'crash_cart': {
        'sop': 'Check emergency supplies. Verify medication expiration. Test defibrillator. Ensure rapid access.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 0.5,
        'maintenance_interval': 7
    },
    'portable_ventilator': {
        'sop': 'Verify settings match patient requirements. Monitor alarms. Check connections. Ensure battery backup.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 4,
        'maintenance_interval': 15
    },
    'anesthesia_cart': {
        'sop': 'Check medication inventory. Verify equipment functionality. Ensure sterile conditions. Monitor patient vitals.',
        'training_required': True,
        'critical_device': True,
        'max_continuous_use': 6,
        'maintenance_interval': 7
    }
}

def generate_qr_code(asset_id):
    """Generate QR code for asset"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"asset:{asset_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def check_asset_alerts(asset):
    """Check and create alerts for asset"""
    alerts = []
    
    # Check for rental expiry
    if asset.ownership == 'rental' and asset.last_usage:
        days_since_usage = (datetime.utcnow() - asset.last_usage).days
        if days_since_usage > 7:  # Alert if rental not used for 7 days
            alerts.append({
                'type': 'rental_expiry',
                'message': f'Rental asset {asset.name} has not been used for {days_since_usage} days',
                'severity': 'high'
            })
    
    # Check for inactivity
    if asset.last_usage:
        days_inactive = (datetime.utcnow() - asset.last_usage).days
        if days_inactive > 30:
            alerts.append({
                'type': 'inactivity',
                'message': f'Asset {asset.name} has been inactive for {days_inactive} days',
                'severity': 'medium'
            })
    
    return alerts

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('asset_management_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('asset_management_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))





@app.route('/asset/<int:asset_id>')
@login_required
def asset_detail(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    usage_history = AssetUsage.query.filter_by(asset_id=asset_id).order_by(AssetUsage.start_time.desc()).limit(10).all()
    atlas_info = ATLAS_OF_ASSETS.get(asset.category, {})
    return render_template('asset_detail.html', asset=asset, usage_history=usage_history, atlas_info=atlas_info)

@app.route('/rfid_event', methods=['POST'])
def rfid_event():
    """Handle RFID events from readers"""
    data = request.get_json()
    
    asset_id = data.get('asset_id')
    reader_location = data.get('location')
    event_type = data.get('event_type')  # 'enter' or 'exit'
    timestamp = data.get('timestamp')
    
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    
    if event_type == 'enter':
        # Asset entered a new location
        if asset.status == 'available' and reader_location != 'Storage':
            # Start new usage automatically
            usage = AssetUsage(
                asset_id=asset.id,
                user_id=None,  # Will be determined by context
                department=reader_location,
                start_time=datetime.fromisoformat(timestamp),
                status='active'
            )
            asset.status = 'in-use'
            asset.location = reader_location
            asset.last_usage = datetime.fromisoformat(timestamp)
            
            db.session.add(usage)
            db.session.commit()
            
            # Generate alert if needed
            check_asset_alerts(asset)
            
    elif event_type == 'exit':
        # Asset left a location
        if asset.status == 'in-use' and reader_location == 'Storage':
            # End usage automatically
            active_usage = AssetUsage.query.filter_by(
                asset_id=asset.id, 
                status='active'
            ).first()
            
            if active_usage:
                active_usage.end_time = datetime.fromisoformat(timestamp)
                active_usage.status = 'completed'
                asset.status = 'available'
                
                db.session.commit()
    
    return jsonify({'success': True})

@app.route('/scan_asset', methods=['GET', 'POST'])
@login_required
def scan_asset():
    """QR code scanning interface for asset information"""
    return render_template('scan_asset.html')

@app.route('/initiate_usage', methods=['POST'])
@login_required
def initiate_usage():
    asset_id = request.form.get('asset_id')
    expected_duration = request.form.get('expected_duration')
    patient_id = request.form.get('patient_id')
    reason = request.form.get('reason')
    
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    
    if asset and asset.status == 'available':
        # Create new usage
        usage = AssetUsage(
            asset_id=asset.id,
            user_id=current_user.id,
            expected_duration=int(expected_duration),
            patient_id=patient_id,
            reason=reason,
            department=current_user.department
        )
        
        # Update asset status
        asset.status = 'in-use'
        asset.last_usage = datetime.utcnow()
        
        db.session.add(usage)
        db.session.commit()
        
        flash(f'Usage started for {asset.name}')
        return redirect(url_for('dashboard'))
    
    flash('Unable to start usage')
    return redirect(url_for('scan_asset'))

@app.route('/end_usage/<int:usage_id>', methods=['POST'])
@login_required
def end_usage(usage_id):
    usage = AssetUsage.query.get_or_404(usage_id)
    asset = Asset.query.get(usage.asset_id)
    
    if usage.status == 'active':
        usage.end_time = datetime.utcnow()
        usage.status = 'completed'
        
        # Update asset status
        asset.status = 'available'
        
        # Check for overuse
        duration = (usage.end_time - usage.start_time).total_seconds() / 3600
        atlas_info = ATLAS_OF_ASSETS.get(asset.category, {})
        max_use = atlas_info.get('max_continuous_use', 8)
        
        if duration > max_use:
            alert = Alert(
                asset_id=asset.id,
                alert_type='overuse',
                message=f'Asset {asset.name} was used for {duration:.1f} hours (max: {max_use})',
                severity='medium'
            )
            db.session.add(alert)
        
        db.session.commit()
        flash(f'Usage ended for {asset.name}')
    
    return redirect(url_for('dashboard'))

@app.route('/reports')
@login_required
def reports():
    # Generate utilization report with realistic demo data
    assets = Asset.query.all()
    usage_records = AssetUsage.query.all()
    
    # Generate realistic department utilization data
    dept_utilization = {
        'ICU': {'usage_count': 45, 'hours': 180.5},
        'ER': {'usage_count': 32, 'hours': 128.2},
        'OR': {'usage_count': 28, 'hours': 112.8},
        'Rehab': {'usage_count': 18, 'hours': 72.4},
        'Storage': {'usage_count': 5, 'hours': 8.2}
    }
    
    # Generate realistic asset category utilization
    category_utilization = {
        'wheelchair': {'count': 25, 'in_use': 18},
        'stretcher_gurney': {'count': 12, 'in_use': 8},
        'portable_xray': {'count': 6, 'in_use': 4},
        'portable_ultrasound': {'count': 8, 'in_use': 6},
        'mobile_ecg': {'count': 10, 'in_use': 7},
        'iv_pole_wheeled': {'count': 30, 'in_use': 22},
        'mobile_vital_signs': {'count': 15, 'in_use': 12},
        'defibrillator_cart': {'count': 8, 'in_use': 2},
        'infusion_pump_stand': {'count': 20, 'in_use': 16},
        'crash_cart': {'count': 10, 'in_use': 1},
        'portable_ventilator': {'count': 6, 'in_use': 4},
        'anesthesia_cart': {'count': 4, 'in_use': 3}
    }
    
    # Realistic average usage duration
    avg_usage_duration = 4.2
    

    
    # Generate realistic rental efficiency data
    rental_roi_data = [
        {'asset': 'Infusion Pump Stand', 'rental_cost': 2500, 'rental_count': 156},
        {'asset': 'Portable Ventilator', 'rental_cost': 4500, 'rental_count': 89},
        {'asset': 'Mobile Vital Signs Monitor', 'rental_cost': 1800, 'rental_count': 234},
        {'asset': 'Portable X-Ray Machine', 'rental_cost': 8000, 'rental_count': 67},
        {'asset': 'Anesthesia Cart', 'rental_cost': 3200, 'rental_count': 123},
        {'asset': 'Crash Cart', 'rental_cost': 1200, 'rental_count': 345},
        {'asset': 'Wheelchair', 'rental_cost': 800, 'rental_count': 567},
        {'asset': 'Stretcher/Gurney', 'rental_cost': 1500, 'rental_count': 234}
    ]
    

    
    # Generate realistic lifecycle data
    lifecycle_data = [
        {'asset': 'Infusion Pump Stand #7', 'age_months': 18, 'expected_life': 60, 'remaining': 70},
        {'asset': 'Portable Ventilator Unit C', 'age_months': 42, 'expected_life': 48, 'remaining': 12},
        {'asset': 'Mobile Vital Signs Monitor D', 'age_months': 24, 'expected_life': 72, 'remaining': 67},
        {'asset': 'Defibrillator Cart #1', 'age_months': 36, 'expected_life': 84, 'remaining': 57},
        {'asset': 'Anesthesia Cart #3', 'age_months': 54, 'expected_life': 60, 'remaining': 10},
        {'asset': 'Portable X-Ray Machine A', 'age_months': 12, 'expected_life': 96, 'remaining': 88},
        {'asset': 'Crash Cart #2', 'age_months': 30, 'expected_life': 48, 'remaining': 38},
        {'asset': 'Wheelchair #5', 'age_months': 48, 'expected_life': 72, 'remaining': 33},
        {'asset': 'Stretcher/Gurney #3', 'age_months': 22, 'expected_life': 60, 'remaining': 63},
        {'asset': 'Mobile ECG Machine B', 'age_months': 66, 'expected_life': 72, 'remaining': 8},
        {'asset': 'Portable Ultrasound A', 'age_months': 15, 'expected_life': 84, 'remaining': 82},
        {'asset': 'IV Pole #4', 'age_months': 28, 'expected_life': 48, 'remaining': 42}
    ]
    
    # Generate meaningful asset statistics
    asset_stats = {
        'total_assets': 70000,
        'scanned_assets': 45600,
        'unscanned_assets': 24400,
        'active_use': 30700,
        'under_utilized': 15400,
        'maintenance': 13650,
        'available': 10250,
        'total_asset_value': 4850000000,  # $4.85B
        'rental_assets': 20500,
        'owned_assets': 49500,
        'rental_monthly_cost': 77000000,  # $77M/month
        'asset_categories': {
            'Infusion Pumps': 13650,
            'Ventilators': 10250,
            'Monitors': 17100,
            'Wheelchairs': 8550,
            'X-Ray Machines': 6850,
            'Other': 13650
        },
        'department_distribution': {
            'ICU': 20500,
            'ER': 13650,
            'OR': 10250,
            'Radiology': 6850,
            'Storage': 18750
        }
    }
    
    # Calculate realistic utilization rate based on asset_stats
    total_assets = asset_stats['total_assets']  # 70,000 total assets
    active_use_assets = asset_stats['active_use']  # 30,700 assets in active use
    utilization_rate = (active_use_assets / total_assets * 100) if total_assets > 0 else 43.9
    
    # Generate maintenance data
    maintenance_data = {
        'status_overview': {
            'Operational': 45600,
            'Under Maintenance': 8500,
            'Scheduled Maintenance': 5150,
            'Out of Service': 1750
        },
        'scheduled_maintenance': {
            'This Week': 1250,
            'Next Week': 2100,
            'This Month': 3800,
            'Next Month': 4200
        },
        'maintenance_alerts': {
            'Critical': 850,
            'High Priority': 1250,
            'Medium Priority': 2100,
            'Low Priority': 3450
        }
    }
    
    # Generate cost optimization data for capital budget decisions
    cost_optimization_data = {
        'cost_savings_opportunities': {
            'underutilized_assets': {
                'count': 15400,
                'potential_savings': 38500000,  # $38.5M
                'description': 'Assets used <50% of available time'
            },
            'maintenance_optimization': {
                'count': 8500,
                'potential_savings': 12750000,  # $12.75M
                'description': 'Preventive vs reactive maintenance'
            },
            'rental_vs_purchase': {
                'count': 20500,
                'potential_savings': 61500000,  # $61.5M
                'description': 'Convert high-usage rentals to purchases'
            }
        },
        'capital_budget_insights': {
            'replacement_needed': {
                'count': 8500,
                'estimated_cost': 170000000,  # $170M
                'priority': 'High',
                'description': 'Assets reaching end of life'
            },
            'upgrade_opportunities': {
                'count': 12000,
                'estimated_cost': 96000000,  # $96M
                'priority': 'Medium',
                'description': 'Technology upgrades for efficiency'
            },
            'consolidation_opportunities': {
                'count': 6800,
                'estimated_cost': 34000000,  # $34M
                'priority': 'Medium',
                'description': 'Consolidate similar equipment',
                'evidence': {
                    'duplicate_equipment': {
                        'infusion_pumps': 1250,  # Multiple brands/models doing same job
                        'monitors': 980,         # Different monitor types with overlap
                        'ventilators': 450,      # Various ventilator models
                        'xray_machines': 320,    # Portable vs stationary overlap
                        'ultrasound': 280,       # Different ultrasound units
                        'ecg_machines': 420,     # Multiple ECG models
                        'defibrillators': 380,   # Various defibrillator types
                        'anesthesia_carts': 290, # Different anesthesia setups
                        'crash_carts': 520,      # Multiple crash cart configurations
                        'wheelchairs': 890,      # Various wheelchair types
                        'stretchers': 610        # Different stretcher models
                    },
                    'consolidation_benefits': {
                        'reduced_maintenance': 8500000,    # $8.5M savings
                        'standardized_training': 3200000,  # $3.2M savings
                        'bulk_purchasing': 12000000,       # $12M savings
                        'reduced_inventory': 6800000,      # $6.8M savings
                        'improved_efficiency': 3500000     # $3.5M savings
                    },
                    'methodology': [
                        'Equipment overlap analysis across departments',
                        'Usage pattern comparison for similar equipment',
                        'Maintenance cost analysis by equipment type',
                        'Training requirements assessment',
                        'Inventory management optimization',
                        'Standardization feasibility study',
                        'Cost-benefit analysis of consolidation',
                        'Implementation timeline planning'
                    ],
                    'examples': [
                        'Replace 5 different infusion pump models with 2 standardized models',
                        'Consolidate 8 monitor types into 4 core models',
                        'Standardize ventilator fleet from 6 models to 3',
                        'Reduce X-ray machine variety from 4 types to 2',
                        'Unify ultrasound equipment from 5 models to 3'
                    ]
                }
            }
        },
        'monthly_cost_breakdown': {
            'rental_costs': 77000000,  # $77M
            'maintenance_costs': 25500000,  # $25.5M
            'insurance_costs': 8500000,  # $8.5M
            'total_monthly': 111000000  # $111M (removed energy costs)
        },
        'performance_metrics': {
            'rental_assets': {
                'monthly_cost': 77000000,
                'utilization_rate': 65,
                'recommendation': 'Monitor usage patterns for optimization'
            },
            'owned_assets': {
                'monthly_cost': 52000000,
                'utilization_rate': 78,
                'recommendation': 'Good utilization, maintain current strategy'
            }
        },
        'department_cost_analysis': {
            'ICU': {'monthly_cost': 38500000, 'utilization': 85, 'efficiency_score': 92},
            'ER': {'monthly_cost': 25800000, 'utilization': 72, 'efficiency_score': 78},
            'OR': {'monthly_cost': 19300000, 'utilization': 88, 'efficiency_score': 95},
            'Radiology': {'monthly_cost': 12900000, 'utilization': 65, 'efficiency_score': 71},
            'Storage': {'monthly_cost': 6450000, 'utilization': 45, 'efficiency_score': 52}
        },
        'rental_utilization_tracking': {
            'total_rented': 20500,
            'actively_used': 13325,  # 65% utilization
            'not_used': 7175,  # 35% not used
            'underutilized': 4100,  # 20% underutilized
            'rental_periods': {
                'daily': 8200,
                'weekly': 6150,
                'monthly': 6150
            },
            'unused_assets_by_period': {
                'daily': 2870,  # 35% of daily rentals unused
                'weekly': 2153,  # 35% of weekly rentals unused
                'monthly': 2153   # 35% of monthly rentals unused
            },
            'potential_losses': {
                'daily': 2870000,  # $2.87M daily losses
                'weekly': 10765000,  # $10.77M weekly losses
                'monthly': 43060000   # $43.06M monthly losses
            },
                            'unused_asset_details': [
                    {'asset_id': 'RENTAL_001', 'name': 'Infusion Pump Stand', 'rental_start': '2024-01-15', 'rental_end': '2024-02-15', 'days_unused': 12, 'daily_cost': 2500, 'total_loss': 30000, 'action': 'Return immediately'},
                    {'asset_id': 'RENTAL_002', 'name': 'Portable Ventilator', 'rental_start': '2024-01-10', 'rental_end': '2024-02-10', 'days_unused': 18, 'daily_cost': 4500, 'total_loss': 81000, 'action': 'Cancel rental'},
                    {'asset_id': 'RENTAL_003', 'name': 'Mobile Vital Signs Monitor', 'rental_start': '2024-01-20', 'rental_end': '2024-02-20', 'days_unused': 8, 'daily_cost': 1800, 'total_loss': 14400, 'action': 'Reassign to active use'},
                    {'asset_id': 'RENTAL_004', 'name': 'Portable X-Ray Machine', 'rental_start': '2024-01-05', 'rental_end': '2024-02-05', 'days_unused': 25, 'daily_cost': 8000, 'total_loss': 200000, 'action': 'Return immediately'},
                    {'asset_id': 'RENTAL_005', 'name': 'Anesthesia Cart', 'rental_start': '2024-01-12', 'rental_end': '2024-02-12', 'days_unused': 15, 'daily_cost': 3200, 'total_loss': 48000, 'action': 'Cancel rental'}
                ],
                'expiring_rentals': {
                    'expiring_this_week': 1250,
                    'expiring_next_week': 2100,
                    'expiring_this_month': 3800,
                    'total_expiring_soon': 7150,
                    'expiring_assets': [
                        {'asset_id': 'RENTAL_101', 'name': 'ICU Ventilator', 'rental_end': '2024-02-28', 'days_remaining': 3, 'daily_cost': 5000, 'status': 'Not Scanned', 'action': 'Return or Extend'},
                        {'asset_id': 'RENTAL_102', 'name': 'Portable Monitor', 'rental_end': '2024-03-02', 'days_remaining': 7, 'daily_cost': 2000, 'status': 'Scanned', 'action': 'Review Usage'},
                        {'asset_id': 'RENTAL_103', 'name': 'Infusion Pump', 'rental_end': '2024-03-05', 'days_remaining': 10, 'daily_cost': 1500, 'status': 'Not Scanned', 'action': 'Return or Extend'},
                        {'asset_id': 'RENTAL_104', 'name': 'X-Ray Machine', 'rental_end': '2024-03-10', 'days_remaining': 15, 'daily_cost': 8000, 'status': 'Scanned', 'action': 'Review Usage'},
                        {'asset_id': 'RENTAL_105', 'name': 'Anesthesia Cart', 'rental_end': '2024-03-15', 'days_remaining': 20, 'daily_cost': 3000, 'status': 'Not Scanned', 'action': 'Return or Extend'}
                    ]
                }
        }
    }
    
    return render_template('reports.html', 
                         dept_utilization=dept_utilization,
                         category_utilization=category_utilization,
                         utilization_rate=utilization_rate,
                         avg_usage_duration=avg_usage_duration,
                         total_assets=total_assets,
                         rental_roi_data=rental_roi_data,
                         lifecycle_data=lifecycle_data,
                         asset_stats=asset_stats,
                         maintenance_data=maintenance_data,
                         cost_optimization_data=cost_optimization_data) 

@app.route('/api/assets')
@login_required
def api_assets():
    assets = Asset.query.all()
    return jsonify([{
        'id': asset.id,
        'asset_id': asset.asset_id,
        'name': asset.name,
        'status': asset.status,
        'location': asset.location
    } for asset in assets])

@app.route('/api/scan/<asset_id>')
@login_required
def api_scan_asset(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if asset:
        atlas_info = ATLAS_OF_ASSETS.get(asset.category, {})
        return jsonify({
            'found': True,
            'asset': {
                'id': asset.id,
                'name': asset.name,
                'category': asset.category,
                'status': asset.status,
                'ownership': asset.ownership
            },
            'atlas_info': atlas_info
        })
    return jsonify({'found': False})

@app.route('/register_asset', methods=['GET', 'POST'])
@login_required
def register_asset():
    if request.method == 'POST':
        try:
            # Get form data
            asset_type = request.form.get('asset_type')
            serial_number = request.form.get('serial_number')
            ownership_type = request.form.get('ownership_type')
            manufacturer = request.form.get('manufacturer')
            vendor = request.form.get('vendor')
            rental_rate = float(request.form.get('rental_rate', 0)) if request.form.get('rental_rate') else 0
            initial_location = request.form.get('initial_location', 'Storage')
            purchase_date_str = request.form.get('purchase_date')
            notes = request.form.get('notes', '')
            
            # Parse purchase date
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d') if purchase_date_str else datetime.now()
            
            # Generate unique asset ID based on ownership type
            if ownership_type == 'rental':
                asset_id = f"RENTAL_{serial_number[-6:]}_{datetime.now().strftime('%Y%m%d')}"
                status = 'unassociated'  # Start as unassociated for rentals
            else:
                asset_id = f"HOSP_{serial_number[-6:]}_{datetime.now().strftime('%Y%m%d')}"
                status = 'available'  # Start as available for hospital owned
            
            # Create new asset
            new_asset = Asset(
                asset_id=asset_id,
                name=f"{asset_type} - {serial_number}",
                category=asset_type.lower().replace(' ', '_'),
                status=status,
                ownership=ownership_type,
                location=initial_location,
                manufacturer=manufacturer,
                vendor=vendor if ownership_type == 'rental' else None,
                rental_rate=rental_rate if ownership_type == 'rental' else None,
                purchase_date=purchase_date,
                expected_lifespan=60,  # Default 5 years
                qr_code=generate_qr_code(asset_id)
            )
            
            db.session.add(new_asset)
            db.session.commit()
            
            if ownership_type == 'rental':
                flash(f'Rental asset {asset_id} registered successfully! Status: Unassociated', 'success')
            else:
                flash(f'Hospital owned asset {asset_id} registered successfully! Status: Available', 'success')
            
            return redirect(url_for('register_asset'))
            
        except Exception as e:
            flash(f'Error registering asset: {str(e)}', 'error')
            return redirect(url_for('register_asset'))
    
    # Get existing unassociated rentals for display
    unassociated_rentals = Asset.query.filter_by(ownership='rental', status='unassociated').all()
    
    # Get today's date for the purchase date field
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('register_asset.html', unassociated_rentals=unassociated_rentals, today_date=today_date)

@app.route('/associate_rental/<int:asset_id>', methods=['POST'])
@login_required
def associate_rental(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)
        asset.status = 'available'
        db.session.commit()
        flash(f'Rental asset {asset.asset_id} has been associated and is now available for use!', 'success')
    except Exception as e:
        flash(f'Error associating asset: {str(e)}', 'error')
    
    return redirect(url_for('register_asset'))

@app.route('/delete_rental/<int:asset_id>', methods=['POST'])
@login_required
def delete_rental(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)
        db.session.delete(asset)
        db.session.commit()
        flash(f'Rental asset {asset.asset_id} has been removed from the system.', 'success')
    except Exception as e:
        flash(f'Error deleting asset: {str(e)}', 'error')
    
    return redirect(url_for('register_asset'))

@app.route('/asset_management_dashboard')
@login_required
def asset_management_dashboard():
    """Complete Asset Management Dashboard with workflow tracking"""
    
    # Get all assets from database
    assets = Asset.query.all()
    
    # Separate scanned and unscanned assets
    scanned_assets = [asset for asset in assets if asset.status != 'unassociated']
    unscanned_assets = [asset for asset in assets if asset.status == 'unassociated']
    
    # Define asset_stats (same as in reports route)
    asset_stats = {
        'total_assets': 70000,
        'scanned_assets': 45600,
        'unscanned_assets': 24400,
        'active_use': 27300,
        'under_utilized': 18300,
        'maintenance': 5600,
        'available': 18800,
        'total_asset_value': 850000000,  # $850M
        'rental_assets': 19100,
        'owned_assets': 50900,
        'rental_monthly_cost': 77000000  # $77M
    }
    
    # Generate vendor analytics data
    vendor_stats = {
        'total_vendors': 15,
        'total_monthly_spend': 125000000,  # $125M
        'contracts_expiring_soon': 4,
        'total_assets_managed': 67800,
        'top_rental_department': 'ICU',
        'top_rental_count': 8200,
        'most_diverse_vendor': 'MedEquip Solutions',
        'vendor_asset_types': 12
    }
    
    # Department rental distribution data
    department_rental_distribution = {
        'ICU': 8200,
        'ER': 6800,
        'OR': 5200,
        'Radiology': 3800,
        'Cardiology': 2900,
        'Neurology': 2100,
        'Pediatrics': 1800,
        'Oncology': 1500
    }
    
    vendor_performance = [
        {
            'name': 'MedEquip Solutions',
            'asset_count': 8200,
            'monthly_cost': 28500000,  # $28.5M
            'contract_end': '2024-12-31',
            'days_to_expiry': 285,
            'utilization': 88,
            'rating': 5,
            'specialization': 'ICU Equipment',
            'response_time': '2 hours',
            'asset_types': ['Ventilators', 'Monitors', 'Infusion Pumps', 'Defibrillators', 'Ultrasound', 'X-Ray', 'ECG', 'Anesthesia', 'Crash Carts', 'Wheelchairs', 'Stretchers', 'IV Poles']
        },
        {
            'name': 'Healthcare Rentals Inc',
            'asset_count': 7100,
            'monthly_cost': 24500000,  # $24.5M
            'contract_end': '2024-06-15',
            'days_to_expiry': 25,
            'utilization': 82,
            'rating': 5,
            'specialization': 'Surgical Equipment',
            'response_time': '4 hours',
            'asset_types': ['Surgical Tables', 'Anesthesia Machines', 'Surgical Lights', 'Electrosurgical Units', 'Endoscopes', 'Laparoscopes', 'Surgical Instruments', 'Patient Monitors']
        },
        {
            'name': 'Medical Supply Co',
            'asset_count': 6800,
            'monthly_cost': 22500000,  # $22.5M
            'contract_end': '2024-08-20',
            'days_to_expiry': 91,
            'utilization': 79,
            'rating': 4,
            'specialization': 'Diagnostic Equipment',
            'response_time': '6 hours',
            'asset_types': ['X-Ray Machines', 'CT Scanners', 'MRI Machines', 'Ultrasound', 'ECG Machines', 'Blood Analyzers', 'Microscopes', 'Lab Equipment']
        },
        {
            'name': 'Equipment Partners',
            'asset_count': 6200,
            'monthly_cost': 20500000,  # $20.5M
            'contract_end': '2024-07-10',
            'days_to_expiry': 51,
            'utilization': 75,
            'rating': 4,
            'specialization': 'Emergency Equipment',
            'response_time': '3 hours',
            'asset_types': ['Defibrillators', 'Ventilators', 'Patient Monitors', 'Infusion Pumps', 'Crash Carts', 'Stretchers', 'Emergency Lights', 'Trauma Equipment']
        },
        {
            'name': 'Rental Solutions',
            'asset_count': 5800,
            'monthly_cost': 18500000,  # $18.5M
            'contract_end': '2024-09-30',
            'days_to_expiry': 133,
            'utilization': 72,
            'rating': 4,
            'specialization': 'General Equipment',
            'response_time': '8 hours',
            'asset_types': ['General Monitors', 'Basic Equipment', 'Standard Devices', 'Common Tools', 'Rental Equipment', 'General Solutions']
        },
        {
            'name': 'Advanced Medical Equipment',
            'asset_count': 5200,
            'monthly_cost': 16500000,  # $16.5M
            'contract_end': '2024-05-25',
            'days_to_expiry': 15,
            'utilization': 70,
            'rating': 4,
            'specialization': 'Specialized Equipment',
            'response_time': '5 hours',
            'asset_types': ['Advanced Monitors', 'Specialized Devices', 'Complex Equipment', 'Advanced Tools', 'Specialized Solutions', 'Advanced Technology']
        },
        {
            'name': 'Precision Healthcare',
            'asset_count': 4800,
            'monthly_cost': 14500000,  # $14.5M
            'contract_end': '2024-11-15',
            'days_to_expiry': 229,
            'utilization': 68,
            'rating': 3,
            'specialization': 'Precision Equipment',
            'response_time': '7 hours',
            'asset_types': ['Precision Scales', 'Calibration Equipment', 'Measurement Tools', 'Testing Equipment', 'Quality Control Devices', 'Laboratory Instruments']
        },
        {
            'name': 'Elite Medical Rentals',
            'asset_count': 4400,
            'monthly_cost': 12500000,  # $12.5M
            'contract_end': '2024-10-05',
            'days_to_expiry': 158,
            'utilization': 65,
            'rating': 3,
            'specialization': 'Elite Equipment',
            'response_time': '6 hours',
            'asset_types': ['Elite Monitors', 'Premium Ventilators', 'Advanced Imaging', 'Specialty Beds', 'High-End Equipment', 'Luxury Medical Devices']
        },
        {
            'name': 'ProCare Equipment',
            'asset_count': 4100,
            'monthly_cost': 11500000,  # $11.5M
            'contract_end': '2024-06-30',
            'days_to_expiry': 40,
            'utilization': 63,
            'rating': 3,
            'specialization': 'Pro Care Equipment',
            'response_time': '9 hours',
            'asset_types': ['Patient Care Beds', 'Nursing Equipment', 'Caregiving Tools', 'Patient Monitors', 'Mobility Aids', 'Care Equipment']
        },
        {
            'name': 'MedTech Solutions',
            'asset_count': 3800,
            'monthly_cost': 10500000,  # $10.5M
            'contract_end': '2024-08-15',
            'days_to_expiry': 86,
            'utilization': 60,
            'rating': 3,
            'specialization': 'Technology Equipment',
            'response_time': '4 hours',
            'asset_types': ['Digital Monitors', 'Smart Devices', 'IoT Equipment', 'Connected Devices', 'Tech Solutions', 'Digital Tools']
        },
        {
            'name': 'Healthcare Innovations',
            'asset_count': 3500,
            'monthly_cost': 9500000,  # $9.5M
            'contract_end': '2024-07-25',
            'days_to_expiry': 66,
            'utilization': 58,
            'rating': 3,
            'specialization': 'Innovative Equipment',
            'response_time': '8 hours',
            'asset_types': ['Innovative Devices', 'Cutting-Edge Equipment', 'New Technology', 'Experimental Tools', 'Research Equipment', 'Innovation Labs']
        },
        {
            'name': 'Medical Excellence',
            'asset_count': 3200,
            'monthly_cost': 8500000,  # $8.5M
            'contract_end': '2024-09-10',
            'days_to_expiry': 113,
            'utilization': 55,
            'rating': 2,
            'specialization': 'Excellence Equipment',
            'response_time': '10 hours',
            'asset_types': ['Excellence Monitors', 'Premium Equipment', 'Quality Devices', 'High-Standard Tools', 'Excellence Solutions', 'Premium Care']
        },
        {
            'name': 'Care Equipment Plus',
            'asset_count': 2900,
            'monthly_cost': 7500000,  # $7.5M
            'contract_end': '2024-06-20',
            'days_to_expiry': 30,
            'utilization': 52,
            'rating': 2,
            'specialization': 'Care Equipment',
            'response_time': '12 hours',
            'asset_types': ['Care Beds', 'Patient Monitors', 'Caregiving Tools', 'Mobility Equipment', 'Care Solutions', 'Patient Care']
        },
        {
            'name': 'HealthTech Rentals',
            'asset_count': 2600,
            'monthly_cost': 6500000,  # $6.5M
            'contract_end': '2024-08-05',
            'days_to_expiry': 76,
            'utilization': 48,
            'rating': 2,
            'specialization': 'Health Tech Equipment',
            'response_time': '15 hours',
            'asset_types': ['Health Monitors', 'Tech Devices', 'Digital Equipment', 'Smart Monitors', 'Health Solutions', 'Tech Tools']
        },
        {
            'name': 'Medical Partners Co',
            'asset_count': 2300,
            'monthly_cost': 5500000,  # $5.5M
            'contract_end': '2024-07-01',
            'days_to_expiry': 41,
            'utilization': 45,
            'rating': 2,
            'specialization': 'Partner Equipment',
            'response_time': '18 hours',
            'asset_types': ['Partner Devices', 'Collaborative Equipment', 'Shared Tools', 'Joint Solutions', 'Partner Monitors', 'Cooperative Equipment']
        }
    ]
    
    # Generate active rentals with contract data
    active_rentals = [
        {
            'id': 1,
            'asset_id': 'RENTAL_001',
            'name': 'ICU Ventilator',
            'vendor': 'MedEquip Solutions',
            'contract_start': '2024-01-15',
            'contract_end': '2024-03-15',
            'daily_rate': 5000,
            'days_remaining': 3
        },
        {
            'id': 2,
            'asset_id': 'RENTAL_002',
            'name': 'Portable Monitor',
            'vendor': 'Healthcare Rentals Inc',
            'contract_start': '2024-01-20',
            'contract_end': '2024-03-20',
            'daily_rate': 2000,
            'days_remaining': 8
        },
        {
            'id': 3,
            'asset_id': 'RENTAL_003',
            'name': 'Infusion Pump',
            'vendor': 'Medical Supply Co',
            'contract_start': '2024-01-25',
            'contract_end': '2024-03-25',
            'daily_rate': 1500,
            'days_remaining': 13
        },
        {
            'id': 4,
            'asset_id': 'RENTAL_004',
            'name': 'X-Ray Machine',
            'vendor': 'Equipment Partners',
            'contract_start': '2024-02-01',
            'contract_end': '2024-04-01',
            'daily_rate': 8000,
            'days_remaining': 18
        },
        {
            'id': 5,
            'asset_id': 'RENTAL_005',
            'name': 'Anesthesia Cart',
            'vendor': 'Rental Solutions',
            'contract_start': '2024-02-05',
            'contract_end': '2024-04-05',
            'daily_rate': 3000,
            'days_remaining': 23
        }
    ]
    
    # Generate expiring rentals data
    expiring_rentals = {
        'total_expiring_soon': 7150,
        'expiring_this_week': 1250,
        'expiring_next_week': 2100,
        'expiring_this_month': 3800
    }
    
    # Generate pending workflow actions
    pending_actions = [
        {
            'id': 1,
            'title': 'Return Expiring Ventilators',
            'description': '15 ICU ventilators expiring this week need immediate return or extension',
            'due_date': '2024-03-15',
            'priority': 'high'
        },
        {
            'id': 2,
            'title': 'Bulk Scan Unscanned Assets',
            'description': '24,400 assets need to be scanned and added to tracking system',
            'due_date': '2024-03-20',
            'priority': 'medium'
        },
        {
            'id': 3,
            'title': 'Review Vendor Performance',
            'description': 'Monthly vendor performance review and contract negotiations',
            'due_date': '2024-03-25',
            'priority': 'medium'
        },
        {
            'id': 4,
            'title': 'Update Asset Locations',
            'description': 'Update location data for 1,250 assets that have been moved',
            'due_date': '2024-03-30',
            'priority': 'low'
        }
    ]
    
    # Generate workflow metrics
    workflow_metrics = {
        'assets_scanned_today': 156,
        'rentals_returned_today': 23,
        'maintenance_completed': 8,
        'total_actions_pending': 12
    }
    
    # Generate advanced metrics for complex workflow demonstration
    advanced_metrics = {
        'total_assets_managed': 70000,
        'total_cost_savings': '$2.8M',
        'chaos_resolution_rate': '94%',
        'total_security_incidents': 0,
        'predictive_accuracy': '89%',
        'compliance_score': '98%',
        'vendor_optimization_savings': '$1.2M',
        'maintenance_optimization_savings': '$850K',
        'rental_vs_purchase_savings': '$750K'
    }
    
    # Generate lifecycle alerts data with detailed evidence
    lifecycle_alerts = {
        'critical_assets': 1250,  # Assets with <20% life remaining
        'warning_assets': 2100,   # Assets with 20-50% life remaining
        'attention_assets': 3800, # Assets with 50-80% life remaining
        'healthy_assets': 62850,  # Assets with >80% life remaining
        'total_replacement_cost': 85000000,  # $85M estimated replacement cost
        'critical_assets_by_category': {
            'Infusion Pumps': 450,
            'Ventilators': 320,
            'Monitors': 280,
            'X-Ray Machines': 120,
            'Ultrasound': 80
        },
        'replacement_recommendations': [
            {
                'category': 'Infusion Pumps',
                'count': 450,
                'estimated_cost': 13500000,  # $13.5M
                'priority': 'Critical',
                'reason': 'Safety critical equipment reaching end of life',
                'evidence': {
                    'avg_age_months': 58,
                    'expected_life_months': 60,
                    'maintenance_issues': 156,
                    'safety_incidents': 12,
                    'compliance_status': 'At Risk',
                    'usage_hours': 28450,
                    'reliability_score': 67,
                    'last_maintenance': '2024-01-15',
                    'next_maintenance': '2024-02-15',
                    'warranty_expiry': '2024-03-01',
                    'regulatory_updates': 'FDA Alert 2024-001',
                    'performance_trend': 'Declining',
                    'cost_per_hour': 2.45,
                    'efficiency_rating': 72
                }
            },
            {
                'category': 'Ventilators',
                'count': 320,
                'estimated_cost': 19200000,  # $19.2M
                'priority': 'Critical',
                'reason': 'Life support equipment requires immediate replacement',
                'evidence': {
                    'avg_age_months': 42,
                    'expected_life_months': 48,
                    'maintenance_issues': 89,
                    'safety_incidents': 8,
                    'compliance_status': 'Critical',
                    'usage_hours': 18920,
                    'reliability_score': 58,
                    'last_maintenance': '2024-01-20',
                    'next_maintenance': '2024-02-20',
                    'warranty_expiry': '2024-04-15',
                    'regulatory_updates': 'JCAHO Standard 2024-02',
                    'performance_trend': 'Critical Decline',
                    'cost_per_hour': 4.20,
                    'efficiency_rating': 65
                }
            },
            {
                'category': 'Patient Monitors',
                'count': 280,
                'estimated_cost': 8400000,   # $8.4M
                'priority': 'High',
                'reason': 'Monitoring equipment showing reliability issues',
                'evidence': {
                    'avg_age_months': 36,
                    'expected_life_months': 72,
                    'maintenance_issues': 234,
                    'safety_incidents': 15,
                    'compliance_status': 'Warning',
                    'usage_hours': 32150,
                    'reliability_score': 74,
                    'last_maintenance': '2024-01-10',
                    'next_maintenance': '2024-03-10',
                    'warranty_expiry': '2024-06-01',
                    'regulatory_updates': 'ISO 13485 Update',
                    'performance_trend': 'Stable',
                    'cost_per_hour': 1.85,
                    'efficiency_rating': 78
                }
            },
            {
                'category': 'X-Ray Machines',
                'count': 120,
                'estimated_cost': 24000000,  # $24M
                'priority': 'Medium',
                'reason': 'Imaging equipment approaching end of life',
                'evidence': {
                    'avg_age_months': 84,
                    'expected_life_months': 96,
                    'maintenance_issues': 67,
                    'safety_incidents': 3,
                    'compliance_status': 'Compliant',
                    'usage_hours': 15680,
                    'reliability_score': 82,
                    'last_maintenance': '2024-01-05',
                    'next_maintenance': '2024-04-05',
                    'warranty_expiry': '2024-08-01',
                    'regulatory_updates': 'Radiation Safety Update',
                    'performance_trend': 'Gradual Decline',
                    'cost_per_hour': 8.50,
                    'efficiency_rating': 85
                }
            },
            {
                'category': 'Ultrasound',
                'count': 80,
                'estimated_cost': 9600000,   # $9.6M
                'priority': 'Medium',
                'reason': 'Diagnostic equipment needs upgrade',
                'evidence': {
                    'avg_age_months': 72,
                    'expected_life_months': 84,
                    'maintenance_issues': 45,
                    'safety_incidents': 2,
                    'compliance_status': 'Compliant',
                    'usage_hours': 12450,
                    'reliability_score': 88,
                    'last_maintenance': '2024-01-12',
                    'next_maintenance': '2024-04-12',
                    'warranty_expiry': '2024-09-01',
                    'regulatory_updates': 'AI Diagnostic Standards',
                    'performance_trend': 'Stable',
                    'cost_per_hour': 6.20,
                    'efficiency_rating': 82
                }
            }
        ],
        'unscanned_assets_evidence': {
            'total_unscanned': 24400,
            'estimated_critical': 3200,
            'estimated_warning': 5400,
            'estimated_attention': 7800,
            'estimated_healthy': 8000,
            'evidence_sources': [
                'Historical maintenance records',
                'Purchase date analysis',
                'Vendor service history',
                'Usage pattern analysis',
                'Industry reliability data',
                'Regulatory compliance records',
                'Performance benchmarking',
                'Cost-benefit analysis'
            ]
        }
    }
    
    return render_template('asset_management_dashboard.html',
                         asset_stats=asset_stats,
                         scanned_assets=scanned_assets,
                         unscanned_assets=unscanned_assets,
                         vendor_stats=vendor_stats,
                         vendor_performance=vendor_performance,
                         department_rental_distribution=department_rental_distribution,
                         active_rentals=active_rentals,
                         expiring_rentals=expiring_rentals,
                         pending_actions=pending_actions,
                         workflow_metrics=workflow_metrics,
                         advanced_metrics=advanced_metrics,
                         lifecycle_alerts=lifecycle_alerts)

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/static/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

@app.route('/return_rental/<int:rental_id>', methods=['POST'])
@login_required
def return_rental(rental_id):
    """Return a rental asset"""
    try:
        data = request.get_json()
        reason = data.get('reason')
        return_date = data.get('return_date')
        notes = data.get('notes')
        
        # In a real application, you would update the database
        # For demo purposes, we'll just return success
        
        return jsonify({
            'success': True,
            'message': f'Rental {rental_id} returned successfully',
            'return_date': return_date,
            'reason': reason
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample data if database is empty
        if not User.query.first():
            # Create admin user
            admin = User(
                username='admin',
                email='admin@hospital.com',
                password_hash=generate_password_hash('admin123'),
                department='IT',
                role='admin'
            )
            db.session.add(admin)
            
            # Create comprehensive sample assets
            sample_assets = [
                # Wheelchairs
                        Asset(asset_id='WC001', name='Wheelchair #1', category='wheelchair', ownership='hospital', status='available', location='Storage', manufacturer='Invacare Corporation'),
        Asset(asset_id='WC002', name='Wheelchair #2', category='wheelchair', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=2), manufacturer='Invacare Corporation'),
        Asset(asset_id='WC003', name='Wheelchair #3', category='wheelchair', ownership='hospital', status='available', location='Rehab', last_usage=datetime.now() - timedelta(hours=6), manufacturer='Sunrise Medical'),
        Asset(asset_id='WC004', name='Wheelchair #4', category='wheelchair', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=1), manufacturer='Sunrise Medical'),
        Asset(asset_id='WC005', name='Wheelchair #5', category='wheelchair', ownership='rental', vendor='Mobility Plus', status='available', location='Storage', manufacturer='Pride Mobility'),
                
                # Stretchers & Gurneys
                        Asset(asset_id='SG001', name='Stretcher/Gurney #1', category='stretcher_gurney', ownership='hospital', status='available', location='Storage', manufacturer='Stryker Corporation'),
        Asset(asset_id='SG002', name='Stretcher/Gurney #2', category='stretcher_gurney', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1), manufacturer='Stryker Corporation'),
        Asset(asset_id='SG003', name='Stretcher/Gurney #3', category='stretcher_gurney', ownership='hospital', status='in-use', location='OR', last_usage=datetime.now() - timedelta(hours=3), manufacturer='Hill-Rom'),
        Asset(asset_id='SG004', name='Stretcher/Gurney #4', category='stretcher_gurney', ownership='rental', vendor='MedEquip Inc', status='available', location='Storage', manufacturer='Hill-Rom'),
                
                # Portable X-Ray Machines
                        Asset(asset_id='PXR001', name='Portable X-Ray Machine A', category='portable_xray', ownership='hospital', status='available', location='Storage', manufacturer='GE Healthcare'),
        Asset(asset_id='PXR002', name='Portable X-Ray Machine B', category='portable_xray', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=1), manufacturer='GE Healthcare'),
        Asset(asset_id='PXR003', name='Portable X-Ray Machine C', category='portable_xray', ownership='rental', vendor='Radiology Solutions', status='maintenance', location='Radiology', last_usage=datetime.now() - timedelta(days=2), manufacturer='Siemens Healthineers'),
        Asset(asset_id='PXR004', name='Portable X-Ray Machine D', category='portable_xray', ownership='hospital', status='available', location='Storage', manufacturer='Philips Healthcare'),
                
                # Portable Ultrasound
                Asset(asset_id='PUS001', name='Portable Ultrasound A', category='portable_ultrasound', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=30)),
                Asset(asset_id='PUS002', name='Portable Ultrasound B', category='portable_ultrasound', ownership='rental', vendor='MedTech Pro', status='available', location='Storage', last_usage=datetime.now() - timedelta(days=1)),
                Asset(asset_id='PUS003', name='Portable Ultrasound C', category='portable_ultrasound', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=3)),
                
                # Mobile ECG Machines
                Asset(asset_id='MECG001', name='Mobile ECG Machine A', category='mobile_ecg', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=2)),
                Asset(asset_id='MECG002', name='Mobile ECG Machine B', category='mobile_ecg', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=3)),
                Asset(asset_id='MECG003', name='Mobile ECG Machine C', category='mobile_ecg', ownership='rental', vendor='CardioCare Inc', status='available', location='Storage', last_usage=datetime.now() - timedelta(hours=12)),
                Asset(asset_id='MECG004', name='Mobile ECG Machine D', category='mobile_ecg', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1)),
                
                # IV Poles
                Asset(asset_id='IVP001', name='IV Pole #1', category='iv_pole_wheeled', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=4)),
                Asset(asset_id='IVP002', name='IV Pole #2', category='iv_pole_wheeled', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(hours=8)),
                Asset(asset_id='IVP003', name='IV Pole #3', category='iv_pole_wheeled', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1)),
                Asset(asset_id='IVP004', name='IV Pole #4', category='iv_pole_wheeled', ownership='hospital', status='available', location='Storage'),
                Asset(asset_id='IVP005', name='IV Pole #5', category='iv_pole_wheeled', ownership='rental', vendor='InfusionCare Pro', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=2)),
                
                # Mobile Vital Signs Monitors
                Asset(asset_id='MVSM001', name='Mobile Vital Signs Monitor A', category='mobile_vital_signs', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=1)),
                Asset(asset_id='MVSM002', name='Mobile Vital Signs Monitor B', category='mobile_vital_signs', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(hours=6)),
                Asset(asset_id='MVSM003', name='Mobile Vital Signs Monitor C', category='mobile_vital_signs', ownership='rental', vendor='VitalTech Solutions', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=2)),
                Asset(asset_id='MVSM004', name='Mobile Vital Signs Monitor D', category='mobile_vital_signs', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=1)),
                
                # Defibrillator Carts
                Asset(asset_id='DC001', name='Defibrillator Cart #1', category='defibrillator_cart', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1)),
                Asset(asset_id='DC002', name='Defibrillator Cart #2', category='defibrillator_cart', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(days=1)),
                Asset(asset_id='DC003', name='Defibrillator Cart #3', category='defibrillator_cart', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=2)),
                Asset(asset_id='DC004', name='Defibrillator Cart #4', category='defibrillator_cart', ownership='rental', vendor='EmergencyCare Pro', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=3)),
                
                # Infusion Pump Stands
                Asset(asset_id='IPS001', name='Infusion Pump Stand #1', category='infusion_pump_stand', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=3)),
                Asset(asset_id='IPS002', name='Infusion Pump Stand #2', category='infusion_pump_stand', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(hours=12)),
                Asset(asset_id='IPS003', name='Infusion Pump Stand #3', category='infusion_pump_stand', ownership='rental', vendor='InfusionCare Pro', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=4)),
                Asset(asset_id='IPS004', name='Infusion Pump Stand #4', category='infusion_pump_stand', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=2)),
                Asset(asset_id='IPS005', name='Infusion Pump Stand #5', category='infusion_pump_stand', ownership='hospital', status='available', location='Storage'),
                
                # Crash Carts
                Asset(asset_id='CC001', name='Crash Cart #1', category='crash_cart', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1)),
                Asset(asset_id='CC002', name='Crash Cart #2', category='crash_cart', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(days=1)),
                Asset(asset_id='CC003', name='Crash Cart #3', category='crash_cart', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=2)),
                Asset(asset_id='CC004', name='Crash Cart #4', category='crash_cart', ownership='rental', vendor='EmergencyCare Pro', status='available', location='Storage'),
                
                # Portable Ventilators
                Asset(asset_id='PV001', name='Portable Ventilator Unit A', category='portable_ventilator', ownership='hospital', status='in-use', location='ICU', last_usage=datetime.now() - timedelta(hours=2)),
                Asset(asset_id='PV002', name='Portable Ventilator Unit B', category='portable_ventilator', ownership='rental', vendor='MedEquip Inc', status='available', location='Storage', last_usage=datetime.now() - timedelta(days=1)),
                Asset(asset_id='PV003', name='Portable Ventilator Unit C', category='portable_ventilator', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=3)),
                Asset(asset_id='PV004', name='Portable Ventilator Unit D', category='portable_ventilator', ownership='hospital', status='in-use', location='ER', last_usage=datetime.now() - timedelta(hours=1)),
                
                # Anesthesia Carts
                Asset(asset_id='AC001', name='Anesthesia Cart #1', category='anesthesia_cart', ownership='hospital', status='in-use', location='OR', last_usage=datetime.now() - timedelta(hours=2)),
                Asset(asset_id='AC002', name='Anesthesia Cart #2', category='anesthesia_cart', ownership='hospital', status='available', location='Storage', last_usage=datetime.now() - timedelta(hours=8)),
                Asset(asset_id='AC003', name='Anesthesia Cart #3', category='anesthesia_cart', ownership='rental', vendor='Anesthesia Solutions', status='in-use', location='OR', last_usage=datetime.now() - timedelta(hours=1)),
                Asset(asset_id='AC004', name='Anesthesia Cart #4', category='anesthesia_cart', ownership='hospital', status='maintenance', location='Biomed', last_usage=datetime.now() - timedelta(days=2)),
                Asset(asset_id='AC005', name='Anesthesia Cart #5', category='anesthesia_cart', ownership='hospital', status='available', location='Storage')
            ]
            
            for asset in sample_assets:
                asset.qr_code = generate_qr_code(asset.asset_id)
                db.session.add(asset)
            
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 