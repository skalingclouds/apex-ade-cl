# %%
import os
import json
from pathlib import Path
from PIL import Image as PILImage
from agentic_doc.parse import parse
from agentic_doc.utils import viz_parsed_document

# %%
base_dir = Path(os.getcwd())
input_folder = base_dir / "input_folder_webinar"
results_folder = base_dir / "results_folder_webinar"
groundings_folder = base_dir / "groundings_folder_webinar"
visualizations_folder = base_dir / "visualizations_folder_webinar"
input_folder.mkdir(parents=True, exist_ok=True)
results_folder.mkdir(parents=True, exist_ok=True)
groundings_folder.mkdir(parents=True, exist_ok=True)
visualizations_folder.mkdir(parents=True, exist_ok=True)

# %%
file_paths = [
    str(p)
    for p in input_folder.iterdir()
    if p.suffix.lower() in [".pdf", ".png", ".jpg", ".jpeg"]
]

# %%
file_paths

# %%
result = parse(
    documents=file_paths,
    result_save_dir=str(results_folder),
    grounding_save_dir=str(groundings_folder),
    include_marginalia=True,
    include_metadata_in_markdown=True,      
    )

# %%
result

# %%
parsed_doc = result[2]
parsed_doc

# %%
from IPython.display import Markdown
Markdown(parsed_doc.markdown)

# %%

print("Doc type:", parsed_doc.doc_type)
print("Pages:", parsed_doc.start_page_idx, "to", parsed_doc.end_page_idx)

# Chunks
chunks = parsed_doc.chunks
print("\nNumber of chunks:", len(chunks))

# Markdown summary
print("\nMarkdown summary:")
print(parsed_doc.markdown[:500])  # just the first 500 characters


# %%
import pandas as pd

chunk_rows = []

for chunk in chunks:
    chunk_id = getattr(chunk, "chunk_id", None)
    chunk_type = chunk.chunk_type.value if chunk.chunk_type else None
    text = getattr(chunk, "text", "")
    grounding = getattr(chunk, "grounding", [])

    if grounding:
        for g in grounding:
            row = {
                "page": g.page if hasattr(g, "page") else None,
                "chunk_id": chunk_id,
                "chunk_type": chunk_type,
                "text": text.strip().replace("\n", " "),
                "image_path": str(g.image_path) if g.image_path else None,
                "box_l": g.box.l if g.box else None,
                "box_t": g.box.t if g.box else None,
                "box_r": g.box.r if g.box else None,
                "box_b": g.box.b if g.box else None,
            }
            chunk_rows.append(row)
    else:
        chunk_rows.append({
            "page": None,
            "chunk_id": chunk_id,
            "chunk_type": chunk_type,
            "text": text.strip().replace("\n", " "),
            "image_path": None,
            "box_l": None,
            "box_t": None,
            "box_r": None,
            "box_b": None,
        })

# Create DataFrame
df_chunks = pd.DataFrame(chunk_rows)
df_chunks

# %%
# Access the markdown content
markdown_text = parsed_doc.markdown

# Choose a filename to save
output_path = results_folder / "goji.md"

# Write to file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown_text)

# %%
import json
from pathlib import Path

# Convert chunks to serializable format using model_dump()
chunk_dicts = [chunk.model_dump() for chunk in parsed_doc.chunks]

# Recursively convert PosixPath objects to strings
def stringify_paths(obj):
    if isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: stringify_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [stringify_paths(v) for v in obj]
    else:
        return obj

chunk_dicts_serializable = stringify_paths(chunk_dicts)

# Define output path
output_path = results_folder / "goji.json"

# Write to JSON file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunk_dicts_serializable, f, indent=2)

# %%
output_dir = "./visualizations"

# %%
images = viz_parsed_document(
    file_paths[0],
    parsed_doc,
    output_dir=visualizations_folder
)

# %%
from IPython.display import Image, display

display(Image(filename='./visualizations/chomps_viz_page_0.png'))

# %%
# Field Extraction 
from pydantic import BaseModel, Field

# Main product schema
class Product(BaseModel):
    product_name: str = Field(description="The full name of the product excluding the brand name as it appears on the packaging.")
    brand: str = Field(description="The brand or company name.")
    net_weight_oz: float = Field(description="The net weight of the product in ounces, as labeled (e.g., 'NET WT 8 OZ'). Return empty field if not found.")
    net_weight_g: float = Field(description="The net weight of the product in grams, often shown in parentheses next to ounces (e.g., '330 g'). Return empty field if not found.")
    servings_per_container: int = Field(description="The total number of servings per container, usually listed in the Nutrition Facts panel. Return empty field if not found.")
    serving_size: str = Field(description="The serving size as printed on the package, such as '1 stick (45g)' or '1 scoop (10g)'. Return empty field if not found.")
    product_type: str = Field(description="General category of the product (e.g., 'yogurt', 'hot dogs', 'supplement').")
    flavor: str = Field(description="The flavor of the product if applicable, such as 'creamy vanilla'. Return empty field if not found or not applicable.")
    is_grass_fed: bool = Field(description="True if the label mentions 'Grass-Fed'.")
    is_organic: bool = Field(description="True if the label mentions 'Organic' or includes the 'USDA Organic' seal.")
    is_keto_friendly: bool = Field(description="True if the label mentions 'Keto' or 'Ketogenic' diets or similar.")
    is_paleo_friendly: bool = Field(description="True if the label mentions 'Paleo' or 'Paleolithic' diets or similar.")
    is_kosher: bool = Field(description="True if the label mentions 'Kosher'.")
    is_regenerative: bool = Field(description="True if the label includes terms like 'Regeneratively Sourced' or 'Certified Regenerative'.")
    is_certified_humane: bool = Field(description="True if the label features the 'Certified Humane' logo or wording.")
    is_animal_welfare_certified: bool = Field(description="True if the product is 'Animal Welfare Certified' or meets GAP (Global Animal Partnership) standards.")
    is_pasture_raised: bool = Field(description="True if the label claims the animals were 'Pasture Raised'.")
    is_non_gmo: bool = Field(description="True if the product is labeled 'Non-GMO' or has the 'Non-GMO Project Verified' seal.")
    is_gluten_free: bool = Field(description="True if the product is labeled 'Gluten-Free' or certified gluten-free.")
    is_dairy_free: bool = Field(description="True if the product states 'Dairy-Free' or No Dairy.")
    is_lactose_free: bool = Field(description="True if the product explicitly states 'Lactose-Free' or no lactose.")
    is_whole30_approved: bool = Field(description="True if the product is labeled as 'Whole30 Approved'.")
    has_no_added_sugar: bool = Field(description="True if the packaging says 'No Added Sugar' or 'Zero Sugar' or similar.")
    no_antibiotics: bool = Field(description="True if the label claims 'No Antibiotics' or similar language.")
    no_hormones: bool = Field(description="True if the product claims 'No Hormones' or or 'Not treated with rBST' or similar language.")
    no_animal_byproducts: bool = Field(description="True if it states animals were not fed animal by-products.")
    usda_inspected: bool = Field(description="True if the USDA inspection seal is present on the packaging.")


# %%
# DO NOT RUN
result = parse(
    documents=file_paths,
    result_save_dir=str(results_folder),
    grounding_save_dir=str(groundings_folder),
    include_marginalia=True,
    include_metadata_in_markdown=True,      
    )

# %%
result_fe = parse(
    documents=file_paths, 
    extraction_model=Product)

# %%
result_fe

# %%
result_fe[2].extraction_metadata

# %%
import pandas as pd

# Assume parsed_docs is your list of ParsedDocument objects
# Example: parsed_docs = [ParsedDocument(...), ParsedDocument(...), ...]

# Extract the product data
records = []
for doc in result_fe:
    product = doc.extraction
    meta=doc.extraction_metadata
    product_dict = {
        "product_name": product.product_name,
        "product_name_ref":meta.product_name,
        "brand": product.brand,
        "net_weight_oz": product.net_weight_oz,
        "net_weight_oz_ref":meta.net_weight_oz,
        "net_weight_g": product.net_weight_g,
        "servings_per_container": product.servings_per_container,
        "serving_size": product.serving_size,
        "product_type": product.product_type,
        "flavor": product.flavor,
        "is_grass_fed": product.is_grass_fed,
        "is_organic": product.is_organic,
        "is_keto_friendly": product.is_keto_friendly,
        "is_paleo_friendly": product.is_paleo_friendly,
        "is_kosher": product.is_kosher,
        "is_regenerative": product.is_regenerative,
        "is_certified_humane": product.is_certified_humane,
        "is_animal_welfare_certified": product.is_animal_welfare_certified,
        "is_pasture_raised": product.is_pasture_raised,
        "is_non_gmo": product.is_non_gmo,
        "is_gluten_free": product.is_gluten_free,
        "is_dairy_free": product.is_dairy_free,
        "is_lactose_free": product.is_lactose_free,
        "is_whole30_approved": product.is_whole30_approved,
        "has_no_added_sugar": product.has_no_added_sugar,
        "no_antibiotics": product.no_antibiotics,
        "no_hormones": product.no_hormones,
        "no_animal_byproducts": product.no_animal_byproducts,
        "usda_inspected": product.usda_inspected,
        "usda_inspected_ref": meta.usda_inspected,
    }
    records.append(product_dict)

# Create DataFrame
df = pd.DataFrame(records)
df


# %% [markdown]
# 

# %% [markdown]
# 

# %%



