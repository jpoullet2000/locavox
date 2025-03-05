import logging
import httpx
from typing import Optional, Tuple, Dict
from pydantic import BaseModel

from ..config import GEOCODING_API_KEY, GEOCODING_PROVIDER

logger = logging.getLogger(__name__)


class GeocodingResult(BaseModel):
    latitude: float
    longitude: float
    success: bool
    message: Optional[str] = None


async def geocode_address(address_components: Dict[str, str]) -> GeocodingResult:
    """
    Convert address components into latitude and longitude using a geocoding service.

    Args:
        address_components: Dictionary with keys like street, house_number, city, postcode, country

    Returns:
        GeocodingResult with latitude, longitude and status information
    """
    # Format address from components
    formatted_address = f"{address_components.get('house_number', '')} {address_components.get('street', '')}, "
    formatted_address += f"{address_components.get('city', '')}, {address_components.get('postcode', '')}, "
    formatted_address += address_components.get("country", "")

    try:
        if GEOCODING_PROVIDER == "nominatim":
            return await _geocode_with_nominatim(formatted_address)
        elif GEOCODING_PROVIDER == "google":
            return await _geocode_with_google(formatted_address)
        else:
            return GeocodingResult(
                latitude=0.0,
                longitude=0.0,
                success=False,
                message=f"Unsupported geocoding provider: {GEOCODING_PROVIDER}",
            )
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return GeocodingResult(
            latitude=0.0,
            longitude=0.0,
            success=False,
            message=f"Geocoding error: {str(e)}",
        )


async def _geocode_with_nominatim(address: str) -> GeocodingResult:
    """
    Geocode an address using Nominatim (OpenStreetMap)
    Note: Please respect Nominatim's usage policy - https://operations.osmfoundation.org/policies/nominatim/
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": "Locavox Application"  # Required by Nominatim ToS
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data:
                return GeocodingResult(
                    latitude=0.0,
                    longitude=0.0,
                    success=False,
                    message="Address not found",
                )

            return GeocodingResult(
                latitude=float(data[0]["lat"]),
                longitude=float(data[0]["lon"]),
                success=True,
            )
    except Exception as e:
        logger.error(f"Nominatim geocoding error: {str(e)}")
        raise


async def _geocode_with_google(address: str) -> GeocodingResult:
    """
    Geocode an address using Google Maps API
    Note: Requires a valid API key
    """
    if not GEOCODING_API_KEY:
        return GeocodingResult(
            latitude=0.0,
            longitude=0.0,
            success=False,
            message="Google Maps API key not configured",
        )

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GEOCODING_API_KEY}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] != "OK":
                return GeocodingResult(
                    latitude=0.0,
                    longitude=0.0,
                    success=False,
                    message=f"Geocoding failed: {data.get('status')}",
                )

            location = data["results"][0]["geometry"]["location"]
            return GeocodingResult(
                latitude=location["lat"], longitude=location["lng"], success=True
            )
    except Exception as e:
        logger.error(f"Google geocoding error: {str(e)}")
        raise
