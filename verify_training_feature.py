import os
import sys

# Add root to path
sys.path.append(os.getcwd())

try:
    from logic.training_registry import TRAINING_REGISTRY
except ImportError:
    print("❌ Critical: Could not import TRAINING_REGISTRY.")
    sys.exit(1)

VIDEO_DIR = "training_videos"

def verify_module():
    print("🔬 Verifying Training Module Integrity...")

    # 1. Check Registry
    roles = list(TRAINING_REGISTRY.keys())
    print(f"✅ Registry loaded. Roles found: {roles}")

    # 2. Check Videos
    if not os.path.exists(VIDEO_DIR):
        print("❌ Video Directory missing!")
    else:
        print(f"✅ Video Directory present: {VIDEO_DIR}")
        
    missing_files = []
    total_files = 0
    for role, videos in TRAINING_REGISTRY.items():
        for vid in videos:
            fpath = os.path.join(VIDEO_DIR, vid['filename'])
            if not os.path.exists(fpath):
                missing_files.append(vid['filename'])
            total_files += 1
            
    if missing_files:
        print(f"⚠️ Missing {len(missing_files)} video files: {missing_files}")
    else:
        print(f"✅ All {total_files} video files accounted for.")

    # 3. Check App UI
    try:
        with open("app_ui.py", "r", encoding="utf-8") as f:
            ui_code = f.read()
            
        if "render_training_section" in ui_code:
            print("✅ Helper function 'render_training_section' detected in app_ui.py")
        else:
            print("❌ Helper function NOT found in app_ui.py")
            
        # Count integrations
        integrations = ui_code.count('render_training_section("')
        print(f"✅ 'render_training_section' called {integrations} times across roles.")
        
    except Exception as e:
        print(f"❌ Error reading app_ui.py: {e}")

    print("\n🏁 Verification Complete.")

if __name__ == "__main__":
    verify_module()
