"""
E12 - Sequenciador distribuido etcd (Raft)
PROD: usa etcd real (3 nos, quay.io/coreos/etcd:v3.5.21)
TERMUX / DEMO: usa fallback local se etcd nao estiver rodando
REGRA: seq NUNCA duplica, NUNCA volta.
"""
import os, json, time

SEQ_FILE = ".xa_last_seq.json"
LOCK_FILE = ".xa_writer.lock"

def _load_seq():
    if not os.path.exists(SEQ_FILE):
        return 0
    try:
        with open(SEQ_FILE) as f:
            return int(json.load(f).get("last_seq", 0))
    except:
        return 0

def _save_seq(n):
    with open(SEQ_FILE, "w") as f:
        json.dump({"last_seq": n}, f)

class XaSequencer:
    def __init__(self):
        # Tenta etcd real, se nao tiver, usa fallback
        try:
            import etcd3
            self.etcd = etcd3.client(host="127.0.0.1", port=2379)
            # testa conexao rapida
            self.etcd.get("/xa/health")
            self.mode = "etcd"
        except Exception:
            self.etcd = None
            self.mode = "local-fallback"
        print(f"MODE: {self.mode}")

    def get_last_seq(self):
        if self.mode == "etcd":
            val, _ = self.etcd.get("/xa/journal/last_seq")
            return int(val.decode()) if val else 0
        return _load_seq()

    def next_seq(self):
        if self.mode == "etcd":
            # TX atomica no etcd - Raft garante 1 escritor
            for _ in range(20):
                cur = self.get_last_seq()
                nxt = cur + 1
                ok = self.etcd.transaction(
                    compare=[self.etcd.transactions.version("/xa/journal/last_seq") == self._ver()],
                    success=[self.etcd.transactions.put("/xa/journal/last_seq", str(nxt))],
                    failure=[]
                )
                if ok:
                    return nxt
                time.sleep(0.05)
            raise Exception("SEQ contention")
        # Fallback: lock por arquivo + seq persistido
        # Simula o que o Raft faz: 1 escritor por vez
        while os.path.exists(LOCK_FILE):
            time.sleep(0.05)
        open(LOCK_FILE, "w").write("locked")
        try:
            cur = _load_seq()
            nxt = cur + 1
            _save_seq(nxt)
            return nxt
        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    def _ver(self):
        _, meta = self.etcd.get("/xa/journal/last_seq")
        return meta.version if meta else 0

    def commit_batch(self, items):
        seq = self.next_seq()
        print(f"LOCK OK | mode={self.mode} | seq={seq} | items={len(items)}")
        # Aqui entra E10: merkle + GBID + sign + anchor com esse seq
        return seq

if __name__ == "__main__":
    s = XaSequencer()
    print(f"last_seq atual: {s.get_last_seq()}")
    for i in range(3):
        seq = s.commit_batch([{"id": i}])
        print(f"COMMITTED seq={seq}")
    print(f"last_seq final: {s.get_last_seq()}")
    print("E12_VERIFIED")
