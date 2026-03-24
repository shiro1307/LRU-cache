#LRUCACHEMINI BY SHARDUL R. HIROLIKAR

import time

class LRUnode:
    def __init__(self,key=None,val=None, expiry = None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None
        self.expiry = expiry 

class LRUchain:
    def __init__(self, timeout=None):
        self.dStart = LRUnode()
        self.dEnd = LRUnode()

        self.dStart.next = self.dEnd
        self.dEnd.prev = self.dStart

        self.length = 0
    
    def __repr__(self):
        res = []
        curr = self.dStart.next
        while curr!=self.dEnd:
            res.append(f'{curr.key}:{curr.val}')
            curr = curr.next
        return '[' + ', '.join(res) + ']'

    def isExpired(self,exp):
        return exp is not None and time.monotonic() >= exp

    def addToFront(self,node):

        t = self.dStart.next

        node.prev = self.dStart
        node.next = t 

        self.dStart.next = node
        t.prev = node

        self.length += 1
    
    def removeNode(self,node):

        tN, tP = node.next, node.prev

        tP.next = tN
        tN.prev = tP

        node.prev = None
        node.next = None

        self.length -= 1
    
    def removeLRU(self):
        if self.length == 0:
            return
        lru = self.dEnd.prev
        self.removeNode(lru)
        return lru
    
    def bringForward(self,node):
        if node.prev != self.dStart:
            self.removeNode(node)
            self.addToFront(node)

class LRUcache:
    def __init__(self,capacity=20,ttl=120):
        self.hashmap = {}
        self.chain = LRUchain()
        self.capacity = capacity
        self.ttl = ttl if ttl and ttl>0 else None
        self.hits = 0
        self.misses = 0
    
    def calcExpiry(self):
        return time.monotonic() + self.ttl if self.ttl is not None else None

    def get(self,key):
        if key in self.hashmap:
            #CACHE KEY EXISTS, CHECK IF HAS EXPIRED OR NOT
            #GET NODE 
            node = self.hashmap[key]
            if self.chain.isExpired(node.expiry):
                #CACHE HAS EXPIRED, TREAT AS A CACHE MISS
                #MISS COUNTER INCREMENT
                self.misses += 1
                #GET RID OF EXPIRED NODE IN LRU
                self.chain.removeNode(node)
                del self.hashmap[key]
                return None
            else:
                #CACHE HASN'T EXPIRED YET, VALID CACHE HIT
                #CACHE HIT COUNTER INCREMENT
                self.hits += 1
                #BRING NODE FORWARD IN LRU CHAIN
                self.chain.bringForward(node)
                return node.val
        else:
            #CACHE MISS
            #MISS COUNTER INCREMENT
            self.misses += 1
            return None

    def put(self,key,val):

        if self.capacity == 0:
            return

        if key in self.hashmap:
            #UPDATE AND BRING UP OLD CACHE
            #GET OLD NODE AND UPDATE VAL
            node = self.hashmap[key]
            node.val = val
            node.expiry = self.calcExpiry()
            #BRING OLD NODE FORWARD IN LRU CHAIN
            self.chain.bringForward(node)
        else:

            #ADD CACHE
            #CREATE NODE AND ADD TO HASHMAP FOR O(1) LOOKUP
            node = LRUnode(key,val)
            node.expiry = self.calcExpiry()
            
            #SKIP THE LOOP AHEAD IF CAPACITY ISN'T EXCEEDED
            if self.chain.length < self.capacity:
                self.chain.addToFront(node)
                self.hashmap[key] = node
                return
            
            #GET RID OF END DEAD NODES
            while self.chain.length > 0 and self.chain.isExpired(self.chain.dEnd.prev.expiry):
                lru = self.chain.removeLRU()
                if lru:
                    del self.hashmap[lru.key]

            #IF CACHE STILL EXCEEDS CAPACITY, GET RID OF LEAST RECENTLY USED CACHE NODE
            if self.chain.length >= self.capacity:
                lru = self.chain.removeLRU()
                if lru:
                    del self.hashmap[lru.key]

            #ADD CREATED NODE TO THE FRONT OF LRU CHAIN
            self.chain.addToFront(node)
            self.hashmap[key] = node
    
    def stats(self):
        return f'Hits: {self.hits}\nMisses: {self.misses}\nHit rate: {self.hits/(self.hits+self.misses) if self.hits+self.misses != 0 else "N/A"}'

A = LRUcache()
A.put('hi',1)
A.put('bye',2)

print(A.get('hi'))
print(A.get('bye'))
print(A.get('yo'))

print(A.chain)
print(A.stats())