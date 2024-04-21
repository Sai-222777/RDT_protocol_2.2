import random

class SimulatedChannel:
    def __init__(self, loss_rate=0.3):
        self.loss_rate = loss_rate
        self.packet=None
    
    def send(self, packet):                      # the packet is sent properly through the channel 
        if random.random() >= self.loss_rate:    # with a probability of 0.7
            self.packet = packet
        else:
            self.packet=None
    
    def receive(self):                          # the packet is received properly from the channel 
        if random.random() >= self.loss_rate:   # with a probability of 0.7
            return self.packet
        return None

class RDTSender:
    def __init__(self,channel):
        self.channel = channel
        self.seq_no = 1
    #    self.t = 0

    def rdt_send(self,packet,receiver):  # the sender pushes the packet through the channel
    #    self.t += 1
        self.channel.send(packet)                                            
        print(f"Sending {packet[0]} with sequence number {packet[1]}")       
        receiver.rdt_receive()           # this calls the receiver to check and acknowledge the
        ack = self.channel.receive()     # packet if received, the sender waits
        
        # if ack is lost, hence "None" is received, so retransmit and wait again
        if ack == None :                
            print('Received ACK None. Transfer Unsuccessful')
            print()
            print()
            self.rdt_send(packet,receiver)

        # if ack with a different seq no is received, this means the ack received is a duplicate
        # so retransmit and wait again
        elif ack != packet[1] :
            print(f"Received ACK {1-packet[1]}. Transfer Unsuccessful")
            print()
            print()
            self.rdt_send(packet,receiver)

        # if ack with the expected seq no is received, this means 
        #  the packet has been sent properly !
        else :
            print(f"Received ACK {packet[1]}. Transfer Successful")
            print()
            print()
            
    def send_packet(self,packet):
        self.channel.send(packet)

    def make_packet(self,data): 
        self.seq_no  = 1 - self.seq_no                
        # here the protocol recieves data from above  and makes a packet with a sequence number
        # that alternates between '0' and '1' for every consecutive packet to be sent

        self.packet = data , self.seq_no    
        # the packet is a tuple containing data at index 0 and the seq no at index 1
        return self.packet                      

class RDTReceiver:
    def __init__(self,channel):
        self.channel = channel
        self.last_success_seq_no = 1

    def rdt_receive(self):
        packet = self.channel.receive()  # receiver takes the packet from the channel  

        # if the packet is lost then the packet recieved is "None"
        # send an ack acknowledging the previous packet, i.e, the last successfully received packet
        # so send ack with previous received packet's seq no 
        if packet == None :
            print("Transfer Unsuccessful")
            print(f"sending ACK {self.last_success_seq_no}")
            self.send_acknowledgement(self.last_success_seq_no)

        else:
            # if packet is received, the current seq no should be different than the one 
            # previously received
            self.expected_seq_no = 1 - self.last_success_seq_no 
            
            # packet received, but incorrect seq no, so send an ack acknowledging the previous packet
            # and wait for the packet with the correct seq no to arrive
            if packet[1] != self.expected_seq_no:
                print("Transfer Unsuccessful")
                print(f"sending ACK {self.last_success_seq_no}")
                self.send_acknowledgement(self.last_success_seq_no)
            
            # packet received, along with the correct seq no, so send an acknowledgment with
            # the currently recieved packet's seq no, and wait for a packet with the next seq no
            # in the pattern, i.e, (0 or 1),  to arrive
            else:
                data_item = packet[0].split()[0]
                content = packet[0].split()[1]
                print(f"Received {data_item} with {content} and sequence number {self.expected_seq_no}") 
                print(f"sending ACK {self.expected_seq_no}")
                self.last_success_seq_no = self.expected_seq_no
                self.send_acknowledgement(self.last_success_seq_no)

    def receive_packet(self):
        data = self.channel.receive()
        print(data)

    def send_acknowledgement(self, seq_num):  # sends an ack for a particular seq no
        self.channel.send(seq_num)
        

text = []
info = open('test_rdt.txt', 'r')
count = 0              

while True:                        # loop to store all the data and it's contents used for testing
    line = info.readline()
    text.append(line.strip())
    if not line:
        break
    count += 1                     # final count gives us the total number of packets for testing

info.close()

virtual_channel = SimulatedChannel()
receiver = RDTReceiver(virtual_channel)
sender = RDTSender(virtual_channel)

i = 0
while i < count :                  # loop to send one-by-one data and it's content
    data = text[i]
    packet = sender.make_packet(data)  # packet is first created
    sender.rdt_send(packet,receiver)   # sender then sends the packet over the dedicated virtual channel
    i += 1
#print(sender.t)   
    
