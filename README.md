# ThreadBare

** Jake Mingolla **

** June 2016 **

** Category: Concurrency **

** Language(s): Python **

### About

Have you ever wanted to compose every image on a Wikipedia page together
in a concurrent way? Now you can! Given a few inputs such as the desired
height and width of the canvas, the desired Wikipedia page, and the
number of threads to use, this script programmatically assigns each
image to a thread and combines them concurrently.

Locks are used to eliminate race conditions between threads -- no two
threads can access the same exact pixel as another. The locks make
accessing and manipulating a pixel within the base image an atomic
action in relation to the other threads accessing the same image.
Once a thread has completed modifying a given pixel, the next thread
that is blocking can access it. A thread pool manages all threads
as the list of all images is mapped over.

### Example
![](https://raw.githubusercontent.com/jakemingolla/ThreadBare/master/meld.gif)

The above GIF is composed of the following images for the Wikipedia entries
for Lamborghini, America, Crimean War, and Tom Brady shown below:

![](https://raw.githubusercontent.com/jakemingolla/ThreadBare/master/2.png)

![](https://raw.githubusercontent.com/jakemingolla/ThreadBare/master/3.png)

![](https://raw.githubusercontent.com/jakemingolla/ThreadBare/master/1.png)

![](https://raw.githubusercontent.com/jakemingolla/ThreadBare/master/4.png)


### To Dos
- Add options on whether or not to scale all images to fit the desired
height and width. As of right now, the default is to shrink/expand all
images so that they fit in the desired canvas size regardless of original
aspect ratio.
