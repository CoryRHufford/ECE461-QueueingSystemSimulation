# Discrete event simulation for a two transmission link queueing system.
#     Author: Cory Hufford
#      Class: ECE 461 - Network Modelling and Performance Analysis
# Instructor: Dr. Gokhan Sahin

import random


class Packet:
    """Object to keep track of a single packet."""
    ARRIVAL_EVENT = 1
    DEPARTURE_EVENT = 2

    def __init__(self, next_event_time, arrival_time):
        self.next_event_time = next_event_time
        self.next_event_type = Packet.ARRIVAL_EVENT
        self.arrival_time = arrival_time
        self.link = None

    def __str__(self):
        return '(Packet in link {}; next event type {} at time {})'.format(self.link, self.next_event_type,
                                                                           self.next_event_time)


class Link:
    """Object representing a single transmission link."""

    def __init__(self, mu, link_buffer_size):
        self.mu = mu
        self.packet_being_served = None
        self.buffer = []
        self.buffer_size = link_buffer_size
        self.num_dropped_packets = 0
        self.num_packets_processed = 0
        self.total_time_spent_by_packets = 0.0  # Total time spent by packets in buffer and transmission (s)

        # Stats to be calculated at the end of the simulation
        self.final_num_transmitted_packets = None
        self.final_average_delay = None
        self.final_blocking_probability = None

    def __str__(self):
        return '(Link with mu={}; buffer {} and packet being served {}; {:d} total packets, {:d} dropped packets)'.format(
            self.mu, self.buffer, self.packet_being_served, self.num_packets_processed, self.num_dropped_packets)

    def add_packet(self, new_packet):
        """Adds a packet to the link or drops it."""
        global current_simulation_time

        self.num_packets_processed += 1
        if len(self.buffer) == self.buffer_size:
            # Link is full - drop the packet
            self.num_dropped_packets += 1
        elif self.packet_being_served is None:
            # Link is idle - put the new packet into service
            new_packet.next_event_time = random.expovariate(self.mu) + current_simulation_time
            new_packet.next_event_type = Packet.DEPARTURE_EVENT
            self.packet_being_served = new_packet
            add_event_to_event_list(new_packet)
        else:
            # Link is not idle but not full
            self.buffer.append(new_packet)

    def finish_serving_packet(self):
        """Moves the next packet from the buffer into service."""
        global current_simulation_time

        self.total_time_spent_by_packets += self.packet_being_served.next_event_time \
                                            - self.packet_being_served.arrival_time
        self.packet_being_served = None
        if len(self.buffer) > 0:
            # There's at least one packet in the buffer - move the next one into service
            self.packet_being_served = self.buffer.pop(0)
            self.packet_being_served.next_event_type = Packet.DEPARTURE_EVENT
            self.packet_being_served.next_event_time = random.expovariate(self.mu) + current_simulation_time
            add_event_to_event_list(self.packet_being_served)

    def reset_stats(self):
        """Resets the stats of the link. Used after processing transient-phase arrivals."""
        self.num_dropped_packets = 0
        self.num_packets_processed = 0
        self.total_time_spent_by_packets = 0.0

    def calculate_final_stats(self):
        """Calculates some final performance stats for the link."""
        self.final_num_transmitted_packets = self.num_packets_processed - self.num_dropped_packets
        self.final_average_delay = self.total_time_spent_by_packets / self.final_num_transmitted_packets
        self.final_blocking_probability = self.num_dropped_packets / self.num_packets_processed


def process_departure_event(packet):
    """See which link the packet is in and finish serving it."""
    if packet.link == 1:
        link1.finish_serving_packet()
    else:
        link2.finish_serving_packet()


def process_arrival_event(packet):
    """Processes an arrival event by:
     1. Choosing a link for the new packet
     2. Placing the packet in buffer or service or dropping it
     3. Creating the next arrival event and putting it in the event list
    """
    global current_simulation_time

    # Choose which link the packet goes to and add/drop it
    if random.random() <= phi1:
        packet.link = 1
        link1.add_packet(packet)
    else:
        packet.link = 2
        link2.add_packet(packet)

    # Make a new arrival event and add it to the event list
    new_packet_time = random.expovariate(lambd) + current_simulation_time
    new_packet = Packet(new_packet_time, new_packet_time)
    add_event_to_event_list(new_packet)


def add_event_to_event_list(event):
    """Places an event in the correct chronological place in the event list."""
    global event_list

    event_list_length = len(event_list)
    for i in range(event_list_length + 1):
        if i == event_list_length:
            event_list.append(event)
        elif event.next_event_time < event_list[i].next_event_time:
            event_list.insert(i, event)
            break


def calculate_final_stats():
    """Calculates the final system performance stats."""
    global final_simulation_time, final_num_packets_processed, final_num_packets_dropped, \
        final_num_packets_transmitted, final_average_delay, final_blocking_probability, current_simulation_time, \
        actual_start_time, num_packets_processed

    final_simulation_time = current_simulation_time - actual_start_time
    final_num_packets_processed = num_packets_processed - num_packets_to_ignore
    final_num_packets_dropped = link1.num_dropped_packets + link2.num_dropped_packets
    final_num_packets_transmitted = final_num_packets_processed - final_num_packets_dropped
    final_average_delay = (link1.total_time_spent_by_packets + link2.total_time_spent_by_packets) \
                          / final_num_packets_processed
    final_blocking_probability = final_num_packets_dropped / final_num_packets_processed


def print_results():
    global final_simulation_time, final_num_packets_processed, final_num_packets_dropped, \
        final_num_packets_transmitted, final_average_delay, final_blocking_probability, num_packets_to_ignore, lambd, \
        phi1, link1, link2

    print('Actual arrivals processed: {:d}'.format(final_num_packets_processed))
    print('Transient-phase arrivals ignored: {:d}'.format(num_packets_to_ignore))
    print('Total simulation time: {:f}'.format(final_simulation_time))
    print('')
    print(' ----------------- Entire system: ----------------- ')
    print('            Total packets: {:d}'.format(final_num_packets_processed))
    print('          Dropped packets: {:d}'.format(final_num_packets_dropped))
    print('     Blocking probability: {:f}'.format(final_blocking_probability))
    print('            Average delay: {:f}'.format(final_average_delay))
    print('       Average throughput: {:f}'.format(final_num_packets_transmitted / final_simulation_time))
    print('Average number of packets: {:f}'.format(lambd * final_average_delay * (1 - final_blocking_probability)))
    print('')
    print(' --------------------- Link 1: -------------------- ')
    print('            Total packets: {:d}'.format(link1.num_packets_processed))
    print('          Dropped packets: {:d}'.format(link1.num_dropped_packets))
    print('     Blocking probability: {:f}'.format(link1.final_blocking_probability))
    print('       Total packet delay: {:f}'.format(link1.total_time_spent_by_packets))
    print('            Average delay: {:f}'.format(link1.final_average_delay))
    print('       Average throughput: {:f}'.format(link1.final_num_transmitted_packets / final_simulation_time))
    print('Average number of packets: {:f}'.format(
        phi1 * lambd * link1.final_average_delay * (1 - link1.final_blocking_probability)))
    print('')
    print(' --------------------- Link 2: -------------------- ')
    print('            Total packets: {:d}'.format(link2.num_packets_processed))
    print('          Dropped packets: {:d}'.format(link2.num_dropped_packets))
    print('     Blocking probability: {:f}'.format(link2.final_blocking_probability))
    print('       Total packet delay: {:f}'.format(link2.total_time_spent_by_packets))
    print('            Average delay: {:f}'.format(link2.final_average_delay))
    print('       Average throughput: {:f}'.format(link2.final_num_transmitted_packets / final_simulation_time))
    print('Average number of packets: {:f}'.format(
        (1 - phi1) * lambd * link2.final_average_delay * (1 - link2.final_blocking_probability)))


def save_results():
    """Saves some of the performance stats to a .csv file."""
    global final_simulation_time, final_num_packets_processed, final_num_packets_dropped, \
        final_num_packets_transmitted, final_average_delay, final_blocking_probability, num_packets_to_ignore

    with open('SimulationResults.csv', 'w') as file:
        file.write('Actual arrivals processed,Transient arrivals ignored\n')
        file.write('{:d},{:d}\n'.format(final_num_packets_processed, num_packets_to_ignore))

        file.write('Perspective,Blocking probability,Average delay,Average throughput,Average number of packets\n')
        file.write('System,{:f},{:f},{:f},{:f}\n'.format(final_blocking_probability, final_average_delay,
                                                         final_num_packets_transmitted / final_simulation_time,
                                                         lambd * final_average_delay * (
                                                                 1 - final_blocking_probability)))
        file.write('Link 1,{:f},{:f},{:f},{:f}\n'.format(link1.final_blocking_probability, link1.final_average_delay,
                                                         link1.final_num_transmitted_packets / final_simulation_time,
                                                         phi1 * lambd * link1.final_average_delay * (
                                                                 1 - link1.final_blocking_probability)))
        file.write('Link 2,{:f},{:f},{:f},{:f}\n'.format(link2.final_blocking_probability, link2.final_average_delay,
                                                         link2.final_num_transmitted_packets / final_simulation_time,
                                                         (1 - phi1) * lambd * link2.final_average_delay * (
                                                                 1 - link2.final_blocking_probability)))


# Simulation settings
lambd = 8  # Poisson rate, intentionally misspelled (packets/s)
mu1 = 5  # Average service rate of link 1 (packets/s)
mu2 = 5  # Average service rate of link 2 (packets/s)
phi1 = 0.5  # Chance of a packet being routed to link 1
buffer_size = 5
num_packets_to_process = 2000000
num_packets_to_ignore = 1000000  # Number of transient-phase arrivals to ignore

# Simulation variables
current_simulation_time = 0.0
event_list = []
link1 = Link(mu1, buffer_size)
link2 = Link(mu2, buffer_size)
actual_start_time = None  # Time of first non-transient-phase arrival
num_packets_processed = 0

# Final system statistics to calculate at the end
final_simulation_time = None
final_num_packets_processed = None
final_num_packets_dropped = None
final_num_packets_transmitted = None
final_average_delay = None
final_blocking_probability = None

if __name__ == '__main__':
    # Create first arrival event
    first_packet_time = random.expovariate(lambd)
    first_packet = Packet(first_packet_time, first_packet_time)
    add_event_to_event_list(first_packet)
    num_packets_processed = 1

    # Process transient phase arrivals
    while num_packets_processed < num_packets_to_ignore:
        next_event = event_list.pop(0)
        current_simulation_time = next_event.next_event_time
        if next_event.next_event_type == Packet.ARRIVAL_EVENT:
            process_arrival_event(next_event)
            num_packets_processed += 1
        else:
            process_departure_event(next_event)

    # Reset stats to ignore transient phase arrivals
    link1.reset_stats()
    link2.reset_stats()
    actual_start_time = current_simulation_time

    # Process actual arrivals
    while num_packets_processed < num_packets_to_process:
        next_event = event_list.pop(0)
        current_simulation_time = next_event.next_event_time
        if next_event.next_event_type == Packet.ARRIVAL_EVENT:
            process_arrival_event(next_event)
            num_packets_processed += 1
        else:
            process_departure_event(next_event)

    # Calculate final stats and print the results
    link1.calculate_final_stats()
    link2.calculate_final_stats()
    calculate_final_stats()
    save_results()
    print_results()
