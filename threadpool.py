# Jake Mingolla
# June,  2016
#
# Creates composite images for a given wikipedia page. Used to demonstrate ability
# of multithreading concepts as well as image manipulation.

# Used for handling threading.
import threading
# Used for image handling master class.
from PIL import Image
# Used for getting wikipedia links directly through the Python api.
import wikipedia
# Used for making raw HTTP connections for image downloading.
import urllib
# Used for interpreting image data into the Image class.
from cStringIO import StringIO
# Used for handling pools of threads.
from multiprocessing.pool import ThreadPool

# Direct linear combination of two pixel (r, g, b) tuples. Blends 
# with 50% interpolation.
def blend(p1, p2):
    r1, g1, b1 = p1
    r2, g2, b2 = p2
    return ((r1 + r2) / 2, (g1 + g2) / 2, (b1 + b2) / 2)

# Paints an image from a given url into the base image. The locks keep track
# of pixel values so that there are no race conditions between different threads
# accessing pixels.
def paint((base, locks, url, w, h)):
    # First, attempt  to open the image and convert it to a usable filetype.
    try:
        f = StringIO(urllib.urlopen(url).read())
        img = Image.open(f)
        img = img.convert('RGB')
    # If the image cannot be opened or converted, release the semaphore and return.
    except IOError:
        return

    # The col- and rowFactor variables store the ratio of the new image
    # to the base image's width and height in order for each image to be stretched
    # to fit into the base image.
    imgW, imgH = img.size
    colFactor = imgW / float(w)
    rowFactor = imgH / float(h)

    # For each pixel in the new image...
    for col in range(w):
        for row in range(h):
            # First get the pixels of the new image after adjustment...
            adjusted_col = col * colFactor
            adjusted_row = row * rowFactor
            
            # ...then get the corresponding pixel in the base image.
            new_pixel = img.getpixel((adjusted_col, adjusted_row))

            # Note that the locks make the entire image below atomic in relation
            # to other threads. No two threads can access the same image at the
            # same time.
            locks[col][row].acquire()
            old_pixel = base.getpixel((col, row))
            # Create a new pixel blend.
            blend_pixel = blend(new_pixel, old_pixel)
            # Add the new blended pixel into the blend image.
            base.putpixel((col, row), blend_pixel)
            # Release the lock so other threads that may be blocking can continue
            locks[col][row].release()
 

# Generator to iterate over all urls to pass to the paint function
def gen(base, locks, urls, w, h):
    for url in urls:
        yield (base, locks, url, w, h)
    

def main():
    '''
    Handles user input, wikipedia link generation, and instantiation and runtime of threads.
    '''

    # Note that no validation is done at any level of the user input.
    w           =     input("Enter width of the canvas (i.e. 512)                  : ")
    h           =     input("Enter height of the canvas (i.e. 512)                 : ")
    num_threads =     input("Enter number of threads (i.e. 16)                     : ")
    title       = raw_input("Enter title of wikipedia page (i.e New York)          : ")
    destination = raw_input("Enter name of destination file (i.e. masterpiece.png) : ")


    # Get the wikipedia page for the current title and limit the images if specified.
    page = wikipedia.page(title)
    image_urls = page.images

    # Initialize the starting image and lock array.
    base = Image.new('RGB', (w, h), 'white')
    locks = [[threading.Lock() for x in range(h)] for y in range(w)]

    # Create a thread pool with the given number of threads and map the paint() function
    # across the pool.
    pool = ThreadPool(num_threads)
    pool.map(paint, gen(base, locks, image_urls, w, h))

    # Finally, save the image under the specified name.
    base.save(destination)

if __name__ == "__main__":
    main()
