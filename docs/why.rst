.. _why:

🤔Why pytest-remote-response?
==============================

Nowadays, many of our tests fetch some data or are in some way connected to an online service.

But, what if the service is down? or modified its response? 

💔? It's a lot more challenging to ascertain the fault in such cases.

This package attempts to mock some external requests to make the tests more self-contained and reduce the requests to the outside world!

Perhaps solve some HTTP 429's too. 🧐

.. note::

    Due to some limitations, it is not advisible to run the tests in completely offline-environments.
    
    Get in touch if interested in testing such cases! 📝