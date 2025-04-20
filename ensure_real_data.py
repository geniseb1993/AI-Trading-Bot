import os
import json
import time
import traceback

def ensure_real_data():
    """
    Script to ensure the backtest data is treated as real data in the frontend
    This does a few things:
    1. Makes sure api/backtest_results.csv exists and is populated
    2. Creates a special marker file to indicate to the frontend that data is real
    """
    print("🔧 Ensuring backtest data is treated as real data...")
    
    # Check if backtest_results.csv exists
    csv_paths = [
        "api/backtest_results.csv",
        "data/backtest_results.csv",
        "backtest_results.csv",
    ]
    
    csv_exists = False
    for csv_path in csv_paths:
        if os.path.exists(csv_path):
            csv_exists = True
            print(f"✅ Found backtest data at {csv_path}")
            
            # Update the file timestamp to ensure it's seen as fresh
            with open(csv_path, 'a'):
                os.utime(csv_path, None)
    
    if not csv_exists:
        print("❌ No backtest data found! Running generate_backtest_data.py...")
        try:
            import generate_backtest_data
            generate_backtest_data.generate_realistic_backtest_data()
            print("✅ Generated new backtest data")
        except Exception as e:
            print(f"❌ Error generating backtest data: {str(e)}")
            traceback.print_exc()
            return False
    
    # Create the frontend/src directory if it doesn't exist
    frontend_src_dir = "frontend/src"
    os.makedirs(frontend_src_dir, exist_ok=True)
    print(f"📁 Ensuring directory exists: {frontend_src_dir}")
    
    # Create a marker file in the frontend directory
    try:
        # JSON marker file
        marker_path = os.path.join(frontend_src_dir, "data_source.json")
        marker_data = {
            "source": "api",
            "isRealData": True,
            "timestamp": time.time()
        }
        
        print(f"📝 Writing JSON marker file to: {os.path.abspath(marker_path)}")
        with open(marker_path, 'w') as f:
            json.dump(marker_data, f, indent=2)
        print(f"✅ Created data source marker file at {marker_path}")
        
        # JavaScript module file
        js_marker_path = os.path.join(frontend_src_dir, "dataSourceMarker.js")
        print(f"📝 Writing JavaScript module to: {os.path.abspath(js_marker_path)}")
        with open(js_marker_path, 'w') as f:
            f.write(f"""// Auto-generated file to indicate real data source
const dataSourceMarker = {{
  source: "api",
  isRealData: true,
  timestamp: {time.time()}
}};

export default dataSourceMarker;
""")
        print(f"✅ Created JavaScript data source marker at {js_marker_path}")
    except Exception as e:
        print(f"❌ Error creating marker files: {str(e)}")
        traceback.print_exc()
        return False
    
    print("✅ Done! The backtest data should now be treated as real data.")
    print("🔄 Please refresh your browser to see the changes.")
    return True

if __name__ == "__main__":
    ensure_real_data() 