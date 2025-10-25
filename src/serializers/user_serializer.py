from typing import List, Dict, Any
from bson import ObjectId

def serialize_users(users: List) -> List[Dict[str, Any]]:
    return [serialize_single_user(user) for user in users]

def serialize_single_user(user: Dict[str, Any]) -> Dict[str, Any]:
    # Extrair dados de localização se existirem
    location_data = None
    if user.get('location'):
        location_data = {
            "latitude": user['location'].get('latitude'),
            "longitude": user['location'].get('longitude'),
            "accuracy": user['location'].get('accuracy')
        }
    
    # Formatar data de check-in se existir
    checkin_time = None
    if user.get('checkin_time'):
        if isinstance(user['checkin_time'], str):
            checkin_time = user['checkin_time']
        else:
            # Se for um objeto datetime, converter para string
            checkin_time = user['checkin_time'].isoformat() if hasattr(user['checkin_time'], 'isoformat') else str(user['checkin_time'])
    
    return {
        "id": str(user.get("_id", "")),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "email": user.get("email", ""),
        "location": location_data,
        "checkin_time": checkin_time
    }