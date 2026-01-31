from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'nurse' or 'doctor'

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'role': self.role}


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class PatientVital(db.Model):
    """PatientVitals: stores heart rate, temperature, spo2 and timestamp"""
    __tablename__ = 'patient_vitals'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    heart_rate = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    spo2 = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    patient = db.relationship('Patient', backref=db.backref('vitals', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            'temperature': self.temperature,
            'spo2': self.spo2,
            'timestamp': self.timestamp.isoformat()
        }


class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    severity = db.Column(db.String(20))  # 'normal', 'warning', 'critical'
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    escalated = db.Column(db.Boolean, default=False)
    escalated_at = db.Column(db.DateTime(timezone=True))
    escalated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    patient = db.relationship('Patient', backref=db.backref('alerts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'severity': self.severity,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'escalated': self.escalated,
            'escalated_at': self.escalated_at.isoformat() if self.escalated_at else None,
            'escalated_by': self.escalated_by
        }
