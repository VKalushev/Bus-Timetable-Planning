# Sent by the gateway when it starts, used to catch any nodes that started before the gateway.
TOPIC_REQUEST_REG = "registration/request"

# Sent by an edge node to make its existance known to the gateway.
TOPIC_BUS_REG = "registration/bus"
TOPIC_STATION_REG = "registration/station"

# Sent by an edge node as a will to make its disconnect known to the gateway
TOPIC_BUS_DEREG = "deregistration/bus"
TOPIC_STATION_DEREG = "deregistration/station"

# Topics used by edge nodes to update their counter data
TOPIC_BUS_COUNTER = "bus/counter/%s"
TOPIC_STATION_COUNTER = "station/counter/%s"

# The same but without the string parameters for checking in gateway
TOPIC_BUS_COUNTER_CHK = "bus/counter/"
TOPIC_STATION_COUNTER_CHK = "station/counter/"

# Topic for the web api
TOPIC_WEB_BUS_COUNTER = "web/bus/counter/%s"
