from db.database import get_engine
from db.models import Base

def main():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created.")

if __name__ == "__main__":
    main()