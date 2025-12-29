from logic.writer_brain import BrainWriter

print("🧪 Testing BrainWriter (The Composer)...")
writer = BrainWriter()
print(f"✅ Loaded: {writer.version}")

print("\n--- Generating Shell: Demographics ---")
df = writer.generate_shell("Demographics")
print(df.to_string(index=False))

print("\n--- Generating Shell: Invalid ---")
df_invalid = writer.generate_shell("Safety")
print(df_invalid.to_string(index=False))
