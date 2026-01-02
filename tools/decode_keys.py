import base64

def decode_key(encoded_str):
    try:
        # Remove AKLT prefix if present for decoding
        prefix = ""
        to_decode = encoded_str
        if encoded_str.startswith("AKLT"):
            prefix = "AKLT"
            to_decode = encoded_str[4:]
        
        decoded = base64.b64decode(to_decode).decode('utf-8')
        return decoded
    except Exception as e:
        return f"Error: {str(e)}"

ak_encoded = "AKLTMDg2ODY4MjUwY2QyNDJiYmFmNWYyYjEwMTJmMWY5NzE"
sk_encoded = "T0RObFpqVTVOamN6T0RCa05HWTNZVGhqWmpObU16aGtPRE0xWXpSbFpXSQ=="

print(f"Encoded AK: {ak_encoded}")
print(f"Decoded AK: {decode_key(ak_encoded)}")
print(f"Encoded SK: {sk_encoded}")
print(f"Decoded SK: {decode_key(sk_encoded)}")
