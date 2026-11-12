import os, sys, unittest, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from osim import scheduler, memory, deadlock, storage, system
from osim.common import InputError, load_input

P = [{"pid": "A", "arrival": 0, "burst": 3, "priority": 1}, {"pid": "B", "arrival": 1, "burst": 2, "priority": 2}]
REFS = [7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1]

class Sched(unittest.TestCase):
    def test_fcfs_known(self):
        r = scheduler.simulate(P, "FCFS"); self.assertEqual(r["avg"]["waiting"], 1.0)
    def test_idle_gap(self):
        r = scheduler.simulate([{"pid": "A", "arrival": 5, "burst": 2}], "RR")
        self.assertEqual(r["gantt"][0][0], "IDLE")
    def test_all_algos_finish(self):
        for a in scheduler.ALGOS: self.assertEqual(len(scheduler.simulate(P, a)["table"]), 2)
    def test_srtf_not_worse_than_fcfs(self):
        pr = load_input("data/sample_input.json")["processes"]
        self.assertLessEqual(scheduler.simulate(pr, "SRTF")["avg"]["waiting"], scheduler.simulate(pr, "FCFS")["avg"]["waiting"])
    def test_invalid_burst(self):
        with self.assertRaises(InputError): scheduler.simulate([{"pid": "A", "arrival": 0, "burst": 0}], "FCFS")
    def test_duplicate_pid(self):
        with self.assertRaises(InputError): scheduler.simulate(P + [P[0]], "FCFS")
    def test_bad_quantum(self):
        with self.assertRaises(InputError): scheduler.simulate(P, "RR", 0)
    def test_empty(self):
        with self.assertRaises(InputError): scheduler.simulate([], "FCFS")

class Mem(unittest.TestCase):
    def test_textbook_faults(self):
        self.assertEqual([memory.page_replace(REFS, 3, a)["faults"] for a in ("FIFO", "LRU", "OPT")], [15, 12, 9])
    def test_belady(self):
        b = [1,2,3,4,1,2,5,1,2,3,4,5]
        self.assertEqual((memory.page_replace(b, 3, "FIFO")["faults"], memory.page_replace(b, 4, "FIFO")["faults"]), (9, 10))
    def test_one_frame_all_distinct(self):
        self.assertEqual(memory.page_replace([1,2,3], 1, "LRU")["faults"], 3)
    def test_zero_frames(self):
        with self.assertRaises(InputError): memory.page_replace(REFS, 0, "FIFO")
    def test_negative_page(self):
        with self.assertRaises(InputError): memory.page_replace([1, -2], 2, "FIFO")
    def test_fit(self):
        self.assertEqual(memory.allocate([100,500,200,300,600], [212,417,112,426], "BEST")["unallocated"], [])
        self.assertEqual(memory.allocate([100,500,200,300,600], [212,417,112,426], "FIRST")["unallocated"], [426])
    def test_too_big(self):
        self.assertEqual(memory.allocate([10], [20], "FIRST")["unallocated"], [20])

BK = dict(alloc=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]], maxm=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]], avail=[3,3,2])
class Dead(unittest.TestCase):
    def test_safe(self):
        s = deadlock.safety(**BK); self.assertTrue(s["safe"]); self.assertEqual(s["sequence"], [1,3,4,0,2])
    def test_unsafe_detected(self):
        s = deadlock.safety([[1],[1]], [[2],[2]], [0]); self.assertFalse(s["safe"]); self.assertEqual(s["deadlocked"], [0,1])
    def test_request_granted(self):
        self.assertTrue(deadlock.request(**BK, pid=1, req=[1,0,2])["granted"])
    def test_request_unsafe(self):
        # classic textbook state after P1's (1,0,2) was granted
        st = dict(alloc=[[0,1,0],[3,0,2],[3,0,2],[2,1,1],[0,0,2]], maxm=BK["maxm"], avail=[2,3,0])
        self.assertFalse(deadlock.request(**st, pid=0, req=[0,2,0])["granted"])
    def test_exceeds_max(self):
        self.assertFalse(deadlock.request(**BK, pid=1, req=[9,0,0])["granted"])
    def test_ragged(self):
        with self.assertRaises(InputError): deadlock.safety([[1,2],[1]], [[2,2],[2]], [1,1])
    def test_alloc_gt_max(self):
        with self.assertRaises(InputError): deadlock.safety([[5]], [[2]], [1])

class Disk(unittest.TestCase):
    R = [98,183,37,122,14,124,65,67]
    def test_totals(self):
        t = {a: storage.schedule(self.R, 53, 200, a)["total_movement"] for a in storage.DISK_ALGOS}
        self.assertEqual((t["FCFS"], t["SSTF"], t["LOOK"]), (640, 236, 299))
    def test_out_of_range(self):
        with self.assertRaises(ValueError): storage.schedule([500], 0, 200, "FCFS")
    def test_bad_dir(self):
        with self.assertRaises(ValueError): storage.schedule([1], 0, 10, "SCAN", "left")
    def test_single(self):
        self.assertEqual(storage.schedule([5], 5, 10, "SSTF")["total_movement"], 0)

class Integration(unittest.TestCase):
    def test_bash_bridge(self):
        s = system.host_snapshot(); self.assertIn("kernel", s)
    def test_missing_file(self):
        with self.assertRaises(InputError): load_input("nope.json")
    def test_cli_batch(self):
        r = subprocess.run([sys.executable, "-m", "osim", "--all"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0); self.assertIn("BANKER", r.stdout)
    def test_cli_bad_input(self):
        r = subprocess.run([sys.executable, "-m", "osim", "--all", "--input", "x.json"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

if __name__ == "__main__": unittest.main(verbosity=2)
