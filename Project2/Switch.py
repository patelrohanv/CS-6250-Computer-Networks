# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015
			    												

from Message import *
from StpSwitch import *

class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):    
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)
        #TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.

        # variable to store switchID (inherited from super), currently the root
        # variable to store distance to switch's root, default 0
        # list to store active links, default is empty
        # variable to keep track of which neighbor it goes through to get to root, default itself is root

        self.root = self.switchID
        self.distance = 0
        self.activeLinks = []
        self.pathThrough = self.switchID

    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	    #      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)
        
        for neighbor in self.links:
            # message fields
                # root = id of the switch thought to be the root by the origin switch
                # distance = the distance from the origin to the root node
                # origin =  the ID of the origin switch 
                # destination = the ID of the destination switch
                # pathThrough = Boolean value indicating the path to the claimed root from the origin passes through the destination 
            msg = Message(self.root, self.distance, self.switchID, neighbor, False)
            self.send_message(msg)    
        return

    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

        # updating switch.root
        # update switch root and distance if message has lower root
        # update switch distance if message has shorter distance to same root
        
        if self.root > message.root:
            self.root = message.root
            self.distance = message.distance + 1
            self.send_new_messages(message.origin)
        if self.distance + 1 > message.distance and self.root == message.root:
            self.distance = message.distance + 1 
            self.send_new_messages(message.origin)

        # update switch.activeLinks
        # add new link to activeLinks (and potentially remoe old link) if switch finds new path to root through different neighbor
        # add message.originID to activeLinks if message.pathThrough == True and message.originID not in activeLinks
        # remove (maybe) message.originID from activeLinks if message.pathThrough == False and message.originID in activeLinks
        if message.origin not in self.activeLinks:
            self.activeLinks.append(message.origin)
            self.send_new_messages(message.origin)
        elif message.pathThrough and message.origin not in self.activeLinks:
            self.activeLinks.append(message.origin)
            self.send_new_messages(message.origin)
        elif not message.pathThrough and message.origin in self.activeLinks:
            self.activeLinks.remove(message.origin)
            self.send_new_messages(message.origin)

        print '-------------------------'
        print 'mRoot {} mDist {} mOr {} mDest {}  mThrough{}'.format(message.root, message.distance, message.origin, message.destination, message.pathThrough)
        print 'sRoot {} sDist {} sAct {} sThrough {}'.format(self.root, self.distance, self.activeLinks, self.pathThrough)
        print '+++++++++++++++++++++++++'
        return

    def send_new_messages(self, origin):
        # pathThrough is only TRUE if destination(neighbor) is the original message's originID
        for neighbor in self.activeLinks:
            self.send_message(Message(self.root, self.distance, self.switchID, neighbor, neighbor == origin))

    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.
        self.activeLinks.sort()
        links = ['{} - {}'.format(self.switchID, link) for link in self.activeLinks]
        return ', '.join(links)
