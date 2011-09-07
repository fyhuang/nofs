NoFS, a networked filesystem
============================

NoFS aims to provide a distributed network filesystem for small cluster use.

NoFS combines all your machines (laptop, desktop, etc.) into a single storage unit. No longer should you have to think about your files as being on a particular computer: now all your files are simply "your files", accessible from anywhere. Each machine contributes storage to the pool and can access all the files in the pool (pending permissions). Remote files can be cached locally and all file access happens as if performed on a local drive.

NoFS aims to provide this functionality while maintaining reasonable performance on high-bandwidth networks. In the course of everyday work, the user should not notice a difference when using NoFS from using a hard drive. NoFS is not intended for general use on medium-/high-latency links, but will provide a "client profile" to access your files from anywhere on the Internet.

Design and inspirations
=======================

This section hopes to shed some light on the inspirations behind the design and conception of NoFS. It also catalogues a list of potential features which aim to solve the problems that NoFS addresses.

Distributed filesystem
----------------------

Why do we bother with a distributed filesystem? There are two problems in particular that we address:

* Users have multiple computers. Their files are spread out across these computers, but there isn't an easy way to gain access to all their files from a single computer. USB drives, network shares, and current sync software are all too cumbersome for this task.
* Backing up files is generally considered to be important, but the incentive structure for backups is completely backwards. It takes a ton of time, effort, disk space, and sometimes even money to back up your files; however, there is no immediately visible benefit. In fact, backing up is detrimental in the short term, wasting time, energy, and disk space.

We aim to solve the first problem -- collating all a user's files into one logical storage unit -- while providing automatic, seamless, and effortless backup as a side effect.

Semantic filesystem
-------------------

A secondary goal of NoFS is to provide a more interconnected and semantic way of looking at your files. We were inspired by Gmail's labels and thought that this same concept could be applied to file organization as well. No file in NoFS has a "definitive" location in the filesystem: rather, each file can be filed into numerous locations simply by adding or removing labels. NoFS automatically finds semantic connections (based on content and metadata) between files to help automate your organizational methodology.
