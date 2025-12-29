import os
import sys

# Add root to path to import logic
sys.path.append(os.getcwd())

from logic.training_registry import TRAINING_REGISTRY

VIDEO_DIR = "training_videos"

def create_dummy_videos():
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
        print(f"📁 Created directory: {VIDEO_DIR}")

    total_videos = 0
    
    for role, videos in TRAINING_REGISTRY.items():
        print(f"🔹 Processing Role: {role}")
        for vid in videos:
            filename = vid['filename']
            filepath = os.path.join(VIDEO_DIR, filename)
            
            # Create a dummy file (text file renamed as mp4)
            if not os.path.exists(filepath):
                with open(filepath, "w") as f:
                    f.write(f"DUMMY VIDEO CONTENT FOR: {vid['title']}\n")
                    f.write(f"Role: {role}\n")
                    f.write(f"Description: {vid['description']}\n")
                    f.write("This is not a real video file. It is a placeholder for the Leevin OS Training Module test.")
                print(f"   ✅ Created: {filename}")
            else:
                print(f"   ⏩ Exists: {filename}")
            
            total_videos += 1

    print(f"\n🎉 Generation Complete. {total_videos} dummy videos ready in '{VIDEO_DIR}/'.")

if __name__ == "__main__":
    create_dummy_videos()
