import tcell_agent
from tcell_agent.sensor_events import AppSensorEvent


def send_event(
        appsensor_meta,
        detection_point,
        parameter,
        meta,
        payload=None,
        pattern=None):
    tcell_agent.agent.TCellAgent.send(AppSensorEvent(
        detection_point,
        parameter,
        appsensor_meta.location,
        appsensor_meta.remote_address,
        appsensor_meta.route_id,
        meta,
        appsensor_meta.method,
        payload=payload,
        user_id=appsensor_meta.user_id,
        session_id=appsensor_meta.session_id,
        pattern=pattern
    ))
