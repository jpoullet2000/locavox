from fastapi import APIRouter, HTTPException, Depends, status
import uuid
from datetime import datetime
from typing import List, Optional

from ..models.schemas.message import Message, MessageCreate, MessageResponse
from ..models.schemas.user_address import Coordinates
from ..dependencies import get_db  # Updated import from dependencies module

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageCreate, db=Depends(get_db)):
    """Create a new message with optional geographic information"""
    message_dict = message.dict()

    # If addressId is provided, get coordinates from the address
    if message.addressId and not message.coordinates:
        user_address = await db.user_addresses.find_one(
            {"id": message.addressId, "userId": message.userId}
        )
        if not user_address:
            raise HTTPException(status_code=404, detail="Address not found")

        message_dict["coordinates"] = user_address["coordinates"]

    new_message = {"id": str(uuid.uuid4()), "timestamp": datetime.now(), **message_dict}

    await db.messages.insert_one(new_message)
    return new_message


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    user_id: Optional[str] = None,
    near_lat: Optional[float] = None,
    near_lng: Optional[float] = None,
    radius: Optional[float] = None,
    db=Depends(get_db),
):
    """Get messages with optional filtering by user or geographic location"""
    query = {}

    # Filter by user if specified
    if user_id:
        query["userId"] = user_id

    # Add geospatial query if coordinates and radius are provided
    if near_lat is not None and near_lng is not None and radius is not None:
        # This assumes you've set up a geospatial index on the coordinates field
        query["coordinates"] = {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [near_lng, near_lat]},
                "$maxDistance": radius,  # distance in meters
            }
        }

    messages = await db.messages.find(query).to_list(length=100)
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str, db=Depends(get_db)):
    """Get a specific message by ID"""
    message = await db.messages.find_one({"id": message_id})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
