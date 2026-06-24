import pandas as pd
from store.models import Product

df = pd.read_excel("zepto dataset.xlsx")

df["Category"] = df["Category"].astype(str).str.strip()
df["Name"] = df["Name"].astype(str).str.strip()
df["Image"] = df["Image"].astype(str).str.strip()

df = df[
    (df["Category"] != "") &
    (df["Category"] != "nan") &
    (df["Name"] != "") &
    (df["Name"] != "nan")
]

total_needed = 2000
category_count = df["Category"].nunique()
per_category = max(1, total_needed // category_count)

df = df.groupby("Category", group_keys=False).head(per_category)

for _, row in df.iterrows():
    Product.objects.create(
        name=row["Name"],
        price=int(float(row["Price"])),
        image_url=row["Image"],
        category=row["Category"],
        stock=100
    )

print("Imported:", Product.objects.count())