from logic.leevin_central import LeevinCentral

print("🚀 Initializing Leevin Central Hub...")
hub = LeevinCentral()

print("\n--- Subsystem Diagnostic ---")
print(f"1. CDM Brain (Enforcer) : {hub.cdm.version}")
print(f"2. CRA Brain (Monitor)  : {hub.cra.version}")
print(f"3. Site Brain (Coord)   : {hub.site.version}")
print(f"4. Coder Brain (Transl) : {hub.coder.version}")
print(f"5. Writer Brain (Compos): {hub.writer.version}")

print("\n✅ Cental Hub Online. All systems nominal.")
