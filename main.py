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
        if node.prev != self.dStart and node != self.dStart.next:
            self.removeNode(node)
            self.addToFront(node)

    def reset(self):
        self.dStart.next = self.dEnd
        self.dEnd.prev = self.dStart
        self.length = 0

class LRUcache:
    def __init__(self,capacity=20,ttl=120):
        self.hashmap = {}
        self.chain = LRUchain()
        self.capacity = capacity
        self.ttl = ttl if ttl and ttl>0 else None
        self.hits = 0
        self.misses = 0
    
    def _calc_expiry(self):
        return time.monotonic() + self.ttl if self.ttl is not None else None

    def _remove_node(self,node):
        self.chain.removeNode(node)
        del self.hashmap[node.key]

    def _remove_lru(self):
        lru = self.chain.removeLRU()
        if lru:
            del self.hashmap[lru.key]
            
    def _create_node(self,key,val):
        node = LRUnode(key,val)
        node.expiry = self._calc_expiry()
        return node
    
    def _insert_node(self,node):
        self.chain.addToFront(node)
        self.hashmap[node.key] = node

    def _is_expired(self,node):
        return self.chain.isExpired(node.expiry)
    
    def _cleanup_expired_back(self):
        while self.chain.length > 0:
            lru = self.chain.dEnd.prev
            if not self.chain.isExpired(lru.expiry):
                break
            self._remove_lru()
    
    def _evict_if_needed(self):
        if self.chain.length >= self.capacity:
            self._remove_lru()

    def get(self,key):
        node = self.hashmap.get(key)

        if not node:
            self.misses += 1
            return None

        if self._is_expired(node):
            self._remove_node(node)
            self.misses += 1
            return None
        
        self.hits += 1
        self.chain.bringForward(node)
        return node.val
        
    def put(self,key,val):

        if self.capacity == 0:
            return

        node = self.hashmap.get(key)

        if node:
            node.val = val
            node.expiry = self._calc_expiry()
            self.chain.bringForward(node)
            return
        
        node = self._create_node(key,val)
        
        if self.chain.length < self.capacity:
            self._insert_node(node)
            return

        self._cleanup_expired_back()
        self._evict_if_needed()
        self._insert_node(node)
    
    def stats(self):
        rate = self.hits/(self.hits+self.misses) if self.hits+self.misses != 0 else 0.0
        return f'Hits: {self.hits}\nMisses: {self.misses}\nHit rate: {rate:.2%}'

    def __len__(self):
        return self.chain.length

    def delete(self,key):
        node = self.hashmap.get(key)
        if node:
            self._remove_node(node)
    
    def clear(self):
        self.hashmap.clear()
        self.chain.reset()
        self.hits = 0
        self.misses = 0

A = LRUcache()
A.put('hi',1)
A.put('bye',2)

print(A.get('hi'))
print(A.get('bye'))
print(A.get('yo'))

print(A.chain)
print(A.stats())