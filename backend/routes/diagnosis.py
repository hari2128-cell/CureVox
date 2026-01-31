from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from ..models import db, User, Diagnosis, RashAnalysis, AudioAnalysis
from ..utils.decorators import jwt_required, validate_content_type
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('diagnosis', __name__, url_prefix='/api/diagnosis')

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@bp.route('/rash/upload', methods=['POST'])
@jwt_required
@validate_content_type('multipart/form-data')
def upload_rash_image():
    """Upload rash/skin image for analysis."""
    try:
        current_user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided',
                'error': 'NO_FILE'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No selected file',
                'error': 'NO_FILE'
            }), 400
        
        if not allowed_file(file.filename, {'png', 'jpg', 'jpeg'}):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed: PNG, JPG, JPEG',
                'error': 'INVALID_FILE_TYPE'
            }), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create user-specific directory
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, unique_filename)
        file.save(filepath)
        
        # TODO: Implement actual ML analysis here
        # For now, return mock analysis
        analysis_result = {
            'condition': 'Possible Dermatitis',
            'confidence': 78.5,
            'description': 'The image shows signs of mild dermatitis with redness and slight swelling.',
            'recommendations': [
                'Apply hydrocortisone cream 2-3 times daily',
                'Avoid scratching the affected area',
                'Keep the area clean and dry',
                'Schedule follow-up in 3 days if no improvement'
            ],
            'severity': 'low'
        }
        
        # Save analysis to database
        rash_analysis = RashAnalysis(
            user_id=current_user_id,
            image_path=filepath,
            analysis_result=analysis_result,
            possible_conditions=[{'name': 'Contact Dermatitis', 'probability': 0.65}],
            confidence_level=analysis_result['confidence'],
            suggested_treatment='\n'.join(analysis_result['recommendations']),
            follow_up_required=True,
            follow_up_date=datetime.utcnow().date()
        )
        
        db.session.add(rash_analysis)
        
        # Also create a diagnosis record
        diagnosis = Diagnosis(
            user_id=current_user_id,
            diagnosis_type='rash',
            title='Skin Rash Analysis',
            description=analysis_result['description'],
            symptoms='Redness, swelling, irritation',
            severity=analysis_result['severity'],
            confidence_score=analysis_result['confidence'],
            recommendations='\n'.join(analysis_result['recommendations'])
        )
        
        db.session.add(diagnosis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded and analyzed successfully',
            'analysis': analysis_result,
            'file_path': filepath,
            'analysis_id': rash_analysis.id,
            'diagnosis_id': diagnosis.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Rash upload error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process image',
            'error': 'PROCESSING_ERROR'
        }), 500


@bp.route('/audio/upload', methods=['POST'])
@jwt_required
@validate_content_type('multipart/form-data')
def upload_audio():
    """Upload audio for cough/respiratory analysis."""
    try:
        current_user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No audio file provided',
                'error': 'NO_FILE'
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No selected file',
                'error': 'NO_FILE'
            }), 400
        
        if not allowed_file(file.filename, {'mp3', 'wav', 'm4a'}):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed: MP3, WAV, M4A',
                'error': 'INVALID_FILE_TYPE'
            }), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create user-specific directory
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, unique_filename)
        file.save(filepath)
        
        # TODO: Implement actual audio analysis here
        # For now, return mock analysis
        analysis_result = {
            'condition': 'Bronchitis',
            'confidence': 82.3,
            'description': 'The audio analysis indicates persistent cough with wheezing sounds.',
            'severity_score': 65,
            'recommendations': [
                'Drink plenty of fluids',
                'Use cough suppressants as needed',
                'Get adequate rest',
                'Consult a doctor if fever develops