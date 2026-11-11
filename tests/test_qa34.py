import sqlite3
import subprocess
import sys


def test_sqlite_writes_are_safe_across_processes(tmp_path):
    database = tmp_path / "multi-process.sqlite3"
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE writes (worker INTEGER NOT NULL, item INTEGER NOT NULL, PRIMARY KEY(worker,item))")

    worker = '''import sqlite3,sys
path,worker=sys.argv[1],int(sys.argv[2])
for item in range(40):
    with sqlite3.connect(path,timeout=20) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT INTO writes(worker,item) VALUES(?,?)",(worker,item))
        db.commit()
'''
    processes = [
        subprocess.Popen([sys.executable, "-c", worker, str(database), str(index)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for index in range(4)
    ]
    failures = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=60)
        if process.returncode:
            failures.append((process.returncode, stdout, stderr))
    assert not failures, failures

    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM writes").fetchone()[0] == 160
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
