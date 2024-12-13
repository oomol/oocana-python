from typing import Optional, TypedDict

status_topic = "/service/report/status"
exit_topic = "/service/report/exit"


class ReportStatusPayload(TypedDict):
    serviceHash: str
    sessionId: Optional[str]
    executor: str

# prefix
global_service_topic_prefix = "/service/python"
service_topic_prefix = "/{session_id}/service/python"

# action suffix
service_config_suffix = "action/config"
service_run_suffix = "action/run"
service_ping_suffix = "action/ping"
service_shutdown_suffix = "action/shutdown"

# report suffix
service_prepare_suffix = "report/prepare"
service_pong_suffix = "report/pong"

# topic = {prefix}/{serviceHash}/{suffix}

def prefix(session_id: Optional[str] = None) -> str:
    if session_id:
        return service_topic_prefix.replace("{session_id}", session_id)
    else:
        return global_service_topic_prefix

class ServiceTopicParams(TypedDict):
    sessionId: Optional[str]
    serviceHash: str

def run_action_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_run_suffix])

def ping_action_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_ping_suffix])

def shutdown_action_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_shutdown_suffix])

# TODO: 修改 oomol 端实现，使其为固定的 topic，不需要 sessionId
service_message_topic = "/service/message"

def prepare_report_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_prepare_suffix])

def pong_report_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_pong_suffix])

def exit_report_topic() -> str:
    return exit_topic

def service_config_topic(params: ServiceTopicParams) -> str:
    return "/".join([prefix(params.get('sessionId')), params['serviceHash'], service_config_suffix])

def report_status_topic() -> str:
    return status_topic