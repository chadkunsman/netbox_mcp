# NetBox Devices API Documentation

This document provides a reference for the NetBox API endpoints related to devices that will be used by the NetBox MCP Server.

## NetBox Instance Specifics

From our exploration, we've learned that this specific NetBox instance has the following characteristics:

### Sites
Common sites in this NetBox instance include:
- SF1
- NYC1
- DEN1
- DEN2
- SYM1
- USCOL3
- SJC1.DC

### Device Roles
Common device roles in this NetBox instance include:
- `office_access_switch` (not simply "switch")
- `net-wireless-accesspoint`
- `net-firewall`
- `router`
- `net-structured-cabling`
- `net-facilities-pdu`
- `net-monitoring`
- `office_sensor_temp`
- `NID`
- `Systems`

### Device Models
Common device models include:
- `C9300-48P` - Cisco 9300 series switches
- `EX4400-48MP` - Juniper switches
- `EX4300-48MP` - Juniper switches
- `Catalyst 9410R` - Cisco Catalyst switches
- `AP43` - Wireless access points

## Device Endpoints

### List Devices

```
GET /api/dcim/devices/
```

Retrieves a list of devices. Can be filtered by various parameters.

#### Filter Parameters:

- **name**: Device name (supports regex)
- **site**: Site name or ID
- **rack**: Rack name or ID
- **role**: Device role name or ID
- **manufacturer**: Manufacturer name or ID
- **device_type**: Device type name or ID
- **status**: Device status (active, planned, etc.)
- **tag**: Tag name
- **limit**: Maximum number of results (default: 50)

#### Example Request:

```bash
curl -X GET \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; indent=4" \
  http://netbox/api/dcim/devices/?site=sf1&status=active
```

#### Example Response:

```json
{
  "count": 42,
  "next": "http://netbox/api/dcim/devices/?limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": 123,
      "name": "sf1-switch01",
      "device_type": {
        "id": 24,
        "model": "Catalyst 3850-48P"
      },
      "device_role": {
        "id": 17,
        "name": "Access Switch"
      },
      "site": {
        "id": 6,
        "name": "SF1"
      },
      "status": {
        "value": "active",
        "label": "Active"
      },
      "serial": "FDO12345XYZ",
      "tags": [
        "monitored",
        "production"
      ]
    }
  ]
}
```

### Get Specific Device

```
GET /api/dcim/devices/{id}/
```

Retrieves a specific device by ID.

#### Example Request:

```bash
curl -X GET \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; indent=4" \
  http://netbox/api/dcim/devices/123/
```

### Filter Devices by Name

```
GET /api/dcim/devices/?name__ic=switch
```

Returns all devices with 'switch' in their name, using a case-insensitive contains filter.

### Filter Devices by Site

```
GET /api/dcim/devices/?site=sf1
```

Returns all devices at the site with name 'sf1'.

### Filter Devices by Role

```
GET /api/dcim/devices/?role=firewall
```

Returns all devices with the role 'firewall'.

### Filter Devices by Regex

```
GET /api/dcim/devices/?name__ic=^sf1.*
```

Returns all devices with names beginning with 'sf1', case-insensitive.

## Common Fields in Device Objects

- **id**: Unique identifier for the device
- **name**: Device name
- **device_type**: Reference to the device type object
- **device_role**: Reference to the device role object
- **site**: Reference to the site object
- **rack**: Reference to the rack object (if assigned)
- **position**: Position in rack (if racked)
- **face**: Rack face (front/rear)
- **status**: Device status object
- **primary_ip4**: Primary IPv4 address
- **primary_ip6**: Primary IPv6 address
- **serial**: Serial number
- **asset_tag**: Asset tag
- **tags**: List of tags

## Sample API Response (Python)

Using pynetbox, you can access the device data as follows:

```python
import pynetbox

nb = pynetbox.api(
    'http://netbox.example.com',
    token='abcdef123456'
)

# Get all devices
devices = nb.dcim.devices.all()

# Filter devices by site
site_devices = nb.dcim.devices.filter(site='sf1')

# Get a specific device by name
device = nb.dcim.devices.get(name='sf1.as1')

# Print device information
print(f"Device: {device.name}")
print(f"Model: {device.device_type.model}")
print(f"Role: {device.device_role.name}")
print(f"Site: {device.site.name}")
print(f"Status: {device.status}")
```

## Useful Query Parameters

- **?limit=value**: Number of objects to return (default: 50)
- **?offset=value**: The initial index from which to return the results
- **?name=value**: Exact match by name
- **?name__ic=value**: Case-insensitive partial match on name
- **?id=value**: Match by ID
- **?id__in=1,2,3**: Match by multiple IDs
- **?site=value**: Filter by site name
- **?site_id=value**: Filter by site ID
- **?role=value**: Filter by device role name
- **?status=value**: Filter by status (e.g., 'active', 'planned')