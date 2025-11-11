"""
Seed database with scraped parts data
"""

import json
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from database.models import init_db, SessionLocal, Part, Model, Base, engine


def seed_database():
    print("=" * 80)
    print("Starting database seeding...")
    print("=" * 80 + "\n")

    # First, initialize database (create tables)
    print("Step 1: Creating database tables...")
    init_db()
    print()

    # Load parts data
    parts_file = os.path.join(parent_dir, "parts_data.json")

    if not os.path.exists(parts_file):
        print(f"✗ Error: {parts_file} not found!")
        print(f"  Current directory: {os.getcwd()}")
        print("  Please run the scraper first: python scripts/scrape_partselect.py")
        return

    with open(parts_file, "r") as f:
        parts_data = json.load(f)

    print(f"Step 2: Loaded {len(parts_data)} parts from {parts_file}\n")

    db = SessionLocal()

    try:
        # Check if tables exist and have data
        print("Step 3: Clearing existing data...")
        try:
            part_count = db.query(Part).count()
            model_count = db.query(Model).count()
            print(f"  Found {part_count} existing parts")
            print(f"  Found {model_count} existing models")

            if part_count > 0 or model_count > 0:
                db.query(Part).delete()
                db.query(Model).delete()
                db.commit()
                print("  ✓ Existing data cleared")
        except Exception as e:
            print(f"  No existing data to clear (this is fine for first run)")
            db.rollback()

        print()

        # Track unique models
        models_dict = {}

        print("Step 4: Adding parts and models to database...")

        # Add parts and models
        for idx, part_data in enumerate(parts_data):
            # Create Part
            part = Part(
                part_number=part_data["part_number"],
                name=part_data["name"],
                category=part_data["category"],
                subcategory=part_data.get("subcategory"),
                price=part_data["price"],
                description=part_data["description"],
                brand=part_data["brand"],
                image_url=part_data.get("image_url"),
                installation_difficulty=part_data.get("installation_difficulty"),
                installation_steps=part_data.get("installation_steps", []),
                common_symptoms=part_data.get("common_symptoms", []),
            )

            # Add compatible models
            for model_number in part_data.get("compatible_models", []):
                if model_number not in models_dict:
                    model = Model(
                        model_number=model_number,
                        brand=part_data["brand"],
                        appliance_type=part_data["category"],
                    )
                    models_dict[model_number] = model
                    db.add(model)

                part.compatible_models.append(models_dict[model_number])

            db.add(part)

            if (idx + 1) % 2 == 0 or (idx + 1) == len(parts_data):
                print(f"  Processed {idx + 1}/{len(parts_data)} parts...")

        db.commit()

        print("\n" + "=" * 80)
        print(f"✓ SUCCESS! Database seeded with {len(parts_data)} parts!")
        print(f"✓ Added {len(models_dict)} unique models!")
        print("=" * 80 + "\n")

        # Verify data
        print("Step 5: Verifying database...")
        part_count = db.query(Part).count()
        model_count = db.query(Model).count()
        print(f"  ✓ Parts in database: {part_count}")
        print(f"  ✓ Models in database: {model_count}\n")

        # Show sample parts
        print("Sample parts:")
        sample_parts = db.query(Part).limit(3).all()
        for part in sample_parts:
            print(f"  - {part.name} ({part.part_number}) - ${part.price}")

        print("\n" + "=" * 80)
        print("✓ Database is ready to use!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
