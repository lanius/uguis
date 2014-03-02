Uguis
=====

An RSS reader for me.


Concepts
--------

- The view is rough and easy to watch a large number of entries
- Entries of all feeds are integrated into a single timeline
- The timeline can be read from both head and tail
- It is managed which entry has already been read
- It is recorded whether an entry is preferred or not for future analysis


Prerequisites
-------------

- Python >= 2.7, pip
- Node.js >= 0.10.26, npm, gulp, bower


Install
-------

Installed libraries and resolves dependencies:

.. code-block:: bash

    $ pip install -r requirements.txt
    $ npm install
    $ bower install

If necessary, use virtualenv.


Build
-----

Builds client-side codes:

.. code-block:: bash

    $ gulp

Or:

.. code-block:: bash

    $ gulp --debug


Run
---

Run the crawler:

.. code-block:: bash

    $ python crawler.py

Run the Web app:

.. code-block:: bash

    $ python webapp.py
