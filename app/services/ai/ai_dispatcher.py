from app.schemas.chat import ChatResponse


def handle_customer_message(message: str) -> ChatResponse:
    text = message.lower()

    if "tow" in text or "towing" in text:
        return ChatResponse(
            reply="I can help with that. Please share your vehicle location, vehicle type, and the issue you're having.",
            intent="tow_request",
        )

    if "flat tire" in text or "flat tyre" in text:
        return ChatResponse(
            reply="It sounds like you need roadside assistance for a flat tire. Please send your location and vehicle details.",
            intent="roadside_flat_tire",
        )

    if "jump" in text or "battery" in text or "won't start" in text or "wont start" in text:
        return ChatResponse(
            reply="It sounds like you may need a jump start. Please send your location, vehicle type, and whether the battery is completely dead.",
            intent="roadside_jumpstart",
        )

    if "locked out" in text or "lockout" in text or "keys in car" in text:
        return ChatResponse(
            reply="I can help with a lockout request. Please send your location, vehicle make/model, and whether the keys are inside the vehicle.",
            intent="roadside_lockout",
        )

    return ChatResponse(
        reply="I can help with towing, jump starts, lockouts, flat tires, and roadside assistance. Please tell me what happened.",
        intent="general_inquiry",
    )