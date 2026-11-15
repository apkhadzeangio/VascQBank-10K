"""Monitor state semantics: never infer live ChatGPT task from a commit."""
import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qbank_monitor import state_for, replace_block

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)

    def signal(self, state, hours=0, sha=None):
        return {"state": state, "emitted_at": (self.now - timedelta(hours=hours)).isoformat(),
                "agent_id": "agent1", "run_id": "run1", "commit_sha": sha}

    def test_no_heartbeat_and_old_commit_is_unknown(self):
        self.assertEqual("UNKNOWN", state_for(3, 100, self.now - timedelta(hours=5), None, self.now))

    def test_recent_verified_growth_marks_producing_not_agent_live(self):
        self.assertEqual("PRODUCING", state_for(3, 100, self.now - timedelta(minutes=20), None, self.now))

    def test_fresh_working_heartbeat(self):
        self.assertEqual("IN_PROGRESS", state_for(3, 100, None, self.signal("WRITING"), self.now))

    def test_stale_working_heartbeat_is_unknown(self):
        self.assertEqual("UNKNOWN", state_for(3, 100, None, self.signal("WRITING", hours=4), self.now))

    def test_blocked_requires_explicit_heartbeat(self):
        self.assertEqual("BLOCKED", state_for(3, 100, None, self.signal("BLOCKED"), self.now))

    def test_finished_target(self):
        self.assertEqual("COMPLETE", state_for(100, 100, None, None, self.now))

    def test_unverified_committed_does_not_prove_activity(self):
        self.assertEqual("UNKNOWN", state_for(3, 100, None, self.signal("COMMITTED", sha="wrong"), self.now))

    def test_readme_updater_is_confined_to_monitoring_block(self):
        old = ("Preamble\n<!-- VASCQBANK_PROGRESS_START -->\nExisting progress\n"
               "<!-- VASCQBANK_PROGRESS_END -->\n"
               "<!-- VASCQBANK_MONITORING_START -->\nOld monitor\n"
               "<!-- VASCQBANK_MONITORING_END -->\n")
        fresh = ("<!-- VASCQBANK_MONITORING_START -->\nNew monitor\n"
                 "<!-- VASCQBANK_MONITORING_END -->\n")
        result = replace_block(old, fresh)
        self.assertIn("Existing progress", result)
        self.assertIn("New monitor", result)
        self.assertNotIn("Old monitor", result)
        self.assertEqual(result.count("VASCQBANK_MONITORING_START"), 1)

if __name__ == "__main__":
    unittest.main()
