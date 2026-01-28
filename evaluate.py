import json

FIELDS = [
    "product_line",
    "origin_port_code",
    "origin_port_name",
    "destination_port_code",
    "destination_port_name",
    "incoterm",
    "cargo_weight_kg",
    "cargo_cbm",
    "is_dangerous",
]

def normalize(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().lower()
    return value

with open("output.json") as f:
    predictions = {e["id"]: e for e in json.load(f)}

with open("ground_truth.json") as f:
    ground_truth = {e["id"]: e for e in json.load(f)}

correct = {field: 0 for field in FIELDS}
total = {field: 0 for field in FIELDS}

for email_id, gt in ground_truth.items():
    pred = predictions[email_id]

    for field in FIELDS:
        total[field] += 1
        if normalize(gt[field]) == normalize(pred[field]):
            correct[field] += 1

print("\nField Accuracy:")
overall_correct = 0
overall_total = 0

for field in FIELDS:
    acc = correct[field] / total[field] * 100
    print(f"{field:25s}: {acc:.2f}%")
    overall_correct += correct[field]
    overall_total += total[field]

print(f"\nOverall Accuracy: {(overall_correct / overall_total) * 100:.2f}%")
