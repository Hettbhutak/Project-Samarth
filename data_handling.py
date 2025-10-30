import re
import json
from datetime import datetime
import os
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional

# Define data models
class CandidateInfo(BaseModel):
    """Pydantic model for candidate information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    experience: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None
    
    # Validators
    @validator('email')
    def validate_email(cls, v):
        if v:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove non-numeric characters for validation
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

class ConversationRecord(BaseModel):
    """Pydantic model for conversation records."""
    timestamp: str
    candidate_info: CandidateInfo
    conversation: List[str]
    technical_questions: List[str]

def extract_candidate_info(user_input, current_info, current_stage):
    """
    Extract candidate information from user input based on the current conversation stage.
    
    Args:
        user_input (str): The user's input text.
        current_info (dict): Current candidate information.
        current_stage (str): The current conversation stage.
        
    Returns:
        dict: Updated candidate information.
    """
    # Create a copy of the current info to avoid modifying the original
    info = current_info.copy()
    
    # Extract information based on the current stage
    if current_stage == "greeting" and not info["name"]:
        # Extract name from greeting
        info["name"] = extract_name(user_input)
    
    elif current_stage == "collecting_email" and not info["email"]:
        # Extract email
        info["email"] = extract_email(user_input)
    
    elif current_stage == "collecting_tech_stack" and not info["tech_stack"]:
        # Extract tech stack
        info["tech_stack"] = user_input.strip()
    
    elif current_stage == "collecting_position" and not info["position"]:
        # Extract position
        info["position"] = user_input.strip()
    
    elif current_stage == "collecting_rating":
        # Extract self-rating (1-10)
        rating = extract_rating(user_input)
        if rating:
            info["rating"] = rating
    
    elif current_stage == "collecting_phone" and not info["phone"]:
        # Extract phone number
        info["phone"] = extract_phone(user_input)
    
    elif current_stage == "collecting_experience" and not info["experience"]:
        # Extract years of experience
        info["experience"] = extract_experience(user_input)
    
    elif current_stage == "collecting_location" and not info["location"]:
        # Extract location
        info["location"] = user_input.strip()
    
    return info

def extract_rating(text):
    """
    Extract a numerical rating from text.
    
    Args:
        text (str): The text to extract rating from.
        
    Returns:
        str: Extracted rating or None if not found.
    """
    # Simple extraction of numbers from 1-10
    text = text.lower()
    
    # Check for numeric rating
    import re
    numeric_match = re.search(r'(\d+)(/10)?', text)
    if numeric_match:
        rating = int(numeric_match.group(1))
        if 1 <= rating <= 10:
            return str(rating)
    
    # Check for textual ratings
    if "one" in text or "1" in text:
        return "1"
    elif "two" in text or "2" in text:
        return "2"
    elif "three" in text or "3" in text:
        return "3"
    elif "four" in text or "4" in text:
        return "4"
    elif "five" in text or "5" in text:
        return "5"
    elif "six" in text or "6" in text:
        return "6"
    elif "seven" in text or "7" in text:
        return "7"
    elif "eight" in text or "8" in text:
        return "8"
    elif "nine" in text or "9" in text:
        return "9"
    elif "ten" in text or "10" in text:
        return "10"
    
    return None

def save_conversation(candidate_info, messages, technical_questions):
    """
    Save the conversation for review.
    
    Args:
        candidate_info (dict): Candidate information.
        messages (list): List of conversation messages.
        technical_questions (list): List of technical questions asked.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create a record of the conversation
        conversation_record = ConversationRecord(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            candidate_info=candidate_info,
            conversation=messages,
            technical_questions=technical_questions
        )
        
        # Generate a filename based on the candidate's name and timestamp
        name_part = candidate_info.get("name", "unknown").lower().replace(" ", "_")
        timestamp_part = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/conversation_{name_part}_{timestamp_part}.json"
        
        # Save to file
        with open(filename, "w") as f:
            f.write(conversation_record.json(indent=2))
        
        return True
        
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")
        return False

def extract_name(text):
    """
    Extract a person's name from the given text.
    
    Args:
        text (str): The text to extract the name from.
        
    Returns:
        str: The extracted name or None if not found.
    """
    # Simple name extraction - take the whole input if it's short and looks like a name
    text = text.strip()
    
    # If it's a short input (likely just a name)
    if len(text.split()) <= 3 and len(text) < 40:
        # Check if it doesn't contain common non-name phrases
        non_name_phrases = ["hello", "hi", "hey", "my name is", "i am", "i'm", "this is"]
        if not any(phrase in text.lower() for phrase in non_name_phrases):
            return text
    
    # Look for patterns like "my name is John" or "I am John"
    import re
    name_patterns = [
        r"(?:my name is|i am|i'm|this is) ([A-Za-z\s]+)",
        r"(?:call me|i'm called|name's) ([A-Za-z\s]+)",
        r"([A-ZaZ\s]+) (?:here|speaking|is my name)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).strip().title()
    
    # If we can't find a pattern, just return the first few words
    # (assuming people often start with their name)
    words = text.split()
    if words:
        # Take up to 3 words, if they're capitalized (likely a name)
        potential_name = " ".join(word for word in words[:3] 
                                if word[0].isupper() or word.lower() in ["van", "de", "la", "von"])
        if potential_name:
            return potential_name
    
    # If nothing worked, just return the first word (better than nothing)
    return words[0] if words else text

def extract_email(text):
    """
    Extract an email address from the given text.
    
    Args:
        text (str): The text to extract the email from.
        
    Returns:
        str: The extracted email or None if not found.
    """
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    """
    Extract a phone number from the given text.
    
    Args:
        text (str): The text to extract the phone number from.
        
    Returns:
        str: The extracted phone number or None if not found.
    """
    import re
    # Remove non-numeric characters for easier matching
    text_digits = re.sub(r'[^0-9]', '', text)
    
    # If we have a 10-digit number, it's likely a phone number
    if len(text_digits) == 10:
        return text_digits
    
    # Look for patterns like (123) 456-7890 or 123-456-7890
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
        r'\d{3}[-.\s]?\d{4}',  # 123-4567
        r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1 123-456-7890
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    # If nothing worked but we have digits, return them
    if text_digits:
        return text_digits
    
    return None

def extract_experience(text):
    """
    Extract years of experience from the given text.
    
    Args:
        text (str): The text to extract the experience from.
        
    Returns:
        str: The extracted experience or None if not found.
    """
    import re
    
    # Look for patterns like "5 years" or "5+ years"
    exp_patterns = [
        r'(\d+\.?\d*)(?:\+)?\s*(?:years?|yrs?)',  # 5 years, 5+ years, 5 yrs
        r'(\d+\.?\d*)(?:\+)?'  # just a number (fallback)
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text.lower())
        if match:
            years = match.group(1)
            # Add context to make it clear
            if "+" in text:
                return f"{years}+ years"
            else:
                return f"{years} years"
    
    # Check for textual years
    text_lower = text.lower()
    if "one year" in text_lower or "a year" in text_lower:
        return "1 year"
    elif "two years" in text_lower:
        return "2 years"
    # Add more textual matches as needed
    
    # If nothing worked, just return the input as is
    return text
