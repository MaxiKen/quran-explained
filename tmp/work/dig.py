import sys, json
d = json.load(open("tmp/sources/001.json"))
EN = ["tafsir-al-jalalayn","tafsir-ibn-abbas","tafsir-ibn-kathir","tafsir-maarif-ul-quran","tafsir_initial"]
AR = ["tafsir-as-saadi","tafsir-al-qurtubi","tafsir-al-tabari","tafsir-al-baghawi","tafsir-al-alusi","tafsir-ibn-uthaymeen"]
def show(v, cap=2500, ar_cap=1200):
    key = str(v)
    print("="*70); print("VERSE", key)
    for s in EN:
        t = d.get(key, {}).get(s, "")
        print(f"\n--- {s} [{len(t)} chars]")
        print(t[:cap])
    for s in AR:
        t = d.get(key, {}).get(s, "")
        print(f"\n--- {s} [{len(t)} chars]")
        print(t[:ar_cap])
if __name__ == "__main__":
    show(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 2500, int(sys.argv[3]) if len(sys.argv)>3 else 1200)
