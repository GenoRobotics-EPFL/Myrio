import requests

def download_bold_marker(taxon="Viridiplantae", marker="matK", output_file=None):
    if output_file is None:
        output_file = f"{marker}_{taxon.replace(' ', '_')}.fasta"

    url = f"https://www.boldsystems.org/index.php/API_Public/sequence?taxon={taxon}&marker={marker}&format=fasta"
    response = requests.get(url)

    if response.status_code == 200 and response.text.strip():
        with open(output_file, "w") as f:
            f.write(response.text)
        print(f"✅ Saved {marker} sequences for {taxon} to {output_file}")
    else:
        print(f"⚠️ No data returned or request failed for {marker} ({response.status_code})")

# List of barcode genes to download
markers = ["matK", "rbcL", "ITS", "psbA-trnH"]  # BOLD uses 'psbA-trnH' as marker name

for marker in markers:
    download_bold_marker(taxon="Viridiplantae", marker=marker)
