"""Global.py - singleton and utility for Flows"""

import flows.ConfigManager
import flows.FlowsLogger
import flows.ProcessManager
import flows.MessageDispatcher

VERSION = '0.8.5'
CONFIG_MANAGER = flows.ConfigManager.ConfigManager.default_instance()
LOGGER_INSTANCE = flows.FlowsLogger.FlowsLogger.default_instance()
LOGGER = flows.FlowsLogger.FlowsLogger.default_instance().get_logger()
PROCESS_MANAGER = flows.ProcessManager.ProcessManager.default_instance()
MESSAGE_DISPATCHER = flows.MessageDispatcher.MessageDispatcher.default_instance()
