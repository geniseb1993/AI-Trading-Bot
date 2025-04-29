from app import app

print("\n=== REGISTERED ROUTES ===")
for rule in app.url_map.iter_rules():
    print(f"Route: {rule.endpoint} -> {rule.rule}")
print("=========================\n") 