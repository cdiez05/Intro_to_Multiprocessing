# Introduction to Multiprocessing Library 

## Part 1
Implementing a concurrent merge:

We have NPROD processes that produce non-negative numbers in increasing order. When a process finishes producing, it produces a -1.

There is a merge process that must take the numbers and store them in increasing order in a single list (or array). The process must wait for the producers to have an element ready and insert the smallest of them.

Semaphore lists must be created. Each producer only handles its semaphores for its data. The merge process must handle all the semaphores.

OPTIONALLY: a fixed-size buffer can be implemented so that producers put values in the buffer.

## Part 2
Implementing a concurrent merge:

We have NPROD processes that produce non-negative numbers in ascending order. When a process finishes producing, it generates a -1.

There is a merge process that must take the numbers and store them in ascending order in a single list (or array). The process must wait for the producers to have an element ready and insert the smallest of them.

Semaphore lists must be created. Each producer only manages its semaphores for its data. The merge process must handle all the semaphores.

OPTIONALLY: a fixed-size buffer can be implemented so that producers put values in the buffer.
