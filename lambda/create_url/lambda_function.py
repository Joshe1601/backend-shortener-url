import json
import boto3
import os
import string
import random
from datetime import datetime
from urllib.parse import urlparse

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'urls'))


def generate_short_code(length=6):
    """Genera un código aleatorio único"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def is_valid_url(url):
    """Valida formato de URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def lambda_handler(event, context):
    """
    Lambda para crear URLs cortas
    Espera: { "url": "https://example.com/url-muy-larga" }
    Retorna: { "shortCode": "abc123", "shortUrl": "https://tu-dominio.com/abc123" }
    """

    # Habilitamos CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }

    # Configuramos preflight OPTIONS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        print("Event:", event)

        # Obtenemos la URL
        original_url = event.get('url').strip()
        custom_code = event.get('customCode', '').strip()  # Solo si queremos un código personalizado

        # Validaciones
        if not original_url:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'La URL es requerida'})
            }

        if not is_valid_url(original_url):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'La URL inválida'})
            }

        # Generamos nuestro código personalizado
        if custom_code:
            # Validamos que no exista en DynamoDB
            response = table.get_item(Key={'shortCode': custom_code})
            if 'Item' in response:
                return {
                    'statusCode': 409,
                    'headers': headers,
                    'body': json.dumps({'error': 'El código ya existe'})
                }
            short_code = custom_code
        else:
            # Generamos un código único
            max_attempts = 5
            for _ in range(max_attempts):
                short_code = generate_short_code()
                response = table.get_item(Key={'shortCode': short_code})
                if 'Item' not in response:
                    break
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': 'No se pudo generar el código único'})
                }

        # Guardamos en DynamoDB el código generado
        timestamp = datetime.utcnow().isoformat()
        item = {
            'shortCode': short_code,
            'originalUrl': original_url,
            'createdAt': timestamp,
            'clicks': 0,
            'lastAccessed': None
        }

        table.put_item(Item=item)

        # Generamos la URL corta
        base_url = os.environ.get('BASE_URL', 'https://shorter.morillospinedo.com')
        short_url = f"{base_url}/{short_code}"

        return {
            'statusCode': 201,
            'headers': headers,
            'data': json.dumps({
                'shortCode': short_code,
                'shortUrl': short_url,
                'originalUrl': original_url,
                'createdAt': timestamp
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'data': json.dumps({'error': 'Error del servidor'})
        }