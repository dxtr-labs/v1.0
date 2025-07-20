import json

# Read and analyze the generated prompts
with open('test_prompts.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total prompts generated: {len(lines)}")

# Parse and categorize
categories = {}
prr_prompts = []
complex_prompts = []

for i, line in enumerate(lines):
    try:
        data = json.loads(line.strip())
        category = data.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
        
        if 'prr_travels' in category:
            prr_prompts.append(data)
        elif 'complex' in category:
            complex_prompts.append(data)
    except json.JSONDecodeError as e:
        print(f"Error parsing line {i+1}: {e}")

print("\nCategory breakdown:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

print(f"\nPRR Travels prompts: {len(prr_prompts)}")
if prr_prompts:
    print("Sample PRR prompt:")
    print(f"  {prr_prompts[0]['prompt']}")

print(f"\nComplex workflow prompts: {len(complex_prompts)}")
if complex_prompts:
    print("Sample complex prompt:")
    print(f"  {complex_prompts[0]['prompt']}")

print("\nFirst 3 prompts:")
for i in range(min(3, len(lines))):
    data = json.loads(lines[i].strip())
    print(f"{i+1}. {data['prompt'][:100]}...")
