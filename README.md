# ECE461-QueueingSystemSimulation
This is a discrete event simulation for a two transmission link queueing system, created as part of a university project.
<br />
<br />
Written by Cory Hufford  
ECE 461 - Network Modelling and Performance Analysis, Dr. Gokhan Sahin  
Miami University College of Engineering and Computing
<br />
<br />
System description:
 * Packets arrive according to a Poisson process with average interarrival time of 1/lambda
 * Packets are instantaneously placed in one of two outgoing transmission link queues
 * Service times are distributed exponentially at each transmission link with different average service rates mu1 and mu2
 * An arriving packet joins link 1 with a fixed probability phi1
