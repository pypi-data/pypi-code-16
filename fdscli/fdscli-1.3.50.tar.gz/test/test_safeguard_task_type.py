# Copyright 2017 Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
import collections
from fdscli.model.task.safeguard_task_status import SafeGuardTaskType

class SafeGuardTaskTypeTests(BaseCliTest):
    '''Tests for the SafeGuardTaskType enum.
    '''

    def test_table_display_string(self):

        assert "volume snapshot export" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_s3_snapshot )
        assert "volume export" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_s3_checkpoint )
        assert "volume incremental replicate" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_replica_incremental )
        assert "volume replicate" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_replica_checkpoint )
        assert "volume snapshot copy" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_remoteclone_snapshot )
        assert "volume copy" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export_remoteclone_checkpoint )
        assert "snapshot" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.snapshot )
        assert "incremental" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.incremental )
        assert "import" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.volume_import )
        assert "export" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.export )
        assert "unknown" == SafeGuardTaskType.getTableDisplayString( SafeGuardTaskType.unknown )

    def test_str(self):

        assert "import" == str( SafeGuardTaskType.volume_import )
        assert "export" == str( SafeGuardTaskType.export )
        assert "snapshot" == str( SafeGuardTaskType.snapshot )
        assert "export_remoteclone_checkpoint" == str( SafeGuardTaskType.export_remoteclone_checkpoint )
        assert "export_s3_checkpoint" == str( SafeGuardTaskType.export_s3_checkpoint )
