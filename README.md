NoFS, a networked filesystem
============================

NoFS aims to provide a distributed network filesystem for small cluster use.

We are trying to combine all your machines (laptop, desktop, etc.) into a single logical storage unit. Each machine contributes storage to the pool and can access all the files in the pool (pending permissions). Remote files can be cached locally and all file access happens as if performed on a local drive.

NoFS also aims to provide performce better than the network speed by intelligently caching and predicting file accesses.
