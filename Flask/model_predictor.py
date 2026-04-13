import tensorflow as tf
import numpy as np
from PIL import Image
import os
from io import BytesIO

# Model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'Models')

MODEL_PATHS = {
    'detection': os.path.join(MODELS_DIR, 'Detection_liver_model.h5'),
    'stage': os.path.join(MODELS_DIR, 'SizeStage_cancer_model.h5'),
    'location': os.path.join(MODELS_DIR, 'TumorLoc_unet_model.h5')
}

# Load models
models = {}

DETECTION_THRESHOLD = 0.2   # Confidence threshold for liver detection (0-1)
TUMOR_THRESHOLD = 0.001     # Confidence threshold for tumor detection (0-1)

def load_models():
    global models
    for model_name, model_path in MODEL_PATHS.items():
        try:
            if os.path.exists(model_path):
                try:
                    models[model_name] = tf.keras.models.load_model(model_path)
                    print(f"[OK] Loaded {model_name} model")
                except Exception as first_error:
                    print(f"[WARN] Standard load failed for {model_name}: {str(first_error)[:100]}")
                    print(f"[WARN] Trying with compile=False")
                    models[model_name] = tf.keras.models.load_model(model_path, compile=False)
                    print(f"[OK] Loaded {model_name} model (with compile=False)")
            else:
                print(f"[ERROR] Model not found: {model_path}")
        except Exception as e:
            error_msg = str(e)[:150]
            print(f"[ERROR] {model_name}: {error_msg}")

def prepare_image(image_input, target_size=(224, 224), grayscale=False):
    try:
        if isinstance(image_input, bytes):
            img = Image.open(BytesIO(image_input))
        elif isinstance(image_input, BytesIO):
            img = Image.open(image_input)
        else:
            img = Image.open(image_input)

        if grayscale:
            if img.mode != 'L':
                img = img.convert('L')
        else:
            if img.mode != 'RGB':
                img = img.convert('RGB')

        img = img.resize(target_size)

        img_array = np.array(img) / 255.0

        if grayscale and len(img_array.shape) == 2:
            img_array = np.expand_dims(img_array, axis=-1)

        img_array = np.expand_dims(img_array, axis=0)

        return img_array
    except Exception as e:
        raise ValueError(f"Error preparing image: {e}")

def predict_liver_detection(image_input):
    if 'detection' not in models:
        return {'is_liver': False, 'confidence': 0.0, 'error': 'Model not loaded'}

    try:
        img_array = prepare_image(image_input)
        prediction = models['detection'].predict(img_array, verbose=0)

        confidence = float(prediction[0][0])
        is_liver = bool(confidence > DETECTION_THRESHOLD)

        print(f"Liver detection: confidence={confidence:.4f}, threshold={DETECTION_THRESHOLD}, detected={is_liver}")

        return {
            'is_liver': is_liver,
            'confidence': round(confidence, 4)
        }
    except Exception as e:
        print(f"Liver detection error: {e}")
        return {'is_liver': False, 'confidence': 0.0, 'error': str(e)}

def predict_cancer_stage(image_input):
    if 'stage' not in models:
        return {'stage': 'Benign', 'stage_num': 0, 'score': 0.0, 'risk_level': 'No Risk', 'classification': 'Benign', 'tumor_count': 0.0, 'tumor_size': 0.0, 'error': 'Model not loaded'}

    try:
        img_array = prepare_image(image_input)
        predictions = models['stage'].predict(img_array, verbose=0)

        if isinstance(predictions, (list, tuple)):
            stage_logits = predictions[0][0] 
            tumor_count = float(predictions[1][0][0]) if len(predictions) > 1 else 0.0
            tumor_size = float(predictions[2][0][0]) if len(predictions) > 2 else 0.0
        else:
            stage_logits = predictions[0]
            tumor_count = 0.0
            tumor_size = 0.0

        stage_idx = int(np.argmax(stage_logits))
        stage_score = float(np.max(stage_logits))

        stages = ['Benign', 'Stage I', 'Stage II', 'Stage III', 'Stage IV']

        if stage_idx < len(stages):
            stage = stages[stage_idx]
        else:
            stage = 'Unknown'

        classification = 'Benign' if stage_idx == 0 else 'Malignant'

        risk_levels = ['No Risk', 'Low', 'Medium', 'High', 'Very High']
        risk_level = risk_levels[min(stage_idx, len(risk_levels)-1)]

        print(f"Cancer stage: class={stage_idx}, score={stage_score:.4f}, stage={stage}, classification={classification}, tumor_count={tumor_count:.2f}, tumor_size={tumor_size:.2f}")

        return {
            'stage': stage,
            'stage_num': int(stage_idx),
            'score': round(stage_score, 4),
            'risk_level': risk_level,
            'classification': classification,
            'tumor_count': round(tumor_count, 4),
            'tumor_size': round(tumor_size, 4)
        }
    except Exception as e:
        print(f"Cancer stage error: {e}")
        import traceback
        traceback.print_exc()
        return {'stage': 'Benign', 'stage_num': 0, 'score': 0.0, 'risk_level': 'No Risk', 'classification': 'Benign', 'tumor_count': 0.0, 'tumor_size': 0.0, 'error': str(e)}

def predict_tumor_location(image_input):
    if 'location' not in models:
        return {'has_tumor': False, 'location': 'Unknown', 'confidence': 0.0, 'error': 'Model not loaded'}

    try:

        img_array = prepare_image(image_input, target_size=(128, 128), grayscale=True)
        prediction = models['location'].predict(img_array, verbose=0)


        tumor_confidence = float(np.max(prediction))
        has_tumor = bool(tumor_confidence > TUMOR_THRESHOLD)

        print(f"Tumor location: confidence={tumor_confidence:.4f}, threshold={TUMOR_THRESHOLD}, detected={has_tumor}")

        locations = ['Right Lobe', 'Left Lobe', 'Central', 'Multiple']
        location_idx = int(np.argmax(np.mean(prediction, axis=(1, 2, 3)))) % len(locations)

        return {
            'has_tumor': has_tumor,
            'location': locations[location_idx],
            'confidence': round(tumor_confidence, 4),
            'location_map': 'generated'
        }
    except Exception as e:
        print(f"Tumor location error: {e}")
        return {'has_tumor': False, 'location': 'Unknown', 'confidence': 0.0, 'error': str(e)}

def get_full_prediction(image_input):
    try:
        results = {
            'liver_detection': predict_liver_detection(image_input),
            'cancer_stage': predict_cancer_stage(image_input),
            'tumor_location': predict_tumor_location(image_input)
        }

        detection = results.get('liver_detection') or {}
        stage = results.get('cancer_stage') or {}
        location = results.get('tumor_location') or {}

        is_liver = detection.get('is_liver', False)
        has_tumor = location.get('has_tumor', False)

        if not is_liver:
            overall_status = 'NO_LIVER'
            overall_message = 'No liver detected in the image'
        elif not has_tumor:
            overall_status = 'NORMAL'
            overall_message = 'No abnormalities detected'
        else:
            overall_status = 'ABNORMAL'


            if has_tumor and stage.get('stage') == 'Benign':
                print(f"[OVERRIDE] Tumor detected but stage=Benign, overriding to Stage I")
                stage['stage'] = 'Stage I'
                stage['stage_num'] = 1
                stage['classification'] = 'Malignant'
                stage['risk_level'] = 'Low'

            risk_level = stage.get('risk_level', 'Unknown')
            overall_message = f'Abnormality detected - {risk_level} risk'

        results['overall_status'] = overall_status
        results['overall_message'] = overall_message

        results = convert_to_json_serializable(results)

        return results
    except Exception as e:
        print(f"Full prediction error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'liver_detection': {'is_liver': False, 'confidence': 0.0},
            'cancer_stage': {'stage': 'Unknown', 'risk_level': 'Unknown', 'score': 0.0},
            'tumor_location': {'has_tumor': False, 'location': 'Unknown', 'confidence': 0.0},
            'overall_status': 'ERROR',
            'overall_message': 'Error processing image: ' + str(e),
            'error': str(e)
        }

def convert_to_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj
