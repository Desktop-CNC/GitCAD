# GitCAD 
GitCAD is a tool that will manage GitHub CAD repositories on a local machine and allow a user to import one CAD repository into another. This allows CAD assemblies to be developed on independent repositories while keeping assemblies connected across repositories.  

## Overview 
_GitCAD_ is an application that makes uploading (pushing) changes and downloading (pulling) changes from a repository easier. There are tools that do this already, such as _GitHub Desktop_. However, **_GitCAD_** allows for **declaring repositories has dependencies of another.** 

_GitCAD_ allows you to create separate CAD assemblies in different repositories to keep them independent. This is useful for keeping CAD documentation modular. Dependencies essentially serve as CAD sub-assemblies that are stored independently. 

## Benefits
Any CAD project or assembly can be made of many other assemblies; typically known as sub-assemblies. Should these all exist in one single repository, only one developer can make changes to that repository at a time. Otherwise, many developers will overwrite each other's work, or merge conflicts between changes made by different developers will arise. Merge conflicts can be handled for debugging software, but debugging raw CAD files is not practical. 

For these reasons, merge conflicts should be avoided entirely and so should having more than one developer working on a CAD repository at a time.

A **dependency** is a repository that is needed for another parent repository. An example of this is a **Enclosure assembly** CAD repository that has the **Standard Parts** repository as a dependency. A copy of _Standard Parts_ will exist within a `/deps` folder of _Enclosure assembly_. If changes are made to the _Standard Parts_ repository, it will not affect _Enclosure assembly_. If it is decided to update the dependencies under _Enclosure assembly_, then the copy of _Standard Parts_ under _Enclosure assembly_ will be updated. 

Putting _GitCAD_ in practice, _Enclosure assembly_ and _Standard Parts_ can be separate repositories that different developers can work on at the same time. Since they exist on separate repositories, merge conflicts are avoided entirely. If one parent repository depends on another, the parent can try to update its dependencies if there are new versions available. 

## Available Distributions:
TO DO

## How It Works:
### Cloning a CAD Repository
Write this up
### Pulling a CAD Repository
Write this up
### Pushing a CAD Repository
Write this up
### Adding / Removing a Dependency
Write this up
### Updating Local Dependencies
Write this up