class LRUnode:
    def __init__(self,key=None,val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None
    
class LRUchain:
    def __init__(self):
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
    
class LRUcache:
    def __init__(self):
        self.hashmap = {}
        self.chain = LRUchain()
        self.capacity = 20

        self.hits = 0
        self.misses = 0
            
    def get(self,key):
        if key in self.hashmap:
            #CACHE HIT
            
            self.hits += 1

            node = self.hashmap[key]

            if node.prev != self.chain.dStart:
                self.chain.removeNode(node)
                self.chain.addToFront(node)

            return node.val

        else:
            #CACHE MISS

            self.misses += 1

            return None

    def put(self,key,val):
        if key in self.hashmap:
            #UPDATE AND BRING UP OLD CACHE

            node = self.hashmap[key]
            node.val = val

            if node.prev != self.chain.dStart:
                self.chain.removeNode(node)
                self.chain.addToFront(node)
        
        else:
            #ADD CACHE

            node = LRUnode(key,val)
            self.hashmap[key] = node

            if self.chain.length == self.capacity:
                lru = self.chain.removeLRU()
                if lru:
                    del self.hashmap[lru.key]

            self.chain.addToFront(node)
    
    def stats(self):
        return f'Hits: {self.hits}\nMisses: {self.misses}\nHit rate: {self.hits/(self.hits+self.misses) if self.hits+self.misses != 0 else "N/A"}'

A = LRUcache()
A.put('hi',1)
A.put('bye',2)
print(A.chain)
print(A.stats())