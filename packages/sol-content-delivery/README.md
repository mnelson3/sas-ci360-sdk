# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Content Delivery Module

> **Status: canonical.** This is the actively maintained client for the Digital Assets API.

This repository provides Python interfaces for SAS Customer Intelligence 360 Digital Assets and Content Delivery APIs.

### Overview

The Content Delivery module enables programmatic management of digital assets, content creation, and delivery operations within CI360.

### Features

- Digital asset management
- Content creation and publishing
- Asset delivery and distribution
- Content personalization
- Asset performance tracking

### Prerequisites

- Python 3.8+
- Access to SAS Customer Intelligence 360 environment
- Required dependencies (see requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mnelson3/sas-ci360-sol-content-delivery.git
   cd sas-ci360-sol-content-delivery
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Getting Started

```python
from sasci360solcontentdelivery.base import Base

# Initialize content delivery client
content_client = Base(
    algorithm="HS256",
    api="digital-assets",
    encoding="utf-8",
    host="your-ci360-host",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id"
)

# Manage digital assets and content
```

### Solutions Code

The content delivery module provides:

1. **Asset Management**: Upload, organize, and manage digital assets
2. **Content Operations**: Create and publish marketing content
3. **Delivery Control**: Manage content distribution channels
4. **Personalization**: Dynamic content adaptation

### Troubleshooting

- Verify asset formats and sizes
- Check content publishing permissions
- Review delivery channel configurations
- Monitor asset performance metrics

## 🛠️ Developer/Implementation Guide

This section provides comprehensive guidance for developers implementing content delivery solutions with SAS CI360.

### Architecture Overview

The SAS CI360 Content Delivery module follows a modular architecture designed for scalable digital asset management:

```
┌─────────────────────────────────────────────────────────────┐
│                Content Delivery Module                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Asset       │ │ Content     │ │ Delivery    │           │
│  │ Management  │ │ Operations  │ │ Control     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ REST API    │ │ JWT Auth    │ │ Async I/O   │           │
│  │ Client      │ │ & Security  │ │ Operations  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

#### Core Components

1. **Asset Management Layer**
   - `CI360ContentDeliveryBase`: Core client class for asset operations
   - Asset CRUD operations (Create, Read, Update, Delete)
   - File upload and metadata management
   - Asset versioning and lifecycle management

2. **Content Operations Layer**
   - Content publishing and distribution
   - Personalization engine integration
   - Content performance analytics
   - Multi-channel content delivery

3. **Delivery Control Layer**
   - Delivery channel configuration
   - Content targeting and segmentation
   - Delivery scheduling and automation
   - Performance monitoring and reporting

### Configuration Management

#### Environment Variables
```bash
export SAS_CI360_SECRET_KEY="your-secret-key"
export SAS_CI360_TENANT_ID="your-tenant-id"
```

#### Configuration Class
```python
from sasci360solcontentdelivery.base import CI360ContentDeliveryConfig

config = CI360ContentDeliveryConfig(
    algorithm="HS256",
    api="digital-assets",
    encoding="utf-8",
    host="your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id"
)
```

### API Integration Patterns

#### Synchronous Operations
```python
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase

# Initialize client
client = CI360ContentDeliveryBase()

# Get all assets
assets = client.get_assets()
print(f"Found {len(assets)} assets")

# Upload new asset
with open('marketing-banner.png', 'rb') as f:
    asset_data = {
        'name': 'Marketing Banner',
        'description': 'Q4 Marketing Campaign Banner',
        'type': 'image'
    }
    result = client.upload_asset(asset_data, f.read(), 'marketing-banner.png')
    print(f"Uploaded asset: {result['id']}")
```

#### Asynchronous Operations
```python
import asyncio
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase

async def manage_assets():
    client = CI360ContentDeliveryBase()

    # Get assets asynchronously
    assets = await client.get_assets_async()
    print(f"Found {len(assets)} assets")

    # Upload asset asynchronously
    with open('newsletter-template.html', 'rb') as f:
        asset_data = {
            'name': 'Newsletter Template',
            'type': 'html',
            'category': 'templates'
        }
        result = await client.upload_asset_async(
            asset_data, f.read(), 'newsletter-template.html'
        )
        print(f"Uploaded asset: {result['id']}")

# Run async operations
asyncio.run(manage_assets())
```

#### Content Delivery
```python
# Deliver content to specific audience
delivery_config = {
    'channel': 'email',
    'audience_segment': 'newsletter_subscribers',
    'schedule': '2024-01-15T10:00:00Z',
    'personalization_rules': {
        'dynamic_content': True,
        'location_based': True
    }
}

result = client.deliver_content(asset_id, delivery_config)
print(f"Content delivery scheduled: {result['delivery_id']}")
```

### Error Handling

#### Exception Types
```python
from sasci360solcontentdelivery.base import (
    CI360ContentDeliveryBase,
    CI360ContentDeliveryError,
    CI360ContentDeliveryAuthError,
    CI360ContentDeliveryValidationError
)

try:
    client = CI360ContentDeliveryBase()
    assets = client.get_assets()
except CI360ContentDeliveryAuthError as e:
    print(f"Authentication failed: {e}")
    # Handle auth issues (token refresh, credentials)
except CI360ContentDeliveryValidationError as e:
    print(f"Validation error: {e}")
    # Handle input validation issues
except CI360ContentDeliveryError as e:
    print(f"API error: {e}")
    # Handle general API errors
```

#### Retry Logic
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def upload_with_retry(client, asset_data, file_content, filename):
    return client.upload_asset(asset_data, file_content, filename)

# Usage
try:
    result = upload_with_retry(client, asset_data, file_content, filename)
except Exception as e:
    print(f"Upload failed after retries: {e}")
```

### Testing Approaches

#### Unit Testing
```python
import unittest
from unittest.mock import Mock, patch
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase

class TestContentDelivery(unittest.TestCase):
    def setUp(self):
        self.client = CI360ContentDeliveryBase()
        self.mock_response = Mock()
        self.mock_response.json.return_value = {'status': 'success'}

    @patch('requests.Session.request')
    def test_get_assets(self, mock_request):
        mock_request.return_value = self.mock_response

        result = self.client.get_assets()
        self.assertEqual(result['status'], 'success')
        mock_request.assert_called_once()

    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._generate_token')
    def test_token_generation(self, mock_generate):
        mock_generate.return_value = 'mock-jwt-token'

        headers = self.client.get_auth_headers()
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer mock-jwt-token')
```

#### Integration Testing
```python
import pytest
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase

@pytest.fixture
def content_client():
    return CI360ContentDeliveryBase()

@pytest.mark.integration
def test_asset_lifecycle(content_client):
    # Test complete asset lifecycle
    asset_data = {
        'name': 'Test Asset',
        'type': 'document',
        'description': 'Integration test asset'
    }

    # Create
    with open('test-file.txt', 'rb') as f:
        created = content_client.upload_asset(asset_data, f.read(), 'test-file.txt')
    asset_id = created['id']

    # Read
    retrieved = content_client.get_asset(asset_id)
    assert retrieved['name'] == 'Test Asset'

    # Update
    updated_data = asset_data.copy()
    updated_data['description'] = 'Updated description'
    updated = content_client.update_asset(asset_id, updated_data)
    assert updated['description'] == 'Updated description'

    # Delete
    deleted = content_client.delete_asset(asset_id)
    assert deleted is True
```

### Performance Considerations

#### Connection Pooling
```python
# Configure session for optimal performance
client._session.mount('https://', requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3,
    pool_block=False
))
```

#### Batch Operations
```python
# Process assets in batches for better performance
def process_assets_batch(client, asset_ids, batch_size=50):
    for i in range(0, len(asset_ids), batch_size):
        batch = asset_ids[i:i + batch_size]
        # Process batch concurrently
        tasks = [client.get_asset_async(asset_id) for asset_id in batch]
        results = asyncio.run(asyncio.gather(*tasks))
        yield results
```

#### Caching Strategies
```python
from cachetools import TTLCache
import hashlib

class CachedContentDeliveryClient(CI360ContentDeliveryBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL

    def _get_cache_key(self, method, *args, **kwargs):
        key_data = f"{method}:{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_asset(self, asset_id: str):
        cache_key = self._get_cache_key('get_asset', asset_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = super().get_asset(asset_id)
        self._cache[cache_key] = result
        return result
```

### Security Best Practices

1. **Token Management**: Rotate JWT tokens regularly
2. **Input Validation**: Validate all asset data and file uploads
3. **Access Control**: Implement proper authorization checks
4. **Audit Logging**: Log all asset operations for compliance
5. **Encryption**: Use HTTPS for all API communications

### Contributing

We welcome your contributions! Please read [CONTRIBUTING](CONTRIBUTING.md) for details on how to submit contributions to this project.

### License

This project is licensed under the [Nelson Grey LLC Community License 1.0](LICENSE).

- **Free for individuals, education, and research**: use, modify, and distribute this software for non-commercial purposes
- **Commercial evaluation**: evaluate the software for a possible commercial use, free of charge
- **Commercial production use**: requires a commercial license from Nelson Grey LLC
- **Automatic conversion**: on December 13, 2029, this automatically converts to the Apache License 2.0

For commercial licensing inquiries, contact support@nelsongrey.com.

### Additional Resources

For more information, see [Digital Assets API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-digital-assets.htm).
