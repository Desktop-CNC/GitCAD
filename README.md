# GitCAD 
GitCAD is a tool that will manage GitHub CAD repositories on a local machine and allow a user to import one CAD repository into another. This allows CAD assemblies to be developed on independent repositories while keeping assemblies connected across repositories.  

## Overview 
_GitCAD_ is an application that makes uploading (pushing) changes and downloading (pulling) changes from a repository easier. There are tools that do this already, such as _GitHub Desktop_. However, **_GitCAD_** allows for **declaring repositories has dependencies of another.** 

_GitCAD_ allows you to create separate CAD assemblies in different repositories to keep them independent. This is useful for keeping CAD documentation modular. Dependencies essentially serve as CAD sub-assemblies that are stored independently. 

## Benefits
Any CAD project or assembly can be made of many other assemblies; typically known as sub-assemblies. Should these all exist in one single repository, only one developer can make changes to that repository at a time. Otherwise, many developers will overwrite each other's work, or merge conflicts between changes made by different developers will arise. Merge conflicts can be handled for debugging software, but debugging raw CAD files is not practical. 

For these reasons, merge conflicts should be avoided entirely and so should having more than one developer working on a CAD repository at a time.

A **dependency** is a repository that is needed for another parent repository. This allows on one repository to depend and and import another. When resolving conflicting changes and merge conflicts should be avoided, the work across a larger project can be split across many repositories that have dependencies to others. 

## Available Distributions:
_GitCAD_ has been developed for both Linux and Windows systems. These can be found here: (can also be found in folder `/executables`)
- <a href="./executables/GitCAD_Linux"><strong>GitCAD_Linux</strong></a>
- <a href="./executables/GitCAD_Win64.exe"><strong>GitCAD_Win64.exe</strong></a>

## How It Works:
The app is a menu that is navigated with UP/DOWN arrow keys and by selecting ENTER. 