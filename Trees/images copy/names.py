import os

# Pääkansio
base_dir = "/Users/iirokaki/artificial_int_2025/projekti/Untitled/Trees/images"

# Käydään läpi kaikki alakansiot
for root, dirs, files in os.walk(base_dir):
    # Hyppää pääkansion yli (vain alakansiot käsittelyyn)
    if root == base_dir:
        continue

    folder_name = os.path.basename(root)  # esim. "koivu"
    counter = 1

    for filename in files:
        old_path = os.path.join(root, filename)
        # Otetaan tiedoston loppuliite (esim. .jpg, .png)
        ext = os.path.splitext(filename)[1].lower()
        
        # Muodostetaan uusi tiedostonimi
        new_filename = f"{folder_name}{counter}{ext}"
        new_path = os.path.join(root, new_filename)

        # Jos tiedostonimi on jo olemassa, kasvatetaan counteria kunnes vapaa nimi löytyy
        while os.path.exists(new_path):
            counter += 1
            new_filename = f"{folder_name}{counter}{ext}"
            new_path = os.path.join(root, new_filename)

        # Uudelleennimeäminen
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")

        counter += 1