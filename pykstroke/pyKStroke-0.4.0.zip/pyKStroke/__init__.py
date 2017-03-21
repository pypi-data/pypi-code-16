__all__=["ksSys","ksApp"]

import ctypes

DEFAULT_EXIT_KEY_CODE= 27 #ESC
KEY_STATE_WORD = ("up","down")

class KeyInput: 
    """Base input class.
Should be used if you need key or character as the only one input. Does not echo to the screen. 

    Method list:
        __call__
        _test
        
    """ 

    def __init__(self): 
        """Initialize the base instance for the current OS."""
        self._impl = KeyInput._OSImpl()
        
    def __call__(self):
        """Return the pressed key as tuple (unicode char, event type code, event type string) then exit."""
        self.keycode = None
        def _keyEvent():
            self.keycode = self._impl._retkey   
            self._impl.set_exit(True)
        self._impl.key_event = _keyEvent
        self._impl()
        key,state = self.keycode #validstate code only > 0
        return (key,state,KEY_STATE_WORD[state])

    def _test(self):
        """Try if the class implementation work well. Print on screen the pressed character and character code.
Use this as example for understand how the class work.

        """
        print 'Press a key' 
        key,state,word = self.__call__()
        print 'you pressed key:',unichr(key),'  with state:',state,'/',word,'  ASCII code:',key       
     
           
class KeyEvent(KeyInput):
    """Inherits from KeyInput class.
Run keyInput.__call__() method in a loop. Return an		k	116	int
y pressed key from an handler function. 
This is the equivalent keyYield class used in ksApp.py module, but instead of a yield call use the handler loop.
The loop will be executed under the same main thread. 
If initialized after a KeyThread instance may cause some weird events when executed.

    Method list:
        __call__
        set_event
        _test        
         
    """

    def __init__(self,exitkeycode=DEFAULT_EXIT_KEY_CODE):
        """Initialize itself and the inherited class.
        Parameters:
            exitkeycode - insert an ASCII key number that will be used to stop input keys. Default value is 27 (ESC key).
        
        """
        KeyInput.__init__(self)
        self.EXIT_KEY_CODE=exitkeycode
        self.set_exit=self._impl.set_exit

    def __call__(self):
        """Start the key event handler. 
Initialize the event handler and put the *keyEvent.set_event()* method inside it, then starts it.
The pressed key is returned as tuple in the self.keycode variable (unicode char, event type code, event type string).

        """

        def _keyEvent():
            key,state = self._impl._retkey
            self.keycode = (key,state,KEY_STATE_WORD[state])
            self.set_event()   
            if key==self.EXIT_KEY_CODE: #improve, check the type before the condition.
                self._impl.set_exit(True)
        self._impl.key_event=_keyEvent
        self._impl()

    def set_event(self):
        """Override this method if you would to loop inside the handler. Use self.keycode inside it for extract the pressed key.
        
        """

        pass
    
    def _test(self):
        """Try if the class implementation work well. Print on screen the pressed character and character code.
Use this as example for understand how the class work.

        """

        print 'Press a key'
        def testEvent():
            key,state,word = self.keycode
            print 'you pressed key:',unichr(key),'  with state:',state,'/',word,'  ASCII code:',key 
        self.set_event=testEvent
        self.__call__()


class KeyThread():
    """Used with build-in threading package. Should be used when you need a fast input response, independently from the main process execution.
Run and instance of KeyEvent class in a separate thread and return any pressed key in asynchronous mode. (best mode)
Character 27 (default ESC key) for terminate the code. 

    Method list:
        __call__
        stop
        _thread_event
        _runcode
        _check_buffer
        _test

    Property list:
        keycode

    """

    from Queue import Queue as _Queue
    import Queue

    def __init__(self,thread_id=None,max_buffer=0,exitkeycode=DEFAULT_EXIT_KEY_CODE): 
        """Initialize thread object. Check if the system support the build-in threading package. If thread_id is None create a new thread, check if the given thread id is associated with an existing thread otherwise. If this is true join the thread with the class instance.
    
    Parameters:
        thread_id - the unique thread id number associated with the run threading object.
        max_buffer - the  maximum characters buffer which serves for transfer characters from the child thread to the main thread. Default value=0 (unlimited characters).
        exitkeycode - insert an ASCII key number that will be used to stop input keys. Default value is 27 (ESC key).

        """

        try:
            import threading as _threading
        except ImportError:
            try:
                import dummy_threading as _threading
            except (ImportError):              
                raise ImportError ("""Threading not supported.
You can't instanciate this class.

                      """)
                del self   
        else:                
            self.keybuffer = KeyThread._Queue(self._check_buffer(max_buffer))
            self.quitevent = _threading.Event()
            
            self.EXIT_KEY_CODE = exitkeycode
            keyev = KeyEvent(self.EXIT_KEY_CODE)
            
            KeyEvent.set_event = KeyThread._thread_event #could be overwritten as instance method instead of class method, but give me some errors. This may raise some implementation problems if you instantiathe this class before the KeyEvent class. 
            keyev.keybuffer = self.keybuffer
            keyev.quitevent = self.quitevent

            if thread_id != None and type(thread_id)!= int and type(thread_id)!= object:
                raise TypeError("thread_id parameter must be a thread Number or thread Object.")
            else:
                if thread_id == None:
                    self._thread=_threading.Thread(target=KeyThread._runcode,args=(keyev,))
                else:
                    for tobj in _threading.enumerate():
                        if tobj.ident or tobj==thread_id:
                            self._thread = tobj
                            break                            

    def __call__(self):
        """Start the thread if it isn't alive and return the thread ID, if it exist returns None instead.
   
        """
        if not self._thread.isAlive():
            self._thread.start()
            return self._thread.ident

    @property
    def keycode(self):
        """If the thread is alive return a queue of pressed keys as tuples (unicode char, event type code, event type string). This is a property method.

The main thread programm can countinue the execution of its code and if the key buffer queue is empty returns None.

        """

        try:   
            return self.keybuffer.get(False)     
        except KeyThread.Queue.Empty:
            pass

    @staticmethod
    def _thread_event(this):
        """Core event that overwrites the *KeyEvent.set_event* method. Implemented as Static method.

This method overwrites the KeyEvent.set_event method as key press detection event.
Do not overwrite it unless you know what you're doing. 

        """

        this.keybuffer.put(this.keycode)
            
        if this.quitevent.is_set():
            this.quitevent.clear()
            this.set_exit(True)
 
    @staticmethod
    def _runcode(keyinstance):
        """The core of the key thread acquisition code. Implemented as Static method.
Overwrites the threading run() method with the key press detection event.

Do not overwrite it unless you know what you're doing. 
        
        """  

        keyinstance()

    def _check_buffer(self,max=0):
        """Check the buffer length which serves for transfer characters from the asynchronous thread to the main thread. 

    Parameters:
        *max* - The maximum characters buffer. Default value = 1 (character).
        
        """
        if type(max)!=int:
            raise TypeError("max_buffer parameter value must be an integer")
        if max <0 :
            raise ValueError("max_buffer parameter value must be greather than or equal to 0")
        return max

    def stop(self, force=0, retry=3, wait=1):
        """Abort thread instance. *force* parameter set the strenght of abort state (default=0).
        Parameters:
            force = 0 - recomended: only verify if the thread is alive and set a stop event in the thread (the thread will close softly).
            force = 1 - not recomended: verify if the thread is alive and if the thread do not join in a few millisecond, the function send to it and exception that force the abort state (if the thread respond will close softly otherwise, it will close in the middle of its execution).
            force = 2 - strongly not recomended: verify if the thread is alive and stop it by sending an exception that force the abort state (it will close in the middle of its execution).
            retry - how many times try to stop the thread and wait it's join.
            wait - waiting time every retry loop in a join state.

        """

        if force<0 or force>2:
            raise ValueError("*force* param in KeyThread.stop() must be between 0 and 2")
        if retry<0:
            raise ValueError("*retry* parameter in KeyThread.stop() must be greather than 0")
        if wait<0:
            raise ValueError("*wait_time* parameter in KeyThread.stop() must be greather than 0")

        res=0
        
        if self._thread.isAlive() == True and force == 0 and force == 1:
            #softly thread stop
            for i in xrange(retry): 
                self.quitevent.set() #set the thread stop variable on true.
                self._thread.join(wait)
                if not self._thread.isAlive(): 
                    break

        if self._thread.isAlive() == True and force == 1 and force == 2:
            #force thread stop
            for i in xrange(retry):
                exc = ctypes.py_object(SystemExit)
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)
                if res<1:
                    raise ValueError("Invalid keyThread id")
                else: #elif res >1:  1 is the tID of the main thread.
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
                    #raise SystemError("KeyThread force stop failed") useless?
                self._thread.join(wait)
                if not self._thread.isAlive(): 
                    break
                
        return self._thread.isAlive()

    def _test(self):
        """Try if the class implementation work well. Print on screen the pressed character and character code. 
Use this as example for understand how the class work.

        """

        print 'Press a key' 
        self.__call__()
        while 1:
            keycode=self.keycode
            if keycode is not None:
                key,state,word = keycode
                print 'you pressed key:',unichr(key),'  with state:',state,'/',word,'  ASCII code:',key 