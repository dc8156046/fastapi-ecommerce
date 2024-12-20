from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import Country, State


def populate_initial_data(db: Session):

    # Function to check if a country exists
    def get_or_create_country(name: str, code: str, is_active: bool):
        existing_country = db.query(Country).filter_by(name=name).first()
        if existing_country is None:
            new_country = Country(name=name, code=code, is_active=is_active)
            db.add(new_country)
            return new_country
        return existing_country

    # Create countries
    usa = get_or_create_country(name="United States", code="USA", is_active=True)

    canada = get_or_create_country(name="Canada", code="CAN", is_active=True)

    db.flush()  # Flush to get IDs

    # US States
    us_states = [
        State(name="Alabama", code="AL", country_id=usa.id),
        State(name="Alaska", code="AK", country_id=usa.id),
        State(name="Arizona", code="AZ", country_id=usa.id),
        State(name="Arkansas", code="AR", country_id=usa.id),
        State(name="California", code="CA", country_id=usa.id),
        State(name="Colorado", code="CO", country_id=usa.id),
        State(name="Connecticut", code="CT", country_id=usa.id),
        State(name="Delaware", code="DE", country_id=usa.id),
        State(name="Florida", code="FL", country_id=usa.id),
        State(name="Georgia", code="GA", country_id=usa.id),
        State(name="Hawaii", code="HI", country_id=usa.id),
        State(name="Idaho", code="ID", country_id=usa.id),
        State(name="Illinois", code="IL", country_id=usa.id),
        State(name="Indiana", code="IN", country_id=usa.id),
        State(name="Iowa", code="IA", country_id=usa.id),
        State(name="Kansas", code="KS", country_id=usa.id),
        State(name="Kentucky", code="KY", country_id=usa.id),
        State(name="Louisiana", code="LA", country_id=usa.id),
        State(name="Maine", code="ME", country_id=usa.id),
        State(name="Maryland", code="MD", country_id=usa.id),
        State(name="Massachusetts", code="MA", country_id=usa.id),
        State(name="Michigan", code="MI", country_id=usa.id),
        State(name="Minnesota", code="MN", country_id=usa.id),
        State(name="Mississippi", code="MS", country_id=usa.id),
        State(name="Missouri", code="MO", country_id=usa.id),
        State(name="Montana", code="MT", country_id=usa.id),
        State(name="Nebraska", code="NE", country_id=usa.id),
        State(name="Nevada", code="NV", country_id=usa.id),
        State(name="New Hampshire", code="NH", country_id=usa.id),
        State(name="New Jersey", code="NJ", country_id=usa.id),
        State(name="New Mexico", code="NM", country_id=usa.id),
        State(name="New York", code="NY", country_id=usa.id),
        State(name="North Carolina", code="NC", country_id=usa.id),
        State(name="North Dakota", code="ND", country_id=usa.id),
        State(name="Ohio", code="OH", country_id=usa.id),
        State(name="Oklahoma", code="OK", country_id=usa.id),
        State(name="Oregon", code="OR", country_id=usa.id),
        State(name="Pennsylvania", code="PA", country_id=usa.id),
        State(name="Rhode Island", code="RI", country_id=usa.id),
        State(name="South Carolina", code="SC", country_id=usa.id),
        State(name="South Dakota", code="SD", country_id=usa.id),
        State(name="Tennessee", code="TN", country_id=usa.id),
        State(name="Texas", code="TX", country_id=usa.id),
        State(name="Utah", code="UT", country_id=usa.id),
        State(name="Vermont", code="VT", country_id=usa.id),
        State(name="Virginia", code="VA", country_id=usa.id),
        State(name="Washington", code="WA", country_id=usa.id),
        State(name="West Virginia", code="WV", country_id=usa.id),
        State(name="Wisconsin", code="WI", country_id=usa.id),
        State(name="Wyoming", code="WY", country_id=usa.id),
        # Add US territories if needed
        State(name="District of Columbia", code="DC", country_id=usa.id),
        State(name="Puerto Rico", code="PR", country_id=usa.id),
    ]

    # Canadian Provinces and Territories
    canadian_provinces = [
        State(name="Alberta", code="AB", country_id=canada.id),
        State(name="British Columbia", code="BC", country_id=canada.id),
        State(name="Manitoba", code="MB", country_id=canada.id),
        State(name="New Brunswick", code="NB", country_id=canada.id),
        State(name="Newfoundland and Labrador", code="NL", country_id=canada.id),
        State(name="Nova Scotia", code="NS", country_id=canada.id),
        State(name="Ontario", code="ON", country_id=canada.id),
        State(name="Prince Edward Island", code="PE", country_id=canada.id),
        State(name="Quebec", code="QC", country_id=canada.id),
        State(name="Saskatchewan", code="SK", country_id=canada.id),
        # Territories
        State(name="Northwest Territories", code="NT", country_id=canada.id),
        State(name="Nunavut", code="NU", country_id=canada.id),
        State(name="Yukon", code="YT", country_id=canada.id),
    ]

    # Add all states/provinces
    db.add_all(us_states + canadian_provinces)
    db.commit()


# Usage example
# with SessionLocal() as db:
#     populate_initial_data(db)
