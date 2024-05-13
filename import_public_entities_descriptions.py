import csv
from budgetportal.models.government import PublicEntity

# Open the CSV file
with open("public_entities_descriptions.csv", newline="") as csvfile:
    # Create a DictReader object with named columns
    csvreader = csv.DictReader(csvfile)

    updated = []
    not_found = []
    for row in csvreader:
        public_entities = PublicEntity.objects.filter(name=row['Entity Name'])
        if public_entities:
            for entity in public_entities:
                entity.description = row['Description']
                entity.save()
            print(f"Updated description for {entity.name}")
            updated.append(entity.name)
        else:
            print(f"Could not find public entity {row['Entity Name']}")
            not_found.append(row['Entity Name'])

print(f"Updated {len(updated)} public entities")
print(f"Could not find {len(not_found)} public entities")
print("Not found:")
print(not_found)
