import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from ..models import db, Diagnosis, RashAnalysis, AudioAnalysis
from ..utils.helpers import allowed_file
import logging

logger = logging.getLogger(__name__)

class DiagnosisService:
    """Service for handling medical diagnoses."""
    
    @staticmethod
    def process_rash_image(user_id, file, upload_folder):
        """Process rash image upload and analysis."""
        try:
            if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                raise ValueError("Invalid file type")
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create user directory
            user_dir = os.path.join(upload_folder, str(user_id), 'images')
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(user_dir, unique_filename)
            file.save(filepath)
            
            # TODO: Call ML model for analysis
            # For now, return mock analysis
            analysis_result = {
                'condition': 'Possible Dermatitis',
                'confidence': 78.5,
                'severity': 'low',
                'recommendations': [
                    'Apply hydrocortisone cream 2-3 times daily',
                    'Avoid scratching the affected area'
                ]
            }
            
            # Save to database
            rash_analysis = RashAnalysis(
                user_id=user_id,
                image_path=filepath,
                analysis_result=analysis_result,
                confidence_level=analysis_result['confidence']
            )
            
            diagnosis = Diagnosis(
                user_id=user_id,
                diagnosis_type='rash',
                title='Skin Rash Analysis',
                description=analysis_result['condition'],
                severity=analysis_result['severity'],
                confidence_score=analysis_result['confidence'],
                recommendations='\n'.join(analysis_result['recommendations'])
            )
            
            db.session.add(rash_analysis)
            db.session.add(diagnosis)
            db.session.commit()
            
            return {
                'success': True,
                'analysis': analysis_result,
                'diagnosis_id': diagnosis.id,
                'file_url': f'/uploads/{user_id}/images/{unique_filename}'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Rash image processing error: {str(e)}")
            raise
    
    @staticmethod
    def process_audio(user_id, file, upload_folder):
        """Process audio file for cough analysis."""
        try:
            if not allowed_file(file.filename, {'mp3', 'wav', 'm4a'}):
                raise ValueError("Invalid file type")
            
            # Similar implementation for audio...
            # Placeholder for actual implementation
            
            return {'success': True, 'message': 'Audio processed'}
            
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            raise
    
    @staticmethod
    def get_user_diagnoses(user_id, page=1, per_page=10):
        """Get paginated diagnoses for user."""
        try:
            diagnoses = Diagnosis.query.filter_by(user_id=user_id) \
                .order_by(Diagnosis.created_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'diagnoses': [d.to_dict() for d in diagnoses.items],
                'total': diagnoses.total,
                'pages': diagnoses.pages,
                'current_page': page
            }
            
        except Exception as e:
            logger.error(f"Get diagnoses error: {str(e)}")
            raise