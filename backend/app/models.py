from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'nurse' or 'doctor'
    api_token = db.Column(db.String(128), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'api_token': self.api_token,
            'email': self.email,
        }

    # Password helpers (for JWT/email+password auth)
    def set_password(self, password: str):
        """
        Set the password hash for this user.

        Uses bcrypt for secure hashing. Call this before committing the user.
        """
        if password is None:
            self.password_hash = None
            return
        import bcrypt

        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password, salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the stored bcrypt hash.
        """
        import bcrypt

        if not self.password_hash:
            return False
        if isinstance(password, str):
            password = password.encode('utf-8')
        stored = self.password_hash.encode('utf-8')
        try:
            return bcrypt.checkpw(password, stored)
        except ValueError:
            # corrupted hash
            return False


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(10), nullable=True)
    room = db.Column(db.String(20), nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'sex': self.sex,
            'room': self.room,
            'weight_kg': self.weight_kg,
            'notes': self.notes
        }


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
    # New fields for alert review lifecycle
    reviewed = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime(timezone=True))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    closed = db.Column(db.Boolean, default=False)
    closed_at = db.Column(db.DateTime(timezone=True))
    closed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    patient = db.relationship('Patient', backref=db.backref('alerts', lazy=True))
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    closer = db.relationship('User', foreign_keys=[closed_by])

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'severity': self.severity,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'escalated': self.escalated,
            'escalated_at': self.escalated_at.isoformat() if self.escalated_at else None,
            'escalated_by': self.escalated_by,
            'reviewed': self.reviewed,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'closed': self.closed,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'closed_by': self.closed_by,
        }

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('patient_notes', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('notes', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'content': self.content,
            'user_name': self.user.name # Include user name for display
        }
