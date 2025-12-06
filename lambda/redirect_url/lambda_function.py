import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'urls'))


def lambda_handler(event, context):
    """
    Lambda para obtener URL original y redirigir
    Espera: GET /{shortCode}
    Retorna: { "originalUrl": "https://example.com/...", "shortCode": "abc123" }
    """

    # Habilitamos CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
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
        # Obtenemos el shortCode de los path parameters
        print(f"Event: {event}")

        # El shortCode puede venir en pathParameters o en el path directamente
        short_code = None
        if event.get('pathParameters'):
            short_code = event['pathParameters'].get('shortCode')

        # Si no viene en pathParameters, intentamos extraerlo del path
        if not short_code and event.get('path'):
            path = event['path'].strip('/')
            print(f"Path: {path}")
            if path:
                short_code = path

        print(f"ShortCode extraído: {short_code}")

        if not short_code:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Código corto no proporcionado'})
            }

        # Buscamos en DynamoDB
        response = table.get_item(Key={'shortCode': short_code})
        print(f"Response: {response}")
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'URL no encontrada'})
            }

        item = response['Item']
        original_url = item['originalUrl']

        # Actualizamos el contador de clicks y última vez accedido
        timestamp = datetime.utcnow().isoformat()
        table.update_item(
            Key={'shortCode': short_code},
            UpdateExpression='SET clicks = clicks + :inc, lastAccessed = :timestamp',
            ExpressionAttributeValues={
                ':inc': 1,
                ':timestamp': timestamp
            }
        )

        # Retornamos la URL original
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'originalUrl': original_url,
                'shortCode': short_code,
                'clicks': int(item.get('clicks', 0)) + 1
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Error del servidor'})
        }