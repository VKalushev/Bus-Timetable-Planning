from datetime import datetime

PREDICTION = """For hours: %s - %s on route %d

Average bus capacity: %d%%
Current bus Frequency for the hour is: %d
Bus IDs using this route are: %s"""

SUGGEST_UP = "It is suggested that the bus frequency is increased to: %s"
SUGGEST_DOWN = "It is suggested that the bus frequency is decreased to: %s"


class Frequency:

    def __init__(self, gateway):
        self.gateway = gateway
        self._data = None
        self._bus_routes = []
    
    def get_prediction(self):
        self._data = self.gateway.get_route_data(1)
        self._bus_routes = []

        # For loop which would allow us to store all the different route ids which we have in the data
        for current in self._data:
            if not self._bus_routes.__contains__(current['route']):
                self._bus_routes.append(current['route'])

        for route in self._bus_routes:
            current_hour = 0  
            hour_found = False

            # While loop to make sure that we've gone through all the different hours provided in the data
            while current_hour < 24:
                current_route_bus_ids = []
                current_route_bus_frequency = 0
                total_passengers = 0
                amount_of_data_collection = 0  # Amount of times we've collected data from the different busses
                if not hour_found:
                    current_hour = datetime.strptime(self._data[0]['timestamp'], "%Y-%m-%dT%H:%M:%S").hour
                    hour_found = True
                else:
                    current_hour += 1
                    
                # For Loop with which we get the specific bus ids for the specific routes for the specific hours and
                # also calculates the bus frequency
                for current in self._data:
                    if current['route'] == route:
                        if not current_route_bus_ids.__contains__(current['id']):
                            current_route_bus_ids.append(current['id'])
                            current_bus_timestamp = datetime.strptime(current['timestamp'], "%Y-%m-%dT%H:%M:%S")
                            if current_bus_timestamp.hour == current_hour:
                                current_route_bus_frequency += 1

                        if current_bus_timestamp.hour == current_hour:
                            total_passengers += current['percentage']
                            amount_of_data_collection += 1
                

                if amount_of_data_collection > 0:
                    # Since everytime we collect the amount of passengers we add to the total amount of
                    # passengers we would need to know how many times we did it per bus so if we increase the bus
                    # frequency we would know how many amount of collections to add
                    amount_of_collections_by_bus = amount_of_data_collection/current_route_bus_frequency

                    # Summing the average amount of passengers per bus
                    average_passengers_for_current_route = total_passengers/amount_of_data_collection

                    # Build prediction string                    
                    prediction = PREDICTION % (str(current_hour) + ':00:00',
                                               str(current_hour + 1) + ':00:00',
                                               route,
                                               average_passengers_for_current_route*100,
                                               current_route_bus_frequency, str(current_route_bus_ids))

                    # If/While statements which help us suggest an increasement or decreasement in the bus frequency
                    if average_passengers_for_current_route >= 0.8:
                        while average_passengers_for_current_route >= 0.75:
                            amount_of_data_collection += amount_of_collections_by_bus
                            average_passengers_for_current_route = total_passengers/amount_of_data_collection
                            current_route_bus_frequency += 1
                        prediction += '\n' + SUGGEST_UP % current_route_bus_frequency
                    elif average_passengers_for_current_route <= 0.20 and current_route_bus_frequency >= 2:
                        while average_passengers_for_current_route <= 0.20 and current_route_bus_frequency >= 2:
                            amount_of_data_collection -= amount_of_collections_by_bus
                            average_passengers_for_current_route = total_passengers/amount_of_data_collection
                            current_route_bus_frequency -= 1
                        prediction += '\n' + SUGGEST_DOWN % current_route_bus_frequency

                    print('Prediction sent to adafruit dashboard')
                    self.gateway.aio.send('cm2110-recommend', prediction)
