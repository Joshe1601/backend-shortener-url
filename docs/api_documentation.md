# API Documentation - URL Shortener

## Base URL
```
https://your-api-gateway.execute-api.region.amazonaws.com/prod
```

---

## Endpoints

### 1. Crear URL Corta

Genera una versión acortada de una URL larga.

**Endpoint:** `POST /create`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://ejemplo.com/pagina-muy-larga",
  "customCode": "mi-codigo-personalizado"
}
```

**Response Success (201):**
```json
{
  "shortCode": "14FeKu",
  "shortUrl": "https://shorter.tu-dominio.com/14FeKu",
  "originalUrl": "https://ejemplo.com/pagina-muy-larga",
  "createdAt": "2024-12-06T10:30:00.000Z"
}
```

**Response Errors:**

- **400 Bad Request** - URL inválida o faltante
```json
{
  "error": "La URL es requerida"
}
```

- **409 Conflict** - Código personalizado ya existe
```json
{
  "error": "El código ya existe"
}
```

- **500 Internal Server Error** - Error del servidor
```json
{
  "error": "Error del servidor"
}
```

**Ejemplo cURL:**
```bash
curl -X POST https://your-api-gateway.com/prod/create \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.ejemplo.com/pagina-muy-larga"
  }'
```

---

### 2. Obtener URL Original

Obtiene la URL original a partir del código corto.

**Endpoint:** `GET /redirect/{shortCode}`

**Path Parameters:**
- `shortCode` (string, required): Código único de 6 caracteres

**Response Success (200):**
```json
{
  "originalUrl": "https://ejemplo.com/pagina-muy-larga",
  "shortCode": "14FeKu",
  "clicks": 5
}
```

**Response Errors:**

- **400 Bad Request** - Código no proporcionado
```json
{
  "error": "Código corto no proporcionado"
}
```

- **404 Not Found** - URL no existe
```json
{
  "error": "URL no encontrada"
}
```

- **500 Internal Server Error** - Error del servidor
```json
{
  "error": "Error del servidor"
}
```

**Ejemplo cURL:**
```bash
curl https://your-api-gateway.com/prod/redirect/14FeKu
```

---

## Notas Adicionales

### CORS
Ambos endpoints tienen CORS habilitado con:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`


### Validaciones
- La URL debe tener un esquema válido (`http://` o `https://`)
- El código personalizado debe ser único
- Los códigos generados automáticamente tienen 6 caracteres alfanuméricos

### Tracking
Cada vez que se accede a una URL mediante `/redirect/{shortCode}`, se incrementa el contador de `clicks` y se actualiza `lastAccessed`.