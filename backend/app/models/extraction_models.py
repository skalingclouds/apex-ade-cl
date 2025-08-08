"""
Pydantic models for structured data extraction using Landing.AI
"""
from typing import Optional
from pydantic import BaseModel, Field


class OptInFormExtraction(BaseModel):
    """Schema for extracting opt-in form data from each page"""
    # Page identifier
    page_number: Optional[int] = Field(description="Page number in the document")
    
    # Claimant information
    claimant_name: Optional[str] = Field(description="Full name of the person opting in")
    claimant_address: Optional[str] = Field(description="Street address")
    claimant_city: Optional[str] = Field(description="City")
    claimant_state: Optional[str] = Field(description="State")
    claimant_zip: Optional[str] = Field(description="ZIP code")
    claimant_phone: Optional[str] = Field(description="Phone number")
    claimant_email: Optional[str] = Field(description="Email address")
    
    # Claim information
    claim_number: Optional[str] = Field(description="Unique claim or case number")
    case_name: Optional[str] = Field(description="Name of the class action case")
    
    # Signature and date
    signature_present: Optional[bool] = Field(description="Whether a signature is present")
    date_signed: Optional[str] = Field(description="Date the form was signed")
    
    # SSN (if present)
    ssn_last4: Optional[str] = Field(description="Last 4 digits of SSN if visible")
    
    # Additional fields that might be present
    employer_name: Optional[str] = Field(description="Employer name if applicable")
    employment_dates: Optional[str] = Field(description="Dates of employment if applicable")
    settlement_amount: Optional[float] = Field(description="Settlement amount if specified")