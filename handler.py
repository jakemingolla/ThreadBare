from PIL import Image
from random import randint
import wikipedia
import threading
import urllib
from cStringIO import StringIO
from time import sleep

# Sentinel value for recording the very first instance of pixel
# blending, in which case we overwrite the pixel instead of blending
SENTINEL = -1

def paint(semaphore, pixels, locks, url, w, h):
    '''
    Blends the image specified by url onto the pixel map. Uses a semaphore
    to unlock upon completion of the thread's procedure. Will map whatever
    the image's width and height are into the w and h specified in the function
    call.
    '''

    # First, attempt  to open the image and convert it to a usable filetype.
    try:
        f = StringIO(urllib.urlopen(url).read())
        img = Image.open(f)
        img = img.convert('RGB')
    # If the image cannot be opened or converted, release the semaphore and return.
    except IOError:
        semaphore.release()
        return
    
    # Calculate the pixel offsets for the columns and rows so that the new image will
    # fit in the bounds of the existing image.
    imgW, imgH = img.size
    #if imgW > h:
    #    colOffset = h / float(imgW)
    #else:
    #    colOffset = imgW / float(h)


    #if imgH > w:
    #    rowOffset = w / float(imgH)
    #else:
    #    rowOffset = imgH / float(w)

    # Load the new image's pixel map
    pixMap = img.load()

    # Iterate through each pixel of the new pixel map, and ignore it if it is outside
    # of the rnage.
    for col in range(w):
        for row in range(h):
            
            # Get the new pixel from the pixel map
            #(newR, newG, newB) = pixMap[int(col * colOffset), int(row * rowOffset)]
            #(newR, newG, newB) = pixMap[int(row * rowOffset), int(col * colOffset)]
            if col >= imgW or row >= imgH:
                continue
            (newR, newG, newB) = pixMap[col, row]

            #try:
            #    (newR, newG, newB) = pixMap[int(col * colOffset), int(row * rowOffset)]
            #except IndexError:
            #    print 'w = ' + str(w)
            #    print 'h = ' + str(w)
            #    print 'imgW = ' + str(imgW)
            #    print 'imgH = ' + str(imgH)
            #    print 'row offset = ' + str(rowOffset)
            #    print 'col offset = ' + str(colOffset)
            #    print str(int(col * colOffset)) + ' / ' + str(imgW)
            #    print str(int(row * rowOffset)) + ' / ' + str(imgH)
            #    exit(1)
                
            # Make sure no one else is trying to paint this pixel by acquiring the lock.
            locks[col][row].acquire()
            # Get the existing pixel from the existing pixel map
            (existingR, existingG, existingB) = pixels[col][row]

            # If we don't need to blend, simply copy in the new RGB values.
            if (existingR == SENTINEL):
                pixels[col][row] = (newR, newG, newB)

            # Otherwise, take an average blending between the new and existing RGB values.
            else:
                blend = ((newR + existingR) / 2, (newG + existingG) / 2, (newB + existingB) / 2)
                pixels[col][row] = blend

            # Finally, unlock the lock associated with this pixel so other threads can use it.
            locks[col][row].release()

    # Decrement the semaphore count to signal to the thread pool to unblock if necessary
    # sicne we have finished with this thread
    semaphore.release()

def main():
    '''
    Handles user input, wikipedia link generation, and instantiation and runtime of threads.
    '''

    # Note that no validation is done at any level of the user input.
    w           =     input("Enter width of the canvas (i.e. 512)                  : ")
    h           =     input("Enter height of the canvas (i.e. 512)                 : ")
    num_threads =     input("Enter number of threads (i.e. 16)                     : ")
    title       = raw_input("Enter title of wikipedia page (i.e New York)          : ")
    img_name    = raw_input("Enter name of destination file (i.e. masterpiece.png) : ")

    # Load the image links from wikipedia API.
    page = wikipedia.page(title)
    image_urls = page.images

    # Create a 2D array of pixels and locks. Each lock is used to make sure only one thread
    # paints a given pixel at a time.
    locks = [[threading.Lock() for c in range(w)] for r in range(h)]
    pixels = [[(SENTINEL, SENTINEL, SENTINEL) for c in range(w)] for r in range(h)]

    # Create a thread pool and a list of threads, both active and completed.
    threads = []
    semaphore = threading.BoundedSemaphore(num_threads)

    # For each of the images, attempt to acquire the semaphore and block if necessary.
    # Then, instantiate a new thread and add it to the list of thread objects.
    for i in range(len(image_urls)):
        semaphore.acquire()
        thread = threading.Thread(target = paint, \
                       args = [semaphore, pixels, locks, image_urls[i], w, h])
        thread.start()
        threads.append(thread)

    # Finally, once all threads have been started, block until all threads have completed.
    for thread in threads:
        thread.join()

    # Put the pixels into the images and save it.
    img = Image.new("RGB", (w, h))
    img.putdata([x for col in pixels for x in col])
    img = img.rotate(270)
    img.save(img_name)
    
# Run it.
if __name__ == "__main__":
    main()
